from django import forms
from .models import *

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
        fields = ['crime_type', 'description', 'location', 'date_reported', 'status', 'tags']
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
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'role': forms.Select(attrs={'class': 'party-role-select'}),
        }