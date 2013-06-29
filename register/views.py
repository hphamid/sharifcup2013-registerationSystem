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
        # print league
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
                'team/create.html', {'leagues': League.nameAndId, 'oldValue': oldValue, 'error': team.errorMessage}, context_instance=RequestContext(request))


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
                temp = request.POST.get('league-' + str(value), 'hamid')
                if temp:
                    try:
                        toadd = Team.objects.get(
                            id=temp, superviser=request.user)
                    except:
                        pass
                    else:
                        teams.append(toadd)
            participant.team = teams
            participant.save()
            if participant.email != oldEmail:
                participant.sendMail(request)
            return HttpResponseRedirect(reverse('listParticipant'))
        else:
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
        participant = get_object_or_404(Participant, email=mail)
        if participant.activateUserEmailAddress(text):
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
                      password2=password2, name=name, lastname=lastname, nationalID=nationalID, email=email, phone=phone, age=age, gender=gender, place=place)
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
            print user.place
            return render_to_response(
                'registration/register.html',
                {'oldValue': user, 'logedinUser':
                    logedinUser, 'error': user.message},
                context_instance=RequestContext(request))


def redirect(request):
    return HttpResponseRedirect(reverse('listTeam'))
