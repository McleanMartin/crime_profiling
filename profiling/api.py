from rest_framework import viewsets
from .models import CustomUser, Crime, Offender, Investigation, JudicialCase
from .serializers import UserSerializer, CrimeSerializer, OffenderSerializer, InvestigationSerializer, JudicialCaseSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class CrimeViewSet(viewsets.ModelViewSet):
    queryset = Crime.objects.all()
    serializer_class = CrimeSerializer

class OffenderViewSet(viewsets.ModelViewSet):
    queryset = Offender.objects.all()
    serializer_class = OffenderSerializer

class InvestigationViewSet(viewsets.ModelViewSet):
    queryset = Investigation.objects.all()
    serializer_class = InvestigationSerializer

class JudicialCaseViewSet(viewsets.ModelViewSet):
    queryset = JudicialCase.objects.all()
    serializer_class = JudicialCaseSerializer