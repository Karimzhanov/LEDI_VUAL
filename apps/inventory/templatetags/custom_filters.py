# apps/inventory/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def format_decimal(value):
    try:
        return f"{value:.2f}".replace('.', ',')
    except (ValueError, TypeError):
        return value
