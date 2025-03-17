from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def role_required(allowed_roles, redirect_url='crime_list', error_message="Access Denied. You don't have permission to perform that action."):
    """
    Custom decorator to restrict access based on user role.
    
    :param allowed_roles: List of roles allowed to access the view.
    :param redirect_url: URL to redirect to if access is denied.
    :param error_message: Custom error message to display.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, error_message)
                return redirect(redirect_url)
        return wrapper
    return decorator

# Specific decorators for each role
def judge_required(view_func):
    return role_required(['judge'], error_message="Only judges can perform this action.")(view_func)

def police_officer_required(view_func):
    return role_required(['police officer'], error_message="Only police officers can perform this action.")(view_func)

def investigator_required(view_func):
    return role_required(['investigator'], error_message="Only investigators can performthis action.")(view_func)