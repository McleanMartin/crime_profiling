from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from profiling.models import Crime, JudicialCase, Investigation, CustomUser, Notification
from profiling.utils.notifications import create_notification, send_email_notification
import re
import random
import logging
from django.conf import settings
from profiling.models import CustomUser

logger = logging.getLogger(__name__)

def base36_encode(number):
    """
    Converts a positive integer to a base36 string.
    """
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base36 = []
    while number:
        number, remainder = divmod(number, 36)
        base36.append(chars[remainder])
    return ''.join(reversed(base36)) if base36 else '0'

@receiver(post_save, sender=Crime)
def generate_case_number_signal(sender, instance, created, **kwargs):
    if created and not instance.case_number:
        max_retries = 3
        retries = 0
        
        while retries < max_retries:
            try:
                with transaction.atomic():
                    # Generate components
                    location_part = re.sub(r'[^A-Z]', '', instance.location.upper())[:2]
                    location_code = location_part.ljust(2, 'X')[:2]
                    
                    pk_code = base36_encode(instance.pk).rjust(3, '0')[-3:]
                    case_number = f"{location_code}{pk_code}"
                    
                    # Direct database update to avoid signal recursion
                    Crime.objects.filter(pk=instance.pk).update(case_number=case_number)
                    logger.info(f"Generated case number: {case_number} for Crime ID: {instance.pk}")
                    break
                    
            except IntegrityError:
                retries += 1
                # Append retry counter if collision occurs
                pk_code = base36_encode(instance.pk + retries).rjust(3, '0')[-3:]
                case_number = f"{location_code}{pk_code}"
                logger.warning(f"Case number collision detected. Retrying with: {case_number}")
                
        else:
            logger.error(f"Failed to generate unique case number after {max_retries} attempts for Crime ID: {instance.pk}")
            raise RuntimeError(f"Failed to generate unique case number after {max_retries} attempts")

@receiver(post_save, sender=Crime)
def create_judicial_case(sender, instance, created, **kwargs):
    """
    Signal to create a JudicialCase and assign an investigator when a Crime is created.
    """
    if created:
        try:
            # Assign a judge to the JudicialCase
            judges = CustomUser.objects.all()
            if not judges.exists():
                logger.warning("No judges found to assign to the JudicialCase.")
                return
            
            judge = random.choice(judges)
            JudicialCase.objects.create(
                crime=instance,
                judge=judge,  # Use the randomly selected judge
                date_heard=timezone.now().date(),
                hearing_date=timezone.now().date(),
                court_location=settings.DEFAULT_COURT_LOCATION,
                status='pending'
            )
            logger.info(f"JudicialCase created for Crime ID: {instance.pk} with Judge: {judge.username}")

            # Assign an investigator to the Investigation
            investigators = CustomUser.objects.filter(role='investigator')  # Filter only investigators
            if not investigators.exists():
                logger.warning("No investigators found to assign to the Investigation.")
                return
            
            investigator = random.choice(investigators)
            Investigation.objects.create(
                crime=instance,
                investigator=investigator,
                status='pending'
            )
            logger.info(f"Investigation created for Crime ID: {instance.pk} with Investigator: {investigator.username}")

        except Exception as e:
            logger.error(f"Error creating JudicialCase or Investigation for Crime ID {instance.pk}: {e}")

@receiver(post_save, sender=Crime)
def notify_crime_creation(sender, instance, created, **kwargs):
    if created:
        message = f"New crime reported: {instance.crime_type} (Case #{instance.case_number})"
        
        # Notification
        recipients = CustomUser.objects.all()
        for recipient in recipients:
            create_notification(
                recipients=recipient,
                notification_type='crime_created',
                message=message,
                content_object=instance,
                metadata={'priority': 'high'}
            )

@receiver(post_save, sender=JudicialCase)
def notify_hearing_scheduled(sender, instance, created, **kwargs):
    if created:
        message = f"New hearing scheduled for {instance.date_heard}"
        create_notification(
            recipients=instance.judge,
            notification_type='hearing_scheduled',
            message=message,
            content_object=instance,
            metadata={'date': instance.date_heard.isoformat()}
        )

@receiver(post_save, sender=Investigation)
def notify_investigation_update(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    message = f"Investigation {action}: {instance.crime.crime_type}"
    
    # Get recipients (investigator and police officers in the same department)
    recipients = [
        instance.investigator,
        *CustomUser.objects.all()
    ]
    
    # Send notifications to each recipient
    for recipient in recipients:
        create_notification(
            recipients=recipient,
            notification_type='investigation_update',
            message=message,
            content_object=instance,
            metadata={'status': instance.status}
        )