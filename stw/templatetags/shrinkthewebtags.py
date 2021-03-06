"""
Django template tags for inserting Shrink The Web images into templates.

There are two templatetags:
 - shrinkthewebimage - the original image insertion templatetag w/o PRO features
 - stwimage - the newest image insertion templatetag that supports simple and PRO features
"""
import urllib
from django.utils.safestring import mark_safe
from django.conf import settings
from django import template

class STWConfigError(template.TemplateSyntaxError):
    pass

class FormatSTWImageNode(template.Node):

    def __init__(self, url, alt, **kwargs):
        params = {}
        # load defaults if any
        params.update(settings.SHRINK_THE_WEB)
        # overwrite defaults for this tag instance
        params.update(kwargs)
        self.kwargs = params
        self.url = url
        self.alt = alt

    @classmethod
    def _buildUrlParams(cls, kwargs):
        """Return a dict of the supplied and required url keywords and values"""
        if 'stwembed' not in kwargs:
            kwargs['stwembed'] = 1 # default to image
        if 'stwaccesskeyid' not in kwargs:
            raise STWConfigError("'stwaccesskeyid' must be defined in settings.SHRINK_THE_WEB")
        # validate conflicting options
        if 'stwsize' in kwargs:
            if 'stwxmax' in kwargs or 'stwymax' in kwargs or 'stwfull' in kwargs:
                raise template.TemplateSyntaxError("'stwimage' tag does not allow 'stwsize' and ('stwfull' or ('stwxmax' and/or 'stwymax')) keyword(s)")
        elif 'stwxmax' not in kwargs and 'stwymax' not in kwargs and 'stwfull' not in kwargs:
            raise template.TemplateSyntaxError("'stwimage' tag requires 'stwsize' or ('stwfull' or ('stwxmax' and/or 'stwymax')) keyword(s)")
        return kwargs

    @classmethod
    def _resolve(cls, var, context):
        """if var is a string then return it otherwise use it to lookup a value in the current context"""
        if var[0] == var[-1] and var[0] in ('"', "'"):
            var = var[1:-1] # a string
        else:
            var = template.Variable(var).resolve(context)
        return var

    def render(self, context):
        url = self._resolve(self.url, context)
        alt = self._resolve(self.alt, context)
        encoded = urllib.urlencode(self._buildUrlParams(self.kwargs))
        if encoded:
            encoded += '&'
        result =  '''<img src="http://images.shrinktheweb.com/xino.php?%sstwurl=%s" alt="%s"/>''' % (encoded, url, alt)

        return result


def do_shrinkthewebimage(parser, token):
    """
    Original templatetag using only basic STW features

    Usage::

        {% load shrinkthewebtags %}

        {% shrinkthewebimage url size alt %}

    Where:

        ``url``
          is expected to be a variable instantiated from the context
          or a quoted string to be used explicitly.

        ``size``
          is expected to a valid size string accepted by shrinktheweb.com
          which currently accepts one of: "mcr", "tny", "vsm", "sm", "lg"
          or "xlg". A context variable can also be used.

        ``alt``
          is alt text for the img tag and is either a quoted string or
          a variable instantiated from the context.

    Examples::

        Given a template context variable "author" with attributes "url" and
        "description" the following are valid entries in a template file:

        {% shrinkthewebimage author.url "sm" '' %}

        {% shrinkthewebimage author.url "lg" author.url %}

        {% shrinkthewebimage author.url "xlg" author.description %}

    """
    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly 3 arguments" % bits[0])
    size = bits[2]
    if size[0] == size[-1] and size[0] in ('"', "'"):
        size = size[1:-1] # a string

    kwargs = {'stwsize' : size,
              }
    return FormatSTWImageNode(url=bits[1], alt=bits[3], **kwargs)


def do_stwimage(parser, token):
    """
    Key value based templatetag supporting all STW features

    Usage::

        {% load shrinkthewebtags %}

        {% stwimage url alt key-value-pairs %}

    Where:

        ``url``
          is expected to be a variable instantiated from the context
          or a quoted string to be used explicitly.

        ``key-value-pairs``
          matching STW API values i.e. stwembed=0 stwinside=1
          minimal validation of key value pairs is performed

    Examples::

        Given a template context variable "author" with attributes "url" and
        "description" the following are valid entries in a template file:

        {% load shrinkthewebtags %}

        get image of the follow the full url (not just the top level page), wait
        5 seconds, and return image in large size (this requires license with PRO
        features:

        {% stwimage author.url author.description stwinside=1 stwdelay=5 stwsize=lrg %}
    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError("'%s' tag takes at least 2 arguments" % bits[0])

    # process keyword args
    kwargs = {}
    for bit in bits[3:]:
        key, value = bit.split("=")
        if value is '':
            raise template.TemplateSyntaxError("'%s' tag keyword: %s has no argument" % (bits[0], key))

        if key.startswith('stw'):
            kwargs[str(key)] = value
        else:
            raise template.TemplateSyntaxError("'%s' tag keyword: %s is not a value STW keyword" % (bits[0], key))
    return FormatSTWImageNode(url=bits[1], alt=bits[2] , **kwargs)


register = template.Library()
register.tag('shrinkthewebimage', do_shrinkthewebimage)
register.tag('stwimage', do_stwimage)
