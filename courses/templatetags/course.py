from django import template

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
