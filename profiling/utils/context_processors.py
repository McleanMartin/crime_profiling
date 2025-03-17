from profiling.models import Notification

def notifications(request):
    """
    Adds unread notification count and recent notifications to the template context.
    
    Args:
        request (HttpRequest): The current request object.
    
    Returns:
        dict: A dictionary containing 'unread_count' and 'recent_notifications'.
    """
    if request.user.is_authenticated:
        # Get the unread notification count
        unread_count = Notification.objects.filter(
            recipient=request.user, 
            read=False
        ).count()
        
        # Get the 5 most recent notifications
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-timestamp')[:5]
        
        return {
            'unread_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    return {}