from rest_framework import serializers
from .models import CustomUser, Crime, Offender, Investigation, JudicialCase

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CrimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crime
        fields = '__all__'

class OffenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offender
        fields = '__all__'

class InvestigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investigation
        fields = '__all__'

class JudicialCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = JudicialCase
        fields = '__all__'