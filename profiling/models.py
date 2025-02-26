from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.gis.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('police', 'Police'),
        ('investigator', 'Investigator'),
        ('judge', 'Judge'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email


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
    social_media_links = models.JSONField(blank=True, default=dict) 
    crimes_committed = models.ManyToManyField(Crime, related_name='offenders')
    criminal_record = models.TextField(blank=True)

class Investigation(models.Model):
    crime = models.ForeignKey(Crime, on_delete=models.CASCADE)
    investigator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_assigned = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50)
    evidence_files = models.FileField(upload_to='evidence/', blank=True)
    timeline = models.JSONField(blank=True, default=dict)  

class JudicialCase(models.Model):
    crime = models.ForeignKey(Crime, on_delete=models.CASCADE)
    judge = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_heard = models.DateField()
    court_location = models.CharField(max_length=255)
    verdict = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    hearing_dates = models.JSONField(blank=True, default=dict)  