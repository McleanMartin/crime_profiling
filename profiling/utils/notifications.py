from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.conf import settings
from profiling.models import Notification, CustomUser
import logging

logger = logging.getLogger(__name__)

def create_notification(
    recipients, 
    notification_type, 
    message, 
    content_object=None, 
    metadata=None
):
    """
    Creates a notification for one or more recipients.
    
    Args:
        recipients (CustomUser or list): The user(s) who will receive the notification.
        notification_type (str): The type of notification (e.g., 'crime_created', 'hearing_scheduled').
        message (str): The notification message.
        content_object (Model instance, optional): The object related to the notification.
        metadata (dict, optional): Additional metadata for the notification.
    
    Returns:
        Notification or list: The created notification instance(s).
    """
    # Ensure recipients is a list
    if not isinstance(recipients, (list, tuple)):
        recipients = [recipients]
    
    # # Validate recipients
    # for recipient in recipients:
    #     if not isinstance(recipient, CustomUser):
    #         raise ValueError("All recipients must be instances of CustomUser.")
    
    # Validate content_object
    if content_object and not hasattr(content_object, '_meta'):
        raise ValueError("content_object must be a valid Django model instance.")
    
    # Get ContentType for the content_object
    try:
        content_type = ContentType.objects.get_for_model(content_object) if content_object else None
    except ContentType.DoesNotExist:
        content_type = None
    
    # Create notifications
    notifications = [
        Notification(
            recipient=recipient,
            notification_type=notification_type,
            message=message,
            content_type=content_type,
            related_object_id=content_object.id if content_object else None,
            metadata=metadata or {}
        )
        for recipient in recipients
    ]
    
    # Bulk create notifications
    created_notifications = Notification.objects.bulk_create(notifications)
    
    # Send email notifications
    send_email_notification(created_notifications, recipients=recipients)
    
    return created_notifications

def send_email_notification(notifications, recipients=None):
    """
    Sends email notifications to one or more recipients.
    
    Args:
        notifications (Notification or list): The notification instance(s) to send.
        recipients (list): List of CustomUser instances to send the email to.
    """
    # Ensure notifications is a list
    if not isinstance(notifications, (list, tuple)):
        notifications = [notifications]
    
    # Ensure recipients is a list
    if not recipients:
        recipients = list(set(notification.recipient for notification in notifications))
    elif not isinstance(recipients, (list, tuple)):
        recipients = [recipients]
    
    # Validate recipients
    for recipient in recipients:
        if not isinstance(recipient, CustomUser):
            raise ValueError("All recipients must be instances of CustomUser.")
    
    # Send emails for each notification
    for notification in notifications:
        try:
            # Build the email subject and message
            subject = f"Notification: {notification.get_notification_type_display()}"
            message = f"{notification.message}\n\n"
            
            # Add a link to the related object if available
            if notification.content_object and hasattr(notification.content_object, 'get_absolute_url'):
                message += f"View details: {notification.content_object.get_absolute_url()}"
            
            # Send the email to all recipients
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email for user in recipients if user.email],
                fail_silently=True,
            )
            logger.info(f"Email notification sent to {recipients} for notification ID: {notification.id}")
        
        except Exception as e:
            logger.error(f"Failed to send email notification for notification ID: {notification.id}. Error: {e}")