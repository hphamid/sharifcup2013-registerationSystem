# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import hashlib
# for validation purpose! :)
from django.core.exceptions import ValidationError
# for email in Participant
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import string
import random


class Superviser(models.Model):
    messages = {
        'blank': u'این فیلد نمی‌تواند خالی باشد',
        'invalid': u'اطلاعات وارد شده معتبر نیست!',
        'unique': u'کاربری با این شماره‌ی ملی قبلا ثبت‌نام کرده است!'
    }
    user = models.OneToOneField(User, default=0)
    phone = models.CharField(
        max_length=20, blank=False, error_messages=messages)
    nationalID = models.CharField(
        unique=True, max_length=11, blank=False, error_messages=messages)
    age = models.CharField(max_length=3, blank=False, error_messages=messages)
    male = "0"
    female = "1"
    available_status = ((male, 'male'),
                        (female, 'female'),
                        )
    gender = models.CharField(
        max_length=1, choices=available_status, blank=False, error_messages=messages)
    tehran = "0"
    notTehran = "1"
    available_places = ((tehran, 'tehran'),
                       (notTehran, 'not tehran'),
                        )
    place = models.CharField(
        max_length=1, choices=available_places, blank=True, null=True)
    LOCK = "1"
    UNLOCK = ""
    NIGHT = "3"
    is_activeChoices = ((LOCK, 'LOCK'),
                        (UNLOCK, 'UNLOCK'),
                        (NIGHT, 'NIGHT')
                        )
    extra = models.CharField(
        choices=is_activeChoices, max_length=20, blank=True, null=True)
    errorMessage = {}

    def lock(this):
        if this.extra == this.UNLOCK or this.extra == this.NIGHT:
            this.extra = this.LOCK
            this.save()

    def unlock(this):
        if this.extra == this.LOCK or this.extra == this.NIGHT:
            this.extra = this.NIGHT
            this.save()

    def setNight(this):
        if this.extra != this.LOCK:
            this.extra = this.NIGHT
            this.save()

    def unsetNight(this):
        if this.extra == this.NIGHT:
            this.extra = this.UNLOCK
            this.save()

    def isLocked(this):
        return this.extra == this.LOCK

    def isNight(this):
        return this.extra == this.NIGHT or this.extra == this.LOCK

    def safeToSave(this):
        if this.extra == this.LOCK:
            try:
                old = Participant.objects.get(id=this.id)
                this.gender = old.gender
            except:
                pass
        return True

    def save(this, *args, **kwargs):
        this.errorMessage = {}
        if this.safeToSave():
            try:
                this.full_clean()
            except ValidationError as e:
                for key, value in e.message_dict.items():
                    this.errorMessage[key] = []
                    for message in value:
                        this.errorMessage[key].append(unicode(message))
            else:
                try:
                    super(Superviser, this).save(*args, **kwargs)
                except:
                    this.errorMessage['all'] = [
                        'مشکلی در هنگام ذخیره به وجود آمد!']

    def issaved(this):
        return not this.errorMessage

    def forgetPassword(this):
        password = this.__randomString()
        this.user.set_password(password)
        this.__sendMail(password)
        this.user.save()
        return password

    def __randomString(this, size=10, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for i in range(size))

    def __sendMail(this, password):  # this function send activation email! :)
        plaintext = get_template('mail/resetPassword.txt')
        htmly = get_template('mail/resetPassword.html')
        d = Context(
            {'name': this.user.first_name, 'fname': this.user.last_name,
             'uname': this.user.username, 'password': password})
        subject, from_email, to = 'PasswordReset', 'info@sharifcup.sharif.ir', this.user.email
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class League(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)

    @staticmethod
    def nameAndId():
        temp = {}
        leagues = League.objects.all()
        for league in leagues:
            temp[league.name] = league.id
        return temp

    def __unicode__(this):
        return this.name


