from django import forms
from .models import CustomUser
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm
)

class CustomUserCreationForm(UserCreationForm):  # Fixed typo
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):  
    # Removed Meta class because AuthenticationForm does not use it
    pass  


class CustomPasswordResetForm(PasswordResetForm):  # Fixed typo
    email = forms.EmailField(required=True)


class CustomSetPasswordForm(SetPasswordForm):
    pass  # Removed Meta class since SetPasswordForm does not require model fields


class CustomUserChangeForm(UserChangeForm):
    password = None  # Prevents password from being displayed in the form

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):  # Fixed indentation and method name
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
