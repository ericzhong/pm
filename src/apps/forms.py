from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django import forms

class PasswordResetByEmailForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("This email is invalid.")

        return email