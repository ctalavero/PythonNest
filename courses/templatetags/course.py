from django import template
from datetime import timedelta
register = template.Library()

@register.filter
def model_name(obj):
    """
    This is a custom template filter in Django. It takes an object as an argument and returns the model name of the object.

    Args:
        obj (django.db.models.Model): The Django model instance.

    Returns:
        str: The model name of the object if it exists, otherwise None.
    """
    try:
        return obj._meta.model_name
    except:
        return None

@register.filter
def format_duration(value):
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f'{hours}h {minutes}m {seconds}s'
        elif minutes > 0:
            return f'{minutes}m {seconds}s'
        else:
            return f'{seconds}s'
    return value