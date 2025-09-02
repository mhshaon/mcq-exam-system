from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

# Create your views here.

@login_required
def custom_logout(request):
    """Custom logout view that bypasses confirmation"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('exams:home')
