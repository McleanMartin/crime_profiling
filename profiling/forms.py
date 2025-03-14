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
    class Meta:
        model = Crime
        fields = ['crime_type', 'description', 'location', 'date_reported', 'status', 'tags']
        widgets = {
            'date_reported': forms.DateInput(attrs={'type': 'date'}),
        }

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['role', 'name', 'contact_info', 'date_of_birth', 'address', 'relationship_to_case']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'role': forms.Select(attrs={'class': 'party-role-select'}),
        }