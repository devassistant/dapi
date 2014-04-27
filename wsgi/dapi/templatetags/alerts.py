from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()

t = {
    '': 'info',
    'error': 'danger',
    'debug': 'danger',
}


@register.filter(is_safe=True)
@stringfilter
def alerts(value):
    '''Template filter that converts Django messages tags to Bootstrap alert classes'''
    try:
        return t[value]
    except KeyError:
        return value
