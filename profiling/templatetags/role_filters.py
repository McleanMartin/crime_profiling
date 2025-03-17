from django import template

register = template.Library()

@register.filter(name='has_role')
def has_role(user, allowed_roles):
    """
    Custom template filter to check if the user has one of the allowed roles.
    """
    if user.is_authenticated and hasattr(user, 'role'):
        return user.role in allowed_roles
    else:
        return False