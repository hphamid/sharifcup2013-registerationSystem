# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm
from django import forms


class loginform(AuthenticationForm):
    error_messages = {
        'invalid_login': 'نام کاربری و/یا پسورد اشتباه است!',
        'no_cookies': u"کوکی‌ در بروزر شما غیر فعال است! برای استفاده از سیستم ثبت‌نام کوکی باید فعال باشد!",
        'inactive': u"نام کاربری فعال نشده است!",
    }
    username = forms.CharField(max_length=254, widget=forms.TextInput(
        attrs={'placeholder': 'نام کاربری'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(
        attrs={'placeholder': 'کلمه‌ی عبور'}))


class ChangePasswordForm(forms.Form):
    messages = {
        'blank': u'این فیلد نمی‌تواند خالی باشد',
        'invalid': u'اطلاعات وارد شده معتبر نیست!',
        'required': u'این فیلد اجباری است.',
    }
    oldPassword = forms.CharField(
        widget=forms.PasswordInput, max_length=30, required=True, error_messages=messages)
    newPassword = forms.CharField(
        widget=forms.PasswordInput, max_length=30, required=True, error_messages=messages)
    newPasswordR = forms.CharField(
        widget=forms.PasswordInput, max_length=30, required=True, error_messages=messages)

    def clean(this):
        cleaned_data = super(ChangePasswordForm, this).clean()
        newPass = cleaned_data.get("newPassword")
        newPassR = cleaned_data.get("newPasswordR")
        if newPass != newPassR:
                raise forms.ValidationError("پسورد‌ها یکی نیستند.")
        return cleaned_data
