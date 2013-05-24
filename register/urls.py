from django.conf.urls import patterns, url  # , include

urlpatterns = patterns('register.views',
                       url(r'^signup/$', 'signup', name='signup'),
                       url(r'^team/create/$', 'createTeam', name='createTeam'),
                       url(r'^participant/create/$',
                           'participant', name='createParticipant'),
                       url(r'^participant/delete/(?P<id>\d+)/$',
                           'deleteParticipant', name='deleteParticipant'),
                       url(r'^participant/$',
                           'listParticipant', name='listParticipant'),
                       url(r'^participant/edit/(?P<id>\d+)/$',
                           'participant', name='editParticipant'),
                       url(r'^activate/email/(.+)/(.+)/$',
                           'activate', name='activate'),
                       )
