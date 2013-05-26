# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm
from django import forms

AuthenticationForm.error_messages = {
    'invalid_login': u'نام کاربری و پسورد اشتباه است!',
    'no_cookies': u"کوکی‌ در بروزر شما غیر فعال است! برای استفاده از سیستم ثبت‌نام کوکی باید فعال باشد!",
    'inactive': u"نام کاربری فعال نشده است!",
}


class loginform(AuthenticationForm):

    username = forms.CharField(max_length=254, widget=forms.TextInput(
        attrs={'placeholder': 'نام کاربری'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(
        attrs={'placeholder': 'کلمه‌ی عبور'}))
