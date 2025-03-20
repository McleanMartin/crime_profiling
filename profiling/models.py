from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
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
        ('clerk', 'clerk'),
        ('prison officer', 'Prison officer'),
        ('investigator', 'Investigator'),
        ('magistrate', 'Magistrate'),
        ('police officer', 'Police Officer'),

    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.get_full_name() or self.username


class Crime(models.Model):
    # Define choices for crime_type
    CRIME_TYPE_CHOICES = (
        ('theft', 'Theft'),
        ('assault', 'Assault'),
        ('burglary', 'Burglary'),
        ('fraud', 'Fraud'),
        ('vandalism', 'Vandalism'),
        ('drug_offense', 'Drug Offense'),
        ('homicide', 'Homicide'),
        ('cyber_crime', 'Cyber Crime'),
        ('kidnapping', 'Kidnapping'),
        ('rape', 'Rape'),
        ('armed robbery', 'Armed Robbery'),
        ('other', 'Other'),
    )

    crime_type = models.CharField(
        max_length=100,
        choices=CRIME_TYPE_CHOICES,
        default='other', 
    )
    case_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    location = models.TextField()
    date_reported = models.DateField()
    status = models.CharField(max_length=50)
    documents = models.FileField(upload_to='crime_documents/%Y/%m/%d/', blank=True, null=True)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_crime_type_display()} (Case #{self.case_number})"


class JudicialCase(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in progress', 'In Progress'),
        ('closed', 'Closed'),
    )
    crime = models.ForeignKey(Crime, on_delete=models.CASCADE)
    judge = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_heard = models.DateField()
    court_location = models.CharField(max_length=255)
    verdict = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    hearing_date = models.DateField(blank=True, null=True)
    next_hearing_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Case {self.crime.case_number} - {self.crime.crime_type}"


class Investigation(models.Model):
    crime = models.ForeignKey(Crime, on_delete=models.CASCADE)
    investigator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_assigned = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50)
    evidence_files = models.FileField(
        upload_to='evidence/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx'])]
    )


class Party(models.Model):
    ROLE_CHOICES = [
        ('victim', 'Victim'),
        ('witness', 'Witness'),
        ('suspect', 'Suspect'),
    ]
    
    crime = models.ForeignKey(Crime, on_delete=models.CASCADE, related_name='parties')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    relationship_to_case = models.TextField(blank=True)
    additional_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_role_display()}: {self.name}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('crime_created', 'New Crime Reported'),
        ('investigation_update', 'Investigation Update'),
        ('hearing_scheduled', 'Court Hearing Scheduled'),
    )
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict)
    
    def get_preference(self, notification_type):
        return self.preferences.get(notification_type, True)
