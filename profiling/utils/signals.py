# signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from .models import Crime, DailyCrimeCounter, JudicialCase, CustomUser

@receiver(pre_save, sender=Crime)
def generate_crime_number(sender, instance, **kwargs):
    pass

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


# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=Crime)
def notify_crime_creation(sender, instance, created, **kwargs):
    if created:
        message = f"New crime reported: {instance.crime_type} (Case #{instance.crime_number})"
        
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