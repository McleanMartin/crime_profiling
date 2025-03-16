from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def role_required(allowed_roles):
    """
    Custom decorator to restrict access based on user role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Access Denied. You dont have permission to perform that action.")
                return redirect('crime_list') 
        return wrapper
    return decorator

# Specific decorators for each role
def judge_required(view_func):
    return role_required(['judge'])(view_func)

def police_officer_required(view_func):
    return role_required(['police officer'])(view_func)

def investigator_required(view_func):
    return role_required(['investigator'])(view_func)