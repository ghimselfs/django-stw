"""Tests for custom templatetags"""
import unittest
from mock import Mock, patch
from django.conf import settings
from django import template
from stw.templatetags.shrinkthewebtags import FormatSTWImageNode, do_shrinkthewebimage, do_stwimage, STWConfigError


class TestSTWImageNode(unittest.TestCase):

    def setUp(self):
        self.settings = settings.SHRINK_THE_WEB
        settings.SHRINK_THE_WEB = {'stwaccesskeyid' : 'key'}

    def tearDown(self):
        settings.SHRINK_THE_WEB = self.settings

    def test_init(self):
        node = FormatSTWImageNode("url", "alt")
        self.assertEqual("url", "%s" % node.url)
        self.assertEqual("alt", node.alt)
        # get value from settings.SHRINK_THE_WEB
        self.assertEqual('key', node.kwargs['stwaccesskeyid'])

    def test_init_override_key(self):
        node = FormatSTWImageNode("url", "alt", stwaccesskeyid='overridekey')
        self.assertEqual("url", "%s" % node.url)
        self.assertEqual("alt", node.alt)
        self.assertEqual('overridekey', node.kwargs['stwaccesskeyid'])

    def test_init_add_from_settings_and_override_key(self):
        settings.SHRINK_THE_WEB = {'stwaccesskeyid' : 'key', 'stwanewkey': 'newkey'}
        node = FormatSTWImageNode("url", "alt", stwaccesskeyid='overridekey')
        self.assertEqual("url", "%s" % node.url)
        self.assertEqual("alt", node.alt)
        self.assertEqual('overridekey', node.kwargs['stwaccesskeyid'])
        self.assertEqual('newkey', node.kwargs['stwanewkey'])


    # valid combinations of size, xmax, ymax
    def test_buildUrlKeyValues_no_stwembed(self):
        self.assertEqual({'stwaccesskeyid':'key', 'stwembed': 1, 'stwsize':'lrg'},
                         FormatSTWImageNode._buildUrlParams({'stwaccesskeyid':'key', 'stwsize':'lrg'}))

    def test_buildUrlKeyValues_stwembed(self):
        self.assertEqual({'stwaccesskeyid':'key', 'stwembed': 0, 'stwsize':'lrg'},
                         FormatSTWImageNode._buildUrlParams({'stwaccesskeyid':'key', 'stwembed':0, 'stwsize':'lrg'}))

    def test_buildUrlKeyValues_stwembed_stwxmax(self):
        self.assertEqual({'stwaccesskeyid':'key', 'stwembed': 0, 'stwxmax':100},
                         FormatSTWImageNode._buildUrlParams({'stwaccesskeyid':'key', 'stwembed':0, 'stwxmax':100}))

    def test_buildUrlKeyValues_stwembed_stwymax(self):
        self.assertEqual({'stwaccesskeyid':'key', 'stwembed': 0, 'stwymax':100},
                         FormatSTWImageNode._buildUrlParams({'stwaccesskeyid':'key', 'stwembed':0, 'stwymax':100}))

    def test_buildUrlKeyValues_stwembed_stwxmax_stwymax(self):
        self.assertEqual({'stwaccesskeyid':'key', 'stwembed': 0, 'stwxmax': 100, 'stwymax':200},
                         FormatSTWImageNode._buildUrlParams({'stwaccesskeyid':'key', 'stwembed':0, 'stwymax':200, 'stwxmax':100}))

    def test_buildUrlKeyValues_stwembed_stwxfull(self):
        self.assertEqual({'stwaccesskeyid':'key', 'stwembed': 0, 'stwfull': 1},
                         FormatSTWImageNode._buildUrlParams({'stwaccesskeyid':'key', 'stwembed':0, 'stwfull':1}))

    # missing required configuration
    def test_buildUrlKeyValues_no_stwaccesskeyid(self):
        self.assertRaises(STWConfigError, FormatSTWImageNode._buildUrlParams, {})

    # invalid combinations of stwsize, stwxmax, stwymax and stwfull
    def test_buildUrlKeyValues_no_stwsize_no_stwxmax_no_stwymax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode._buildUrlParams,
                          {'stwaccesskeyid':'key'})

    def test_buildUrlKeyValues_stwsize_stwfull(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode._buildUrlParams,
                          {'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwfull':1})

    def test_buildUrlKeyValues_stwsize_stwxmax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode._buildUrlParams,
                          {'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwxmax':100})

    def test_buildUrlKeyValues_stwsize_stwymax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode._buildUrlParams,
                          {'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwymax':100})

    def test_buildUrlKeyValues_stwsize_stwxmax_stwymax(self):
        self.assertRaises(template.TemplateSyntaxError, FormatSTWImageNode._buildUrlParams,
                          {'stwaccesskeyid':'key', 'stwsize':'lrg', 'stwymax':100, 'stwymax':100})

    def test_render_strings_url_alt(self):
        # ignore kwarg URL params
        node = FormatSTWImageNode("'url'", "'alt'")
        node._resolve = Mock()
        results = ["alt", "url"]
        def side_effect(*args, **kwargs):
            return results.pop()
        node._resolve.side_effect = side_effect

        node._buildUrlParams = Mock(return_value={})
        self.assertEqual('''<img src="http://images.shrinktheweb.com/xino.php?stwurl=url" alt="alt"/>''', node.render(None))

    def test_render_context(self):
        node = FormatSTWImageNode("url", "alt")
        node._resolve = Mock()
        results = ["alt", "url"]
        def side_effect(*args, **kwargs):
            return results.pop()
        node._resolve.side_effect = side_effect

        context = {'alt': 'alt'}
        node._buildUrlParams = Mock(return_value={})
        self.assertEqual('''<img src="http://images.shrinktheweb.com/xino.php?stwurl=url" alt="alt"/>''', node.render(context))

    @patch('urllib.urlencode')
    def test_render_strings_url_alt_kwargs(self, mockurlencode):
        node = FormatSTWImageNode("'url'", "'alt'")
        node._resolve = Mock()
        results = ["alt", "url"]
        def side_effect(*args, **kwargs):
            return results.pop()
        node._resolve.side_effect = side_effect
        node._buildUrlParams = Mock(return_value={})
        mockurlencode.return_value = "kwarg=kwargvalue"
        self.assertEqual('''<img src="http://images.shrinktheweb.com/xino.php?kwarg=kwargvalue&stwurl=url" alt="alt"/>''', node.render(None))


