"""
Custom template filters for BMAD Forge.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a dynamic key.
    
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    
    # Handle both dict and dict-like objects
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        try:
            return dictionary[key]
        except (KeyError, IndexError, TypeError):
            return None