class Team(models.Model):
    messages = {
        'blank': u'این فیلد نمی‌تواند خالی باشد',
        'invalid': u'اطلاعات وارد شده معتبر نیست!'
    }
    PRICElIST = {'team': 150, 'teamNew': 200, 'participant': 50}
    name = models.CharField(
        max_length=30, blank=False, error_messages=messages)
    group = models.CharField(
        max_length=70, blank=False, error_messages=messages)
    # users = models.ManyToManyField(Participant)
    superviser = models.ForeignKey(User)
    league = models.ForeignKey(League, blank=False, error_messages=messages)
    NEW = 2
    OLD = 1
    PAIDoLD = 3
    PAIDnEW = 4
    STATES = ((OLD, 'پیش ثبت‌نام شده.'),
             (NEW, 'جدید'),
             (PAIDoLD, 'پرداخت شده با هزینه‌ی کمتر'),
             (PAIDnEW, 'پرداخت شده با جریمه!'),
              )
    is_active = models.PositiveSmallIntegerField(
        choices=STATES, default=2)  # default is 2! to show these team are new! :P
    errorMessage = {}

    def clean(this):
        if this.league:
            temp = Team.objects.filter(
                league=this.league, name=this.name).exclude(id=this.id)
            if temp:
                this.errorMessage['all'] = [
                    'تیمی با نام وارد شده در این لیگ وجود دارد!']
                raise ValidationError('all',
                                      u'تیمی با نام وارد شده در این لیگ وجود دارد!')

    def paid(this):
        return this.is_active == this.PAIDnEW or this.is_active == this.PAIDoLD

    def lock(this):
        if not this.paid():
            # to show this object has just been locked and must be saved once!
            # :)
            this.justLocked = 1
            if this.is_active == this.OLD:
                this.is_active = this.PAIDoLD
            else:
                this.is_active = this.PAIDnEW
            this.save()

    def unlock(this):
        if this.paid():
            if this.is_active == this.PAIDoLD:
                this.is_active = this.OLD
            else:
                this.is_active = this.NEW
            this.save()

    def safeToSave(this):
        return (not this.paid()) or (hasattr(this, 'justLocked') and this.justLocked == 1)

    def delete(this):
        if this.safeToSave():
            super(Team, this).delete()

    def save(this, *args, **kwargs):
        this.errorMessage = {}
        if this.safeToSave():
            try:
                this.full_clean()
            except ValidationError as e:
                for key, value in e.message_dict.items():
                    this.errorMessage[key] = []
                    for message in value:
                        this.errorMessage[key].append(unicode(message))
            except:
                this.errorMessage['all'] = [
                    'مشکلی در هنگام ذخیره به وجود آمد! لیگ را انتخاب کرده‌اید؟!']
            else:
                try:
                    super(Team, this).save(*args, **kwargs)
                except:
                    this.errorMessage['all'] = [
                        'مشکلی در هنگام ذخیره به وجود آمد!']
        else:
            this.errorMessage['all'] = [
                'هزینه‌ی این تیم پرداخت شده است و امکان ایجاد تغییر در این تیم وجود ندارد.']
        this.justLocked = 0

    def price(this):
        teamPrice = this.PRICElIST['participant'] + this.teamPrice()
        for user in this.participant_set.all():
            teamPrice = teamPrice + this.PRICElIST['participant']
        return teamPrice

    def teamPrice(this):
        if this.is_active == this.OLD or this.is_active == this.PAIDoLD:
            return this.PRICElIST['team']
        else:
            return this.PRICElIST['teamNew']

    def issaved(this):
        return not this.errorMessage

    def uname(this):
        return this.superviser.first_name + " " + this.superviser.last_name

    def uemail(this):
        return this.superviser.email

    @staticmethod
    def list(user):
        temp = {}
        leagues = League.objects.all()
        for league in leagues:
            temp[league.name] = Team.objects.filter(
                superviser=user, league=league)
        return temp

    def __unicode__(this):
        return this.name


