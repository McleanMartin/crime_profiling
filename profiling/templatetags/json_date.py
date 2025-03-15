from django import template
from datetime import datetime

register = template.Library()

@register.filter
def json_date(value, format="M d, Y"):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime(format)
    except (TypeError, ValueError):
        return value

@register.filter
def is_dict(value):
    return isinstance(value, dict)