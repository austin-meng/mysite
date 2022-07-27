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

