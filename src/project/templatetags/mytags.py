from django import template

register = template.Library()


@register.filter
def joinby(value, arg):
    return arg.join(value)