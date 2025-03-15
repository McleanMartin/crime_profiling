from django.db.models.signals import pre_save, post_save
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from profiling.models import *
from profiling.utils.notifications import *
import re

@receiver(post_save, sender=Crime)
def generate_case_number_signal(sender, instance, created, **kwargs):
    """
    Generates and saves a case number after crime record creation
    - Uses post_save to ensure we don't attempt this before the object exists
    - Implements retry logic for potential collisions
    - Updates the instance without infinite signal recursion
    """
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
                    break
                    
            except IntegrityError:
                retries += 1
                # Append retry counter if collision occurs
                pk_code = base36_encode(instance.pk + retries).rjust(3, '0')[-3:]
                case_number = f"{location_code}{pk_code}"
                
        else:
            raise RuntimeError(f"Failed to generate unique case number after {max_retries} attempts")

def base36_encode(number):
    """Converts a positive integer to a base36 string."""
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base36 = []
    while number:
        number, i = divmod(number, 36)
        base36.append(chars[i])
    return ''.join(reversed(base36)) if base36 else '0'


@receiver(post_save, sender=Crime)
def create_initial_judicial_case(sender, instance, created, **kwargs):
    if created:
        try:
            judge = CustomUser.objects.filter(role='judge').first()
            JudicialCase.objects.create(
                crime=instance,
                judge=judge,
                date_heard=timezone.now().date(),
                court_location='Central Courthouse',
                status='pending'
            )
        except Exception as e:
            print(f"Error creating judicial case: {str(e)}")


@receiver(post_save, sender=Crime)
def notify_crime_creation(sender, instance, created, **kwargs):
    if created:
        message = f"New crime reported: {instance.crime_type} (Case #{instance.case_number})"
        
        # Notify investigators
        investigators = CustomUser.objects.filter(role='investigator')
        for user in investigators:
            create_notification(
                user,
                'crime_created',
                message,
                content_object=instance,
                metadata={'priority': 'high'}
            )

@receiver(post_save, sender=JudicialCase)
def notify_hearing_scheduled(sender, instance, created, **kwargs):
    if created:
        message = f"New hearing scheduled for {instance.date_heard}"
        create_notification(
            instance.judge,
            'hearing_scheduled',
            message,
            content_object=instance,
            metadata={'date': instance.date_heard.isoformat()}
        )

@receiver(post_save, sender=Investigation)
def notify_investigation_update(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    message = f"Investigation {action}: {instance.crime.crime_type}"
    
    recipients = [
        instance.investigator,
        *CustomUser.objects.filter(role='police', department=instance.investigator.department)
    ]
    
    for user in set(recipients):
        create_notification(
            user,
            'investigation_update',
            message,
            content_object=instance,
            metadata={'status': instance.status}
        )