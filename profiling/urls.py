from django.urls import path
from .views import *

urlpatterns = [
    path('', public_view, name='public'),
    path('accounts/login/', index_view, name='index'),
    path('trends/', dashboard, name='trends'),
    path('crimes/', crime_list, name='crime_list'),
    path('crimes/<int:pk>/', crime_detail, name='crime_detail'),
    path('crimes/create/', create_crime, name='crime_create'),
    path('crimes/<int:pk>/update/', update_crime, name='crime_update'),
    path('crimes/<int:pk>/delete/', delete_crime, name='delete_crime'),
    path('court_roll/', court_roll, name='court_roll'),
    path('investigations/<int:pk>/', investigation_detail, name='investigation_detail'),
    path('investigations/<int:pk>/upload_evidence/', upload_evidence, name='upload_evidence'),
    path('judicial_cases/<int:pk>/update_status/', update_case_status, name='update_case_status'),
    path('judicial_cases/<int:pk>/schedule_hearing/', schedule_next_hearing, name='schedule_next_hearing'),
    path('monthly-report/', monthly_report, name='monthly_report'),
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/mark-read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
    path('parties/edit/<int:pk>/', edit_party_view, name='edit_party'),
    path('parties/delete/<int:pk>/', delete_party_view, name='delete_party'),
    path('create/user/', custom_user_create_view, name='create_user'),
    path('users/', custom_user_list_view, name='users'),
    path('logout/', Logout_view, name='logout'),
]