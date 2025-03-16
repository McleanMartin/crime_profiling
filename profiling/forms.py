from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'department', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'username':
                field.widget.attrs.update({'placeholder': 'Enter username'})
            elif field_name == 'email':
                field.widget.attrs.update({'placeholder': 'Enter email'})
            elif field_name == 'password1':
                field.widget.attrs.update({'placeholder': 'Enter password'})
            elif field_name == 'password2':
                field.widget.attrs.update({'placeholder': 'Confirm password'})

class EvidenceUploadForm(forms.ModelForm):
    class Meta:
        model = Investigation
        fields = ['evidence_files']

class JudicialCaseStatusForm(forms.ModelForm):
    class Meta:
        model = JudicialCase
        fields = ['status']


class NextHearingForm(forms.ModelForm):
    class Meta:
        model = JudicialCase
        fields = ['next_hearing_date']


class CrimeForm(forms.ModelForm):
    CRIME_TYPE_CHOICES = [
        ('theft', 'Theft'),
        ('assault', 'Assault'),
        ('burglary', 'Burglary'),
        ('fraud', 'Fraud'),
        ('vandalism', 'Vandalism'),
        ('cybercrime', 'Cybercrime'),
    ]

    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
    ]

    crime_type = forms.ChoiceField(choices=CRIME_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
    }))
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
    }))

    class Meta:
        model = Crime
        fields = ['crime_type', 'description', 'location','documents','date_reported', 'status', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter crime description',
                'rows': 3,
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter crime location',
            }),
            'documents': forms.FileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Upload Document',
            }),
            'date_reported': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags (comma-separated)',
            }),
        }
        
class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['role', 'name', 'contact_info', 'date_of_birth', 'address', 'relationship_to_case']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact info'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}),
            'relationship_to_case': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter relationship to case'}),
        }