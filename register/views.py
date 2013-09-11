# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from register.models import *


def signup(request):

    return HttpResponse('\n'.join(hamid.errorMessage))


@login_required
def createTeam(request, id=None):
    if request.method == 'GET':
        oldValue = None
        if id:
            oldValue = get_object_or_404(
                Team, id=id, superviser=request.user)
        return render_to_response(
            'team/create.html', {'leagues': League.nameAndId, 'oldValue': oldValue}, context_instance=RequestContext(request))
    else:
        name = request.POST.get('name', '')
        group = request.POST.get('group', '')
        tleague = request.POST.get('league', '')
        superviser = request.user
        if tleague:
            league = League.objects.get(id=tleague)
        else:
            league = None
        if id:
            team = get_object_or_404(
                Team, id=id, superviser=request.user)
        else:
            team = Team()
        team.name = name
        team.group = group
        if league:
            team.league = league
        team.superviser = superviser
        team.save()
        if team.issaved():
            return HttpResponseRedirect(reverse('listTeam'))
        else:
            oldValue = {
                'name': name,
                'league': league,
                'group': group,
            }
            return render_to_response(
                'team/create.html', {
                    'leagues': League.nameAndId, 'oldValue': oldValue, 'error': team.errorMessage},
                context_instance=RequestContext(request))


@login_required
def listTeam(request):
    teams = Team.objects.filter(superviser=request.user)
    return render_to_response(
        'team/list.html',
        {'teams': teams},)


@login_required
def deleteTeam(request, id):
    if request.method == "GET":
        team = get_object_or_404(
            Team, id=id, superviser=request.user)
        return render_to_response(
            'team/delete.html',
            {'team': team, 'id': id},
            context_instance=RequestContext(request))
    else:
        choice = request.POST.get('approve', '')
        if choice:
            team = get_object_or_404(
                Team, id=id, superviser=request.user)
            team.delete()
        return HttpResponseRedirect(reverse('listTeam'))


@login_required
def userTeam(request, id):
    team = get_object_or_404(
        Team, id=id, superviser=request.user)
    return render_to_response(
        'team/userlist.html',
        {'users': team.participant_set.all},)


def leagueTeams(request, id):
    givenLeague = get_object_or_404(League, id=id)
    team = Team.objects.filter(league=givenLeague)
    return render_to_response("team/leagueTeams.html", {'teams': team, 'i': 0})


