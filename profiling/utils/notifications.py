from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from profiling.models import *

def create_notification(
    recipient, 
    notification_type, 
    message, 
    content_object=None, 
    metadata=None
):
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        message=message,
        content_type=ContentType.objects.get_for_model(content_object) if content_object else None,
        related_object_id=content_object.id if content_object else None,
        metadata=metadata or {}
    )
    return notification

def send_email_notification(notification):
    subject = notification.get_notification_type_display()
    message = f"{notification.message}\n\nView details: {notification.content_object.get_absolute_url()}"
    
    send_mail(
        subject,
        message,
        'noreply@crimesystem.com',
        [notification.recipient.email],
        fail_silently=True,
    )


