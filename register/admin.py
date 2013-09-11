from django.contrib import admin
from models import *


class ParticipantInline(admin.TabularInline):
    model = Participant.team.through  # for many to many fields! :)
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'uname', 'uemail', 'league')
    # filter_horizontal = ('ParticipantInline',)
    inlines = [ParticipantInline]
    save_on_top = True

admin.site.register(Team, TeamAdmin)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'fname', 'superviser', 'place')
    # readonly_fields = ('test',)
                       # great!! you can show function output in readonly
                       # fields! :P
    filter_horizontal = ('team',)
    save_on_top = True
admin.site.register(Participant, ParticipantAdmin)


class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name',)
    # filter_horizontal = ('league',)
    save_on_top = True
admin.site.register(League, LeagueAdmin)


class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'nationalID', 'place')
    # filter_horizontal = ('ParticipantInline',)
    # inlines = [ParticipantInline]
    save_on_top = True
admin.site.register(Superviser, SupervisorAdmin)


class TeamPaidAdmin(admin.ModelAdmin):
    list_display = ('superviser', 'team','email', 'league', 'paymentId', 'paid', 'isOk')
    readonly_fields = ('email', 'phone', 'users', 'price')
    save_on_top = True
admin.site.register(TeamPaid, TeamPaidAdmin)


class NightPaidAdmin(admin.ModelAdmin):
    list_display = ('superviser', 'paymentId', 'paid', 'isOk')
    # filter_horizontal = ('ParticipantInline',)
    # inlines = [ParticipantInline]
    save_on_top = True
admin.site.register(NightPaid, NightPaidAdmin)
