from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings


register = template.Library()

@register.filter(name='register',is_safe=True)
@stringfilter
def register_link(value):
    '''Add registration link for given backedn'''
    try:
        return getattr(settings, 'SOCIAL_AUTH_{provider}_REGISTER_LINK'.format(provider=value.upper()))
    except AttributeError:
        return None
