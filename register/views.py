# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from register.models import *


def signup(request):

    return HttpResponse('\n'.join(hamid.errorMessage))


def createTeam(request):
    if request.method == 'GET':
        return render_to_response(
            'team/create.html', [], context_instance=RequestContext(request))


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
                participant.sendMail(request.META['REMOTE_HOST'])
            return HttpResponseRedirect(reverse('listParticipant'))
        else:
            oldValue = {
                'name': name,
                'fname': fname,
                'nationalID': nationalID,
                'email': email,
                'phone': phone,
                'age': age,
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


@login_required
def listParticipant(request):
    participants = Participant.objects.filter(superviser=request.user)
    return render_to_response(
        'Participant/list.html',
        {'participants': participants},)


def activate(request):
    pass
