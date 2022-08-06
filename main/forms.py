from django import forms
from django.utils.translation import gettext_lazy as _

import logging
logger = logging.getLogger(__name__)


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'), required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs={'class': 'form-control'}))

