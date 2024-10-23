# UserAuth/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class UserEditForm(UserChangeForm):
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        required=False  # Make it optional
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        required=False  # Make it optional
    )

    class Meta:
        model = User
        fields = ('username', 'new_password', 'confirm_password')  # Include only the fields you want to edit

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Check if both password fields match
        if new_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field to prevent it from being rendered
        self.fields.pop('password')