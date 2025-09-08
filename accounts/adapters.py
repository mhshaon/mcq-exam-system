from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter to handle role assignment during signup"""
    
    def save_user(self, request, user, form, commit=True):
        """Override save_user to handle custom fields"""
        # Call the parent method first
        user = super().save_user(request, user, form, commit=False)
        
        # Handle role assignment
        if hasattr(form, 'cleaned_data') and 'role' in form.cleaned_data:
            role = form.cleaned_data['role']
            user.role = role
        
        # Handle role from URL parameter if not in form
        elif 'role' in request.GET:
            role = request.GET.get('role', '').upper()
            if role in [choice[0] for choice in user.Role.choices]:
                user.role = role
        
        if commit:
            user.save()
        
        return user
