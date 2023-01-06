from django import template

register = template.Library()


@register.filter
def ethiopian_date(value):
    if isinstance(value, str):
        return value
    return value.strftime("%Y-%m-%d")
