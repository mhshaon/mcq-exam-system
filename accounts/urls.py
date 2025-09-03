from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('logout/', views.custom_logout, name='logout'),
    path('email-verification-sent/', views.custom_email_verification_sent, name='email_verification_sent'),
    path('confirm-email/<str:key>/', views.custom_email_confirm, name='email_confirm'),
]
