from django.contrib import admin
from models import *


class ParticipantInline(admin.TabularInline):
    model = Participant.team.through  # for many to many fields! :)
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league')
    # filter_horizontal = ('ParticipantInline',)
    inlines = [ParticipantInline]
    save_on_top = True

admin.site.register(Team, TeamAdmin)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'fname', 'superviser')
    filter_horizontal = ('team',)
    # inlines = [TeamInline]
    save_on_top = True
admin.site.register(Participant, ParticipantAdmin)


class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name',)
    # filter_horizontal = ('league',)
    # inlines = [WantKeyValueInline]
    save_on_top = True
admin.site.register(League, LeagueAdmin)


class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'nationalID')
    # filter_horizontal = ('ParticipantInline',)
    # inlines = [ParticipantInline]
    save_on_top = True

admin.site.register(Superviser, SupervisorAdmin)
