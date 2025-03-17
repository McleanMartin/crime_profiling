from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from profiling.models import Crime, JudicialCase, Investigation, CustomUser
from profiling.utils.notifications import create_notification
import re
import random


@receiver(post_save, sender=Crime)
def generate_case_number_signal(sender, instance, created, **kwargs):
    """
    Generates and saves a case number after crime record creation.
    - Uses post_save to ensure we don't attempt this before the object exists.
    - Implements retry logic for potential collisions.
    - Updates the instance without infinite signal recursion.
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
    """
    Creates an initial judicial case and assigns a random judge and investigator
    when a new crime is reported.
    """
    if created:
        try:
            # Randomly assign a judge to the judicial case
            judges = CustomUser.objects.filter(role='judge')
            if judges.exists():
                judge = random.choice(judges)
                JudicialCase.objects.create(
                    crime=instance,
                    judge=judge,
                    date_heard=timezone.now().date(),
                    court_location='Central Courthouse',
                    status='pending'
                )
            else:
                print("No judge found to assign to the judicial case.")

            # Randomly assign an investigator to the investigation
            investigators = CustomUser.objects.filter(role='investigator')
            if investigators.exists():
                investigator = random.choice(investigators)
                Investigation.objects.create(
                    crime=instance,
                    investigator=investigator,
                    status='pending'
                )
            else:
                print("No investigator found to assign to the investigation.")

        except Exception as e:
            print(f"Error creating judicial case or investigation: {str(e)}")


@receiver(post_save, sender=Crime)
def notify_crime_creation(sender, instance, created, **kwargs):
    """
    Sends notifications to investigators when a new crime is created.
    """
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
    """
    Sends notifications to the assigned judge when a new hearing is scheduled.
    """
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
    """
    Sends notifications to the investigator and related police officers when an investigation is created or updated.
    """
    action = "created" if created else "updated"
    message = f"Investigation {action}: {instance.crime.crime_type}"
    
    # Get recipients (investigator and police officers in the same department)
    recipients = [
        instance.investigator,
        *CustomUser.objects.filter(role='police', department=instance.investigator.department)
    ]
    
    # Send notifications to each recipient
    for user in set(recipients):
        create_notification(
            user,
            'investigation_update',
            message,
            content_object=instance,
            metadata={'status': instance.status}
        )