@login_required
def participant(request, id=None):
    if request.method == 'GET':
        oldValue = None
        if id:
            oldValue = get_object_or_404(
                Participant, id=id, superviser=request.user)
        return render_to_response(
            'Participant/create.html',
            {'team': Team.list(
                request.user), 'oldValue': oldValue, 'id': id},
            context_instance=RequestContext(request))
    else:
        name = request.POST.get('name', '')
        fname = request.POST.get('fname', '')
        nationalID = request.POST.get('nationalID', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        place = request.POST.get('place', '')
        if id:
            participant = get_object_or_404(
                Participant, id=id, superviser=request.user)
            oldEmail = participant.email
        else:
            oldEmail = None
            participant = Participant()
        participant.name = name
        participant.fname = fname
        participant.nationalID = nationalID
        participant.email = email
        participant.phone = phone
        participant.age = age
        participant.gender = gender
        participant.place = place
        participant.superviser = request.user
        participant.save()
        if participant.issaved():
            leagues = League.nameAndId()
            teams = []
            for key, value in leagues.items():
                temp = request.POST.get('league-' + str(value), '')
                if temp:
                    try:
                        toadd = Team.objects.get(
                            id=temp, superviser=request.user)
                    except:
                        pass
                    else:
                        teams.append(toadd)
            participant.addTeam(teams)
            if participant.email != oldEmail:
                participant.sendMail(request)
            return HttpResponseRedirect(reverse('listParticipant'))
        oldValue = {
            'name': name,
            'fname': fname,
            'nationalID': nationalID,
            'email': email,
            'phone': phone,
            'age': age,
            'gender': gender,
            'place': place,
        }
        return render_to_response(
            'Participant/create.html',
            {'team': Team.list(request.user),
             'error': participant.errorMessage, 'oldValue': oldValue, 'id': id},
            context_instance=RequestContext(request))


@login_required
def deleteParticipant(request, id):
    if request.method == "GET":
        participant = get_object_or_404(
            Participant, id=id, superviser=request.user)
        return render_to_response(
            'Participant/delete.html',
            {'participant': participant, 'id': id},
            context_instance=RequestContext(request))
    else:
        choice = request.POST.get('approve', '')
        if choice:
            participant = get_object_or_404(
                Participant, id=id, superviser=request.user)
            participant.delete()
        return HttpResponseRedirect(reverse('listParticipant'))

from django.conf import settings
from django.contrib.auth import views
from register.forms import loginform


@login_required
def listParticipant(request):
    participants = Participant.objects.filter(superviser=request.user)
    return render_to_response(
        'Participant/list.html',
        {'participants': participants},)


def activateParticipant(request, mail, text):
    try:
        participants = Participant.objects.filter(email=mail)
        ok = True
        for participant in participants:
            if not participant.activateUserEmailAddress(text):
                ok = False
        if ok:
            return render_to_response('Participant/mailactivated.html', {'email': mail})
    except:
        pass
    raise Http404


def activate(request, mail, text):
    user = MyUser()
    if user.activateUserEmailAddress(email=mail, text=text):
        return render_to_response('registration/mailactivated.html', {'email': mail})
    raise Http404


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        return views.login(request, template_name='registration/login.html',
                           authentication_form=loginform)


def logout(request):
    return views.logout_then_login(request)


from register.userRegister import MyUser


def register(request):
    if request.method == 'GET':
        oldValue = None
        logedinUser = False
        if request.user.is_authenticated():
            oldValue = MyUser(username=request.user.username)
            oldValue.updateInformation()
            logedinUser = True
        return render_to_response(
            'registration/register.html',
            {'oldValue': oldValue, 'logedinUser': logedinUser},
            context_instance=RequestContext(request))
    else:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        name = request.POST.get('name', '')
        lastname = request.POST.get('lastname', '')
        nationalID = request.POST.get('nationalID', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        place = request.POST.get('place', '')
        user = MyUser(username=username, password=password,
                      password2=password2, name=name, lastname=lastname,
                      nationalID=nationalID, email=email, phone=phone, age=age, gender=gender, place=place)
        if request.user.is_authenticated():
            user.username = request.user.username
            user.updateUser(request)
            logedinUser = True
        else:
            user.makeUser(request)
            logedinUser = False
        if user.issaved():
            if logedinUser:
                return HttpResponseRedirect(reverse('profile'))
            else:
                return render_to_response('registration/done.html')
        else:
            oldValue = user
            return render_to_response(
                'registration/register.html',
                {'oldValue': user, 'logedinUser':
                    logedinUser, 'error': user.message},
                context_instance=RequestContext(request))


def redirect(request):
    return HttpResponseRedirect(reverse('listTeam'))

from register.forms import ChangePasswordForm


@login_required
def changePassword(request):
    if request.method == "GET":
        data = ChangePasswordForm()
        return render_to_response('registration/changePassword.html',
                                  {'form': data, 'error': ""},
                                  context_instance=RequestContext(request))
    else:
        data = ChangePasswordForm(request.POST)
        error = ""
        if data.is_valid():
            print data.cleaned_data
            if request.user.check_password(data.cleaned_data['oldPassword']):
                request.user.set_password(data.cleaned_data['newPassword'])
                request.user.save()
                return render_to_response('registration/changePasswordDone.html')
            else:
                error = 'پسورد وارد شده صحیح نمی‌باشد.'
        return render_to_response('registration/changePassword.html',
                                  {'form': data, 'error': error},
                                  context_instance=RequestContext(request))


def forgetPassword(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('changePassword'))
    if request.method == "GET":
        return render_to_response('registration/forgetPassword.html',
                                  {'error': []},
                                  context_instance=RequestContext(request))
    else:
        error = []
        email = request.POST.get("email", '')
        if email:
            try:
                user = User.objects.get(email=email)
            except:
                error.append('ایمیل وارد شده معتبر نمی‌باشد.')
            else:
                user.superviser.forgetPassword()
                return render_to_response('registration/forgetPasswordDone.html')
        else:
            error.append('ایمیل نمی‌تواند خالی باشد.')
        return render_to_response('registration/forgetPassword.html',
                                  {'error': error},
                                  context_instance=RequestContext(request))


@login_required
def teamPay(request, id):
    team = get_object_or_404(
        Team, id=id, superviser=request.user)
    try:
        teamPaid = TeamPaid.objects.get(team=team, superviser=request.user)
    except:
        teamPaid = TeamPaid(team=team, superviser=request.user)
    if request.method == "GET":
        return render_to_response(
            'teamPay/edit.html',
            {'users': team.participant_set.all, 'team': team,
             'superviser': request.user, 'paymentId': teamPaid.paymentId, 'error': {}},
            context_instance=RequestContext(request))
    else:
        teamPaid.paymentId = request.POST.get('paymentId', '')
        teamPaid.save()
        if teamPaid.issaved():
            return HttpResponseRedirect(reverse('listTeamPayment'))
        return render_to_response(
            'teamPay/edit.html',
            {'users': team.participant_set.all, 'team': team,
             'superviser': request.user, 'paymentId': teamPaid.paymentId,
             'error': teamPaid.errorMessage},
            context_instance=RequestContext(request))


@login_required
def listTeamPay(request):
    payments = TeamPaid.objects.filter(superviser=request.user)
    try:
        night = NightPaid.objects.get(superviser=request.user)
    except:
        night = None
    return render_to_response(
        'teamPay/list.html',
        {'payList': payments, 'night': night})


@login_required
def deleteTeamPay(request, id):
    teamPay = get_object_or_404(
        TeamPaid, id=id, superviser=request.user)
    if request.method == "GET":
        return render_to_response(
            'teamPay/delete.html',
            {'team': teamPay.team, 'paymentId':
                teamPay.paymentId, 'id': teamPay.id},
            context_instance=RequestContext(request))
    else:
        if request.POST.get('approve', ''):
            teamPay.delete()
        return HttpResponseRedirect(reverse('listTeamPayment'))


@login_required
def night(request):
    users = Participant.objects.filter(superviser=request.user)
    if request.method == "POST":
        for user in users:
            if request.POST.get('user-' + str(user.id), ''):
                user.setNight()
            else:
                user.unsetNight()
        if request.POST.get('superviser', ''):
            request.user.superviser.setNight()
        else:
            request.user.superviser.unsetNight()
    return render_to_response(
        'night/list.html',
        {'users': users, 'superviser': request.user},
        context_instance=RequestContext(request))


@login_required
def nightPay(request):
    users = Participant.objects.filter(superviser=request.user)
    usersList = []
    errors = {}
    try:
        tempNightPay = NightPaid.objects.get(superviser=request.user)
        paymentId = tempNightPay.paymentId
    except:
        tempNightPay = NightPaid()
        tempNightPay.superviser = request.user
        paymentId = ""
    tempNightPay.superviserNight = request.user.superviser.isNight()
    for user in users:
        if user.isNight():
            usersList.append(user)
    price = tempNightPay.price(usersList)
    if request.method == "POST":
        paymentId = tempNightPay.paymentId = request.POST.get('paymentId')
        tempNightPay.makePayment(usersList)
        errors = tempNightPay.errorMessage
        price = tempNightPay.price(usersList)
        if tempNightPay.issaved():
            return HttpResponseRedirect(reverse('night'))
    return render_to_response(
        'night/pay.html',
        {'users': usersList, 'superviser':
            request.user, 'price': price, 'priceList': NightPaid.PRICES, 'error': errors, 'paymentId': paymentId},
        context_instance=RequestContext(request))


@login_required
def deleteNight(request):
    nightPay = get_object_or_404(
        NightPaid, superviser=request.user)
    if request.method == "GET":
        return render_to_response(
            'night/delete.html',
            {'paymentId': nightPay.paymentId},
            context_instance=RequestContext(request))
    else:
        if request.POST.get('approve', ''):
            nightPay.delete()
        return HttpResponseRedirect(reverse('listTeamPayment'))
