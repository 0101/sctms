from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

from tms.models import Tournament
from tms.views import TmsNyxAuth


urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'tms/login.html'}, name='login'),
)

urlpatterns += patterns('tms.views',
    url(r'^$', 'index', name='index'),
    url(r'^reg/$', 'registration', name='registration'),
    url(r'^logout/$', 'logout', name='logout'),
    #url(r'^nyxauth/authenticate/', redirect_to,
    #    {'url': 'http://thensl.cz/nyxauth/authenticate/', 'query_string': True}),
    url(r'^nyxauth/', include(TmsNyxAuth().urls(), namespace='nyxauth')),
    url(r'^delete-replay/', 'delete_replay', name='delete_replay'),
    url(r'^banner/$', 'banner', name='banner'),
    url(r'^status/$', 'status', name='status'),
    #url(r'^player/(?P<username>[\w_@-]+)/$', 'player_profile', name='player_profile'),
    url(r'^match/(?P<id>\d+)/replays/$', 'match_replays', name='match_replays'),
    url(r'^match/(?P<id>\d+)/replays/upload/$', 'upload_replay', name='upload_replay'),


    #url(r'^(?P<slug>[\w_-]+)/$', 'tournament', name='tournament'),
    #url(r'^(?P<slug>[\w_-]+)/players/$', 'tournament_players', name='tournament_players'),
    #url(r'^(?P<slug>[\w_-]+)/rounds/$', 'tournament_rounds', name='tournament_rounds'),
    #url(r'^(?P<slug>[\w_-]+)/round/(?P<id>\d+)/$', 'tournament_round', name='tournament_round'),
    #url(r'^(?P<slug>[\w_-]+)/playoff/$', 'tournament_playoff', name='tournament_playoff'),
    #url(r'^(?P<slug>[\w_-]+)/report/$', 'result_report', name='result_report'),
    #url(r'^(?P<slug>[\w_-]+)/join/$', 'join_tournament', name='join_tournament'),
    #url(r'^(?P<slug>[\w_-]+)/leave/$', 'leave_tournament', name='leave_tournament'),
)

for tournament in Tournament.objects.all():
    urlpatterns += patterns('',
        (r'^%s/' % tournament.slug,
         include(tournament.get_urls(), namespace=tournament.slug)),
    )
