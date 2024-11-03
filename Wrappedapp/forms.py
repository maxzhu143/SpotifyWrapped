"""Form configurations for Wrappedapp."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

"""User registration form extending Django's UserCreationForm."""
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        """Meta class to specify model and fields for the form."""
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
