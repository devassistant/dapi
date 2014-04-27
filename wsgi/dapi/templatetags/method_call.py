'''This was written by Shah Pavel Jamal
See http://www.sprklab.com/notes/13-passing-arguments-to-functions-in-django-template
Used with permission'''
from django import template

register = template.Library()


@register.filter(name='call')
def call_method(obj, method_name):
    method = getattr(obj, method_name)
    if "__call_arg" in obj.__dict__:
        ret = method(*obj.__call_arg)
        del obj.__call_arg
        return ret
    return method()


@register.filter
def args(obj, arg):
    if "__call_arg" not in obj.__dict__:
        obj.__call_arg = []

    obj.__call_arg += [arg]
    return obj
