from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    institution_name = forms.CharField()

    class Meta:
        model = User
        fields = ["institution_name", "email", "username", "password1", "password2"]