class Participant(models.Model):
    messages = {
        'blank': u'این فیلد نمی‌تواند خالی باشد',
        'invalid': u'اطلاعات وارد شده معتبر نیست!'
    }
    emailmessages = {
        'blank': u'این فیلد نمی‌تواند خالی باشد',
        'invalid': u'ایمیل وارد شده صحیح نیست',
    }
    name = models.CharField(
        max_length=40, blank=False, error_messages=messages)
    fname = models.CharField(
        max_length=40, blank=False, error_messages=messages)
    nationalID = models.CharField(
        max_length=11, blank=False, error_messages=messages)
    email = models.EmailField(blank=False, error_messages=emailmessages)
    phone = models.CharField(
        max_length=20, blank=False, error_messages=messages)
    age = models.CharField(max_length=3, blank=False, error_messages=messages)
    superviser = models.ForeignKey(User)
    team = models.ManyToManyField(Team, null=True, blank=True)
    activate = models.BooleanField(default=False)
    tehran = "0"
    notTehran = "1"
    available_places = ((tehran, 'tehran'),
                       (notTehran, 'not tehran'),
                        )
    place = models.CharField(
        max_length=1, choices=available_places, blank=True, null=True)
    male = "0"
    female = "1"
    available_status = ((male, 'male'),
                        (female, 'female'),
                        )
    gender = models.CharField(
        max_length=1, choices=available_status, blank=False, error_messages=messages)
    night = models.BooleanField(default=False)
    extra = models.CharField(max_length=20, blank=True, null=True)
    LOCK = 0
    UNLOCK = 1
    is_activeChoices = ((LOCK, 'LOCK'),
                        (UNLOCK, 'UNLOCK'),
                        )
    is_active = models.PositiveSmallIntegerField(
        choices=is_activeChoices, default=UNLOCK)
    errorMessage = {}
    __securityString = "security string for increading something! :)))"

    # def clean(this):
    #     temp = Team.objects.filter(
    #         league=this.league, name=this.name).exclude(id=this.id)
    #     if temp:
    #         raise ValidationError(
    #             'تیمی با نام وادر شده در این لیگ وجود دارد!')
    def lock(this):
        if this.is_active == this.UNLOCK:
            this.is_active = this.LOCK
            this.justLocked = 1
            this.setNight()

    def unlock(this):
        if this.is_active == this.LOCK:
            this.is_active = this.UNLOCK
            this.justLocked = 1
            this.save()

    def setNight(this):
        this.night = True
        this.save()

    def unsetNight(this):
        this.night = False
        this.save()

    def isLocked(this):
        return this.is_active == this.LOCK

    def isNight(this):
        return this.night

    def safeToSave(this):
        this.night = this.night or this.is_active == this.LOCK
        if this.is_active == this.LOCK:
            try:
                old = Participant.objects.get(id=this.id)
                this.gender = old.gender
            except:
                pass
        return True

    def safeToRemove(this):
        safe = True
        for obj in this.team.all():
            if obj.paid():
                safe = False
        return safe and this.is_active == this.UNLOCK

    def delete(this):
        if this.safeToRemove():
            super(Participant, this).delete()

    def addTeam(this, teamList):
        for obj in this.team.all():
            if (not obj in teamList) and obj.paid():
                message = "تیم " + obj.name + \
                    "قفل شده است و امکان اضافه کردن شرکت‌کننده به آن وجود ندارد!"
                this.errorMessage['all'] = [].append(message)
        for obj in teamList:
            if obj.paid() and (not obj in this.team.all()):
                message = "تیم " + obj.name + \
                    "قفل شده است و امکان اضافه کردن شرکت‌کننده به آن وجود ندارد!"
                this.errorMessage['all'] = [].append(message)
        if this.issaved():
            this.team = teamList

    def clean(this):
        if not this.safeToSave():
            message = "امکان ایجاد تغییر در این شرکت کندده وجود ندارد."
            this.errorMessage['all'] = [].append(message)
            raise ValidationError('all', message)
        try:
            Participant.objects.get(
                superviser=this.superviser, email=this.email).exclude(id=this.id)
        except:
            pass
        else:
            this.errorMessage['all'] = [].append(
                'شما قبلا کاربری با ایمیل وارد شده ثبت کرده‌اید!')
            raise ValidationError('all',
                                  u'شما قبلا کاربری با ایمیل وارد شده ثبت کرده‌اید!')

    def save(this, *args, **kwargs):
        this.errorMessage = {}
        try:
            this.full_clean()
        except ValidationError as e:
            for key, value in e.message_dict.items():
                this.errorMessage[key] = []
                for message in value:
                    this.errorMessage[key].append(unicode(message))
        else:
            try:
                super(Participant, this).save(*args, **kwargs)
            except:
                this.errorMessage['all'] = [
                    'مشکلی در هنگام ذخیره به وجود آمد!']

    def issaved(this):
        return not this.errorMessage

    def activateUserEmailAddress(this, text):
        if text == this.makeActivationAddress():
            this.activate = True
            this.save()
            return True
        return False

    def makeActivationAddress(this):
        return hashlib.sha224(this.__securityString + this.email).hexdigest()

    def makeActivationLink(this, request):
        text = this.makeActivationAddress()
        return request.build_absolute_uri(reverse('activateParticipant', args=(this.email, text)))

    def sendMail(this, request):  # this function send activation email! :)
        plaintext = get_template('mail/activationEmail.txt')
        htmly = get_template('mail/activationemail.html')
        d = Context({'name': this.name, 'lastname': this.fname,
                    'sname': this.superviser.first_name, 'sfname': this.superviser.last_name,
                    'address': this.makeActivationLink(request)})
        subject, from_email, to = 'SharifcupRegister', 'info@sharifcup.sharif.ir', this.email
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def __unicode__(this):
        return this.name + ' ' + this.fname


