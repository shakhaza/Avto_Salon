from django import template

register = template.Library()

@register.filter(name='price_format')
def price_format(value):
    try:
        value = int(value)
        return "${:,.0f}".format(value)
    except (ValueError, TypeError):
        return value
