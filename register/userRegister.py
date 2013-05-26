# -*- coding: UTF8

from django.contrib.auth.models import User
from register.models import Superviser
from django.contrib.auth import authenticate, login
import re
# for email:
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core.urlresolvers import reverse
import hashlib
# import string
# import random


class MyUser():  # this class contains function to use for flight users! :)
    __messages = {'badUsername': 'نام کاربری معتبر نیست!',
                  'badEmail': 'ایمیل وارد شده معتبر نیست!',
                  'badPassword': 'پسورد وارد شده معتبر نیست',
                  'emailExists': 'کاربری با ایمیل وارد شده موجود است.',
                  'usernameExists': 'نام کاربری در سیستم موجود است.',
                  'failed': 'اطلاعات وارد شده صحیح نیست! لطفا دوبراه بررسی کنید.'
                  }
    __securityString = "security string for increading something in MyUser! :)))"

    def __init__(this, username=None, password=None, password2=None, email=None, name=None, lastname=None, phone=None, nationalID=None, age=None, gender=None, night=None, isActive=False, loginAfterRegister=False):
        this.username = username
        this.email = email
        this.name = name
        this.lastname = lastname
        this.password = password
        this.password2 = password2
        this.phone = phone
        this.nationalID = nationalID
        this.age = age
        this.gender = gender
        this.night = night
        this.user = None
        this.profile = None
        this.isActive = isActive
        # this.loginAfterRegister = loginAfterRegister
        this.message = {}

    # def makeSureThereIsprofile(this):
    # try:  # to make sure there is appropiate profile for each user! :)
    #         this.user.profile.get()
    #     except:
    #         this.user.profile = Superviser()
    #         this.user.profile.save()

    # def makePassword(this):
    # return hashlib.sha224(this.__securityString + this.username +
    # this.randomString()).hexdigest()[5:20]

    # def randomString(this, size=10, chars=string.ascii_letters + string.digits):
    #     return ''.join(random.choice(chars) for i in range(size))

    def updateInformation(this):
        if this.getUser():
            this.name = this.user.first_name
            this.lastname = this.user.last_name
            this.email = this.user.email
            this.getprofile()
            this.phone = this.profile.phone
            this.nationalID = this.profile.nationalID
            this.age = this.profile.age
            this.gender = this.profile.gender
            this.night = this.profile.night
            return True
        return False

    def getUser(this):  # this function returns true if user exists
        try:
            this.user = User.objects.get(username=this.username)
            if this.user:
                return True
        except:
            pass
        return False

    def userIsOk(this):  # this function authenticate user and if user exist this.user would be the user! :)
        this.user = authenticate(
            username=this.username, password=this.password)
        if this.user is not None:
            if this.user.is_active:
                return True
        return False

    def login(this, request):  # this function login given user but request is necessary
        if this.userIsOk():  # this line check user and update this.user
            login(request, this.user)
            return True
        return False

    def updateUser(this, request):
        if this.getUser() and this.canUpdateUser():
            emailIsChanged = not this.user.email == this.email
            print this.user.email
            print this.email
            this.isActive = this.user.is_active and not emailIsChanged
            this.saveInformation(True)
            if this.issaved():
                if emailIsChanged:
                    this.sendMail(request)
                return True
        return False

    def makeUser(this, request):  # making new user
        if this.canMakeUser():
            this.user = User.objects.create_user(
                this.username, this.email, this.password)  # using django users and making a new user object
            this.saveInformation()
            if this.issaved():
                this.sendMail(request)
                return True
        try:  # to make sure no extra user is made! :)
            this.user.delete()
        except:
            return True
        return False

    def getprofile(this):
        this.profile = this.user.superviser

    def issaved(this):
        return not this.message

    def saveInformation(this, update=False):
        this.user.first_name = this.name
        this.user.last_name = this.lastname
        this.user.is_staff = False
        this.user.is_active = this.isActive
        this.user.is_superuser = False
        this.user.email = this.email
        if update:
            this.profile = Superviser.objects.get(user=this.user)
        else:
            this.profile = Superviser()
        this.profile.phone = this.phone
        this.profile.nationalID = this.nationalID
        this.profile.age = this.age
        this.profile.gender = this.gender
        this.profile.night = this.night
        this.profile.user = this.user
        this.profile.save()
        if this.profile.issaved():
            try:
                this.user.save()  # saving the new object
            except:
                this.message['all'] = [this.__messages['failed'], ]
        else:
            this.message.update(this.profile.errorMessage)

    def sendMail(this, request):  # this function send activation email! :)
        if this.updateInformation():
            plaintext = get_template('mail/supervactivationEmail.txt')
            htmly = get_template('mail/supervactivationemail.html')
            d = Context({'name': this.name, 'lastname': this.lastname,
                        'address': this.makeActivationLink(request)})
            subject, from_email, to = 'SharifcupRegister', 'info@sharifcup.sharif.ir', this.email
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return True
        return False

    # def postRegisterActions(this, request):
    #     if this.loginAfterRegister and this.isActive:
    #         this.login(request)
    #     return True

    def validateEmail(this):  # this function check if given email obey standard rules for email or not
        if re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", this.email):
            return True
        else:
            this.message['email'] = [this.__messages['badEmail'], ]
            return False

    def validateUserName(this):  # this function check if given username can be valid or not (just for syntax!)
        if this.username:
            return True
        else:
            this.message['username'] = [this.__messages['badUsername'], ]
            return False

    def validatePassword(this):  # this function check password to be valid
        if this.password and this.password == this.password2:
            return True
        else:
            this.message['password'] = [this.__messages['badPassword'], ]
            return False

    def validateOther(this):  # this function is for development! :)
        return True

    def validateUser(this):  # this function check if with given information can make a new user or not
        if this.validateEmail() and this.validateUserName() and this.validatePassword() and this.validateOther():
            return True
        else:
            return False

    def emailExists(this):  # this check if this email exists or not!
        try:
            user = User.objects.filter(
                email=this.email).exclude(username=this.username)
            if user:
                this.message['email'] = [this.__messages['emailExists'], ]
                return True
        except:
            pass
        return False

    def usernameExists(this):  # check if username exists or not
        try:
            User.objects.get(username=this.username)
            this.message['username'] = [this.__messages['usernameExists'], ]
            return True
        except:
            pass
        return False

    def __otherChecksForMake(this):  # this function is for development! :)
        return True

    def canMakeUser(this):  # this function will be executed when a new user must be created
        if this.validateUser():
            if this.usernameExists():
                return False
            elif this.emailExists():
                return False
            elif this.__otherChecksForMake():
                return True
        return False

    def canUpdateUser(this):  # this function will be executed when a new user must be created
        if this.validateEmail():
            if this.emailExists():
                return False
            elif this.__otherChecksForMake():
                return True
        return False

    def activateUserEmailAddress(this, email, text):
        try:
            this.user = User.objects.get(email=email)
        except:
            pass
        else:
            if this.user:
                this.email = this.user.email
                this.username = this.user.username
                if text == this.makeActivationAddress():
                    this.user.is_active = True
                    this.user.save()
                    return True
        return False

    def makeActivationAddress(this):
        return hashlib.sha224(this.__securityString + this.email + this.username + str(this.user.date_joined)).hexdigest()

    def makeActivationLink(this, request, checked=0):  # if checked is 0 wont get data from database
        if checked or this.updateInformation():
            text = this.makeActivationAddress()
            return request.build_absolute_uri(reverse('activate', args=(this.email, text)))
