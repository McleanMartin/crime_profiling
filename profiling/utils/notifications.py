from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.urls import reverse
from profiling.models import Notification, CustomUser

def create_notification(
    recipient, 
    notification_type, 
    message, 
    content_object=None, 
    metadata=None
):
    """
    Creates a notification for the recipient.
    
    Args:
        recipient (CustomUser): The user who will receive the notification.
        notification_type (str): The type of notification (e.g., 'crime_created', 'hearing_scheduled').
        message (str): The notification message.
        content_object (Model instance, optional): The object related to the notification.
        metadata (dict, optional): Additional metadata for the notification.
    
    Returns:
        Notification: The created notification instance.
    """
    # Ensure the recipient is a CustomUser instance
    if not isinstance(recipient, CustomUser):
        raise ValueError("Recipient must be an instance of CustomUser.")
    
    # Create the notification
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        message=message,
        content_type=ContentType.objects.get_for_model(content_object) if content_object else None,
        related_object_id=content_object.id if content_object else None,
        metadata=metadata or {}
    )
    
    # Send an email notification
    send_email_notification(notification)
    
    return notification


def send_email_notification(notification):
    """
    Sends an email notification to the recipient.
    
    Args:
        notification (Notification): The notification instance to send.
    """
    # Ensure the notification has a recipient with an email address
    if not notification.recipient.email:
        raise ValueError("Recipient must have an email address.")
    
    # Build the email subject and message
    subject = f"Notification: {notification.get_notification_type_display()}"
    message = f"{notification.message}\n\n"
    
    # Add a link to the related object if available
    if notification.content_object and hasattr(notification.content_object, 'get_absolute_url'):
        message += f"View details: {notification.content_object.get_absolute_url()}"
    
    # Send the email
    send_mail(
        subject,
        message,
        'mypolicetxt@gmail.com',  # Replace with your sender email
        [notification.recipient.email],
        fail_silently=True,  # Do not raise errors if email sending fails
    )