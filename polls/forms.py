# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User,Group
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from django.db import connection
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext


# Create your views here.

import re
import logging

logger = logging.getLogger(__name__)


#LOGIN
class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'),required=True)
    password = forms.CharField(label=_('Password'),widget=forms.PasswordInput())


# from captcha.fields import CaptchaField, CaptchaTextInput
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="账号", max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class RegisterForm(forms.Form):
    username = forms.CharField(label="账号", max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
