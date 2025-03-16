from profiling.models import Notification

def notifications(request):
    if request.user.is_authenticated:
        return {
            'unread_count': Notification.objects.filter(
                recipient=request.user, 
                read=False
            ).count(),
            'recent_notifications': Notification.objects.filter(
                recipient=request.user
            ).order_by('-timestamp')[:5]
        }
    return {}