from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from dapi import models

register = template.Library()


@register.filter(needs_autoescape=True)
@stringfilter
def deplink(value, autoescape=None):
    '''Add links for required daps'''
    usedmark = ''
    for mark in '= < >'.split():
        split = value.split(mark)
        if len(split) > 1:
            usedmark = mark
            break
    if usedmark:
        dap = split[0]
    else:
        dap = value
    try:
        m = models.MetaDap.objects.get(package_name=dap)
        link = '<a href="' + m.get_human_link() + '">' + dap + '</a>'
    except models.MetaDap.DoesNotExist:
        link = '<abbr title="This dap is not on Dapi">' + dap + '</abbr>'
    if usedmark:
        link = link + usedmark + usedmark.join(split[1:])
    return mark_safe(link)
