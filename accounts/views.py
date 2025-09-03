from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpResponse
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.utils import send_email_confirmation
from allauth.account import app_settings

User = get_user_model()

# Create your views here.

@login_required
def custom_logout(request):
    """Custom logout view that bypasses confirmation"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('exams:home')

def custom_email_verification_sent(request):
    """Custom view for email verification sent page"""
    return render(request, 'account/email_verification_sent.html')

def custom_email_confirm(request, key):
    """Custom view to handle email confirmation"""
    try:
        # Try to get the email confirmation
        emailconfirmation = EmailConfirmationHMAC.from_key(key)
        if emailconfirmation is None:
            emailconfirmation = EmailConfirmation.objects.get(key=key)
        
        # Confirm the email
        emailconfirmation.confirm(request)
        
        # Mark the email as verified
        emailconfirmation.email_address.verified = True
        emailconfirmation.email_address.set_as_primary()
        emailconfirmation.email_address.save()
        
        # Show success message
        messages.success(request, 'Your email has been successfully verified!')
        
        # Redirect to the success page
        return render(request, 'account/email_confirm.html')
        
    except EmailConfirmation.DoesNotExist:
        messages.error(request, 'Invalid or expired confirmation link.')
        return redirect('account_email_verification_sent')
    except Exception as e:
        messages.error(request, 'An error occurred during email verification.')
        return redirect('account_email_verification_sent')
