from django import forms
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm

User = get_user_model()


class CustomSignupForm(SignupForm):
    """Custom signup form that includes role selection"""
    
    role = forms.ChoiceField(
        choices=User.Role.choices,
        initial=User.Role.EXAMINEE,
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        label='Select Your Role'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default role from URL parameter if available
        if 'role' in self.initial:
            self.fields['role'].initial = self.initial['role']
        elif 'role' in self.data:
            self.fields['role'].initial = self.data['role']
    
    def save(self, request):
        # Call the parent save method to create the user
        user = super().save(request)
        
        # Set the role based on form data
        role = self.cleaned_data.get('role')
        if role:
            user.role = role
            user.save()
        
        return user
