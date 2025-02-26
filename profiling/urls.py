from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import UserViewSet, CrimeViewSet, OffenderViewSet, InvestigationViewSet, JudicialCaseViewSet
from profiling import views

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'crimes', CrimeViewSet)
router.register(r'offenders', OffenderViewSet)
router.register(r'investigations', InvestigationViewSet)
router.register(r'judicial_cases', JudicialCaseViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('',views.index_view,name="index"),
    path('dashboard/',views.profiling_view,name="profiling_view"),
]