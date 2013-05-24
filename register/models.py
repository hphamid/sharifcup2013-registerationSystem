# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import hashlib
from django.core.exceptions import ValidationError  # for validation purpose! :)
# for email in Participant
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


class Superviser(models.Model):
    user = models.OneToOneField(User, default=0)
    phone = models.CharField(max_length=20, blank=False)
    nationalID = models.CharField(unique=True, max_length=11, blank=False)
    age = models.CharField(max_length=3, blank=False)
    errorMessage = []

    def save(this, *args, **kwargs):
        this.errorMessage = []
        try:
            this.full_clean()
        except ValidationError as e:
            this.errorMessage.append(str(e))
        else:
            try:
                super(Superviser, this).save(*args, **kwargs)
            except:
                this.errorMessage = [u'مشکلی در هنگام ذخیره به وجود آمد!']

    def issaved(this):
        return not this.errorMessage


class League(models.Model):
    name = models.CharField(max_length=20)

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
    name = models.CharField(max_length=30)
    # users = models.ManyToManyField(Participant)
    superviser = models.ForeignKey(User)
    league = models.ForeignKey(League)
    errorMessage = []

    def clean(this):
        temp = Team.objects.filter(
            league=this.league, name=this.name).exclude(id=this.id)
        if temp:
            raise ValidationError(
                u'تیمی با نام وادر شده در این لیگ وجود دارد!')

    def save(this, *args, **kwargs):
        this.errorMessage = []
        try:
            this.full_clean()
        except ValidationError as e:
            this.errorMessage.append(str(e))
        else:
            try:
                super(Team, this).save(*args, **kwargs)
            except:
                this.errorMessage = [u'مشکلی در هنگام ذخیره به وجود آمد!']

    def issaved(this):
        return not this.errorMessage

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
        'invalid': u'ایمیل وارد شده صحیح نیست'
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
    team = models.ManyToManyField(Team, null=True)
    activate = models.BooleanField(default=False)
    errorMessage = {}
    __securityString = "security string for increading something! :)))"

    # def clean(this):
    #     temp = Team.objects.filter(
    #         league=this.league, name=this.name).exclude(id=this.id)
    #     if temp:
    #         raise ValidationError(
    #             'تیمی با نام وادر شده در این لیگ وجود دارد!')
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

    def activateUserEmailAddress(this, email, text):
        this.email = this.user.email
        this.username = this.user.username
        if text == this.makeActivationAddress():
            this.user.is_active = True
            this.user.save()
            return True
        return False

    def makeActivationAddress(this):
        return hashlib.sha224(this.__securityString + this.email + this.nationalID).hexdigest()

    def makeActivationLink(this, address):
        text = this.makeActivationAddress()
        return address + reverse('activate', args=(this.email, text))

    def sendMail(this, address):  # this function send activation email! :) (the html part must be edited! :P)
        plaintext = get_template('mail/activationEmail.txt')
        htmly = get_template('mail/activationemail.html')
        d = Context({'name': this.name, 'lastname': this.fname,
                    'address': this.makeActivationLink(address)})
        subject, from_email, to = 'SharifcupRegister', 'info@sharifcup.sharif.ir', this.email
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def __unicode__(this):
        return this.name + ' ' + this.fname