class TeamPaid(models.Model):
    messages = {
        'blank': u'این فیلد نمی‌تواند خالی باشد',
        'invalid': u'اطلاعات وارد شده معتبر نیست!',
        'unique': u'این شناسهی پرداخت قبلا استفاده شده است.'
    }
    superviser = models.ForeignKey(User)
    paid = models.IntegerField()
    paymentId = models.CharField(
        unique=True, blank=False, null=False, max_length=30, error_messages=messages)
    team = models.ForeignKey(Team, blank=False, error_messages=messages)
    isOk = models.BooleanField(default=0)
    extra = models.PositiveSmallIntegerField(default=0)
    errorMessage = {}

    def email(this):
        return this.superviser.email

    def phone(this):
        return this.superviser.superviser.phone

    def league(this):
        return this.team.league

    def superviserName(this):
        return this.superviser.first_name + " " + this.superviser.last_name

    def users(this):
        toReturn = ""
        for participant in this.team.participant_set.all():
            toReturn = toReturn + participant.name + \
                " " + participant.fname + "-"
        return toReturn

    def price(this):
        return this.team.price()

    def clean(this):
        try:
            NightPaid.objects.get(paymentId=this.paymentId)
        except:
            pass
        else:
            this.errorMessage['all'] = [
                'از این شناسه‌ی پرداخت قبلا استفاده شده است.']
            raise ValidationError(
                'از این شناسه‌ی پرداخت قبلا استفاده شده است.', 'all')
        try:
            this.team.lock()
        except:
            this.errorMessage['all'] = [
                'مشکلی در هنگام ذخیره‌سازی به پجود آمد.']
            raise ValidationError(
                'all', 'مشکلی در هنگام ذخیره‌سازی به پجود آمد.')
        finally:
            try:
                old = TeamPaid.objects.get(id=this.id)
            except:
                pass
            else:
                if old.isOk:
                    this.errorMessage['all'] = [
                        'این شناسه‌ی پرداخت تایید شده است و امکان ایجاد تغییر وجود ندارد.']
                    raise ValidationError(
                        'این شناسه‌ی پرداخت تایید شده است و امکان ایجاد تغییر وجود ندارد.', 'all')

    def save(this, *args, **kwargs):
        this.errorMessage = {}
        this.paid = this.team.price()
        try:
            this.full_clean()
        except ValidationError as e:
            for key, value in e.message_dict.items():
                this.errorMessage[key] = []
                for message in value:
                    this.errorMessage[key].append(unicode(message))
        except:
            this.errorMessage['all'] = [
                'مشکلی در هنگام ذخیره به وجود آمد! لیگ را انتخاب کرده‌اید؟!']
        else:
            try:
                super(TeamPaid, this).save(*args, **kwargs)
            except:
                this.errorMessage['all'] = [
                    'مشکلی در هنگام ذخیره به وجود آمد!']

    def delete(this):
        if not this.isOk:
            this.team.unlock()
            super(TeamPaid, this).delete()

    def issaved(this):
        return not this.errorMessage

    def __unicode__(this):
        return this.team.name


