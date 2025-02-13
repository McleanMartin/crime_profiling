from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.db import models as base_models
import jsonfield  # Install using pip install django-jsonfield

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('police', 'Police'),
        ('investigator', 'Investigator'),
        ('judge', 'Judge'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)

class Crime(models.Model):
    crime_type = models.CharField(max_length=100)
    description = models.TextField()
    location = models.PointField()
    date_reported = models.DateField()
    status = models.CharField(max_length=50)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tags = models.CharField(max_length=255, blank=True)

class Offender(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    social_media_links = jsonfield.JSONField(blank=True)
    crimes_committed = models.ManyToManyField(Crime, related_name='offenders')
    criminal_record = models.TextField(blank=True)

class Investigation(models.Model):
    crime = models.ForeignKey(Crime, on_delete=models.CASCADE)
    investigator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_assigned = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50)
    evidence_files = models.FileField(upload_to='evidence/', blank=True)
    timeline = jsonfield.JSONField(blank=True)

class JudicialCase(models.Model):
    crime = models.ForeignKey(Crime, on_delete=models.CASCADE)
    judge = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_heard = models.DateField()
    court_location = models.CharField(max_length=255)
    verdict = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    hearing_dates = jsonfield.JSONField(blank=True)