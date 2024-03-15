from django import forms
from django.contrib.auth.models import User

from .models import *


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class CreateBundleForm(forms.ModelForm):

    class Meta:
        model = Bundle
        fields = ['name', 'end_date']
