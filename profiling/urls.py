from django.urls import path
from .views import *

urlpatterns = [
    path('', index_view, name='index'),
     path('trends/', dashboard, name='trends'),
    path('crimes/', crime_list, name='crime_list'),
    path('crimes/<int:pk>/', crime_detail, name='crime_detail'),
    path('crimes/create/', CrimeCreateView.as_view(), name='crime_create'),
    path('crimes/<int:pk>/update/', CrimeUpdateView.as_view(), name='crime_update'),
    path('court_roll/', court_roll, name='court_roll'),
    path('investigations/<int:pk>/', investigation_detail, name='investigation_detail'),
    path('investigations/<int:investigation_id>/upload_evidence/', upload_evidence, name='upload_evidence'),
    path('judicial_cases/<int:pk>/update_status/', update_case_status, name='update_case_status'),
    path('judicial_cases/<int:pk>/schedule_hearing/', schedule_next_hearing, name='schedule_next_hearing'),
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/mark-read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
    path('logout/', Logout_view, name='logout'),
]