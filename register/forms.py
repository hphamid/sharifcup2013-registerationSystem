# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm


class loginform(AuthenticationForm):
    error_messages = {
        'invalid_login': u'نام کاربری %(username)s و پسورد اشتباه است!',
        'no_cookies': u"کوکی‌ در بروزر شما غیر فعال است! برای استفاده از سیستم ثبت‌نام کوکی باید فعال باشد!",
        'inactive': u"نام کاربری فعال نشده است!",
    }
