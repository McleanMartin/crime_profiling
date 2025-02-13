from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import UserViewSet, CrimeViewSet, OffenderViewSet, InvestigationViewSet, JudicialCaseViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'crimes', CrimeViewSet)
router.register(r'offenders', OffenderViewSet)
router.register(r'investigations', InvestigationViewSet)
router.register(r'judicial_cases', JudicialCaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]