class TestDoShrinkTheWebImage(unittest.TestCase):

    def test_no_args(self):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=('tagname',))
        self.assertRaises(template.TemplateSyntaxError, do_shrinkthewebimage, parser, token)

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWImageNode')
    def test_correct_args(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("tagname", "url", "lrg", "alt"))
        do_shrinkthewebimage(parser, token)
        MockClass.assert_called_with(url="url", stwsize="lrg", alt="alt")


class TestDoSTWImage(unittest.TestCase):

    def test_no_args(self):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=('tagname',))
        self.assertRaises(template.TemplateSyntaxError, do_stwimage, parser, token)

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWImageNode')
    def test_no_kwargs(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt"))
        do_stwimage(parser, token)
        MockClass.assert_called_with(url="url", alt="alt")

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWImageNode')
    def test_stw_kwarg(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt", "stwsize=lrg"))
        do_stwimage(parser, token)
        MockClass.assert_called_with(url="url", alt="alt", stwsize="lrg")

    @patch('stw.templatetags.shrinkthewebtags.FormatSTWImageNode')
    def test_stw_kwargs(self, MockClass):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt", "stwsize=lrg", "stwembed=1"))
        do_stwimage(parser, token)
        MockClass.assert_called_with(url="url", alt="alt", stwsize="lrg", stwembed='1')

    def test_nonstw_kwarg(self):
        parser = Mock()
        token = Mock()
        token.split_contents = Mock(return_value=("stwimage", "url", "alt", "size=lrg"))
        self.assertRaises(template.TemplateSyntaxError, do_stwimage, parser, token)