class NightPaid(models.Model):
    messages = {
        'blank': u'این فیلد نمی‌تواند خالی باشد',
        'invalid': u'اطلاعات وارد شده معتبر نیست!',
        'unique': u'این شناسهی پرداخت قبلا استفاده شده است.'
    }
    superviser = models.ForeignKey(User)
    paid = models.IntegerField()
    paymentId = models.CharField(
        unique=True, blank=False, null=False, max_length=30, error_messages=messages)
    users = models.ManyToManyField(Participant, blank=True, null=True)
    superviserNight = models.BooleanField(default=False)
    isOk = models.BooleanField(default=0)
    extra = models.PositiveSmallIntegerField(default=0)
    errorMessage = {}
    PRICES = {'male': 75, 'female': 75}

    def makePayment(this, plist):
        this.paid = this.price(plist)
        try:
            for person in plist:
                person.lock()
            if this.superviserNight:
                this.superviser.superviser.lock()
        except:
            this.errorMessage['all'] = [
                'مشکلی در هنگام ذخیره به وجود آمد!']
        this.save()
        if this.issaved():
            this.users = plist
            this.save()

    def price(this, plist):
        price = 0
        if this.superviserNight:
            if this.superviser.superviser.gender == this.superviser.superviser.male:
                price = price + this.PRICES['male']
            else:
                price = price + this.PRICES['female']
        for user in plist:
            if user.gender == user.male:
                price = price + this.PRICES['male']
            else:
                price = price + this.PRICES['female']
        return price

    def clean(this):
        try:
            TeamPaid.objects.get(paymentId=this.paymentId)
        except:
            pass
        else:
            this.errorMessage['all'] = [
                'از این شناسه‌ی پرداخت قبلا استفاده شده است.']
            raise ValidationError(
                'all', 'از این شناسه‌ی پرداخت قبلا استفاده شده است.')
        try:
            old = NightPaid.objects.get(id=this.id)
        except:
            pass
        else:
            if old.isOk:
                this.errorMessage['all'] = [
                    'این شناسه‌ی پرداخت تایید شده است و امکان ایجاد تغییر وجود ندارد.']
                raise ValidationError(
                    'این شناسه‌ی پرداخت تایید شده است و امکان ایجاد تغییر وجود ندارد.', 'all')

    def save(this, *args, **kwargs):
        this.errorMessage = {}
        try:
            this.full_clean()
        except ValidationError as e:
            for key, value in e.message_dict.items():
                this.errorMessage[key] = []
                for message in value:
                    this.errorMessage[key].append(unicode(message))
        except:
            this.errorMessage['all'] = [
                'مشکلی در هنگام ذخیره به وجود آمد!']
        else:
            try:
                super(NightPaid, this).save(*args, **kwargs)
            except:
                this.errorMessage['all'] = [
                    'مشکلی در هنگام ذخیره به وجود آمد!']

    def delete(this):
        if not this.isOk:
            for person in this.users.all():
                person.unlock()
            this.superviser.superviser.unlock()
            super(NightPaid, this).delete()

    def issaved(this):
        return not this.errorMessage

    def superviserName(this):
        return this.superviser.first_name + " " + this.superviser.last_name

    def email(this):
        return this.superviser.email

    def phone(this):
        return this.superviser.superviser.phone

    def __unicode__(this):
        return this.superviser.first_name
