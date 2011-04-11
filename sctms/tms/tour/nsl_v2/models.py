"""
Nyx StarCraft League V2

NSL Season ------------ NSL
    Code S ------------ CodeS
        Group Stage --- GroupStage
            Group A --- RoundRobinGroup
            Group B ///
            Group C //
            Group D /
        Playoff ------- SingleEliminationBracket
        Second Chance - GroupStage
            Group A --- RoundRobinGroup
            Group B /
    Code A ------------ CodeA
        Group Stage --- GroupStage
            Group A --- RoundRobinGroup
            Group B ///
            Group C //
            Group D /
        Playoff ------- SingleEliminationBracket
        Potato King --- SingleEliminationBracket
    Up/Down ----------- UpDown
        Group A ------- RoundRobinGroup
        Group B ///
        Group C //
        Group D /

"""

from django.conf.urls.defaults import patterns, url
from django.db import models

from tms.models import TournamentNode, Tournament
from tms.tour.nsl_v2 import views


class NSL(Tournament):

    template_root = 'tms/tournaments/nsl_v2/'
    base_template = template_root + 'base.html'

    class Meta:
        proxy = True
        verbose_name = 'NSL Season'

    def get_urls(self):

        # initial keyword args for all views
        kw = {'tournament': self}

        return patterns('',
            url(r'^$', views.Index.as_view(**kw), name='index'),
            url(r'^info$', views.Info.as_view(**kw), name='info'),
            url(r'^join$', views.Join.as_view(**kw), name='join'),
            url(r'^leave$', views.Leave.as_view(**kw), name='leave'),
            url(r'^players$', views.Players.as_view(**kw), name='players'),
        )


class CodeS(TournamentNode):

    class Meta:
        proxy = True


class CodeA(TournamentNode):

    class Meta:
        proxy = True


class UpDown(TournamentNode):

    class Meta:
        proxy = True


class GroupStage(TournamentNode):

    class Meta:
        proxy = True


class RoundRobinGroup(TournamentNode):

    class Meta:
        proxy = True


class SingleEliminationBracket(TournamentNode):

    class Meta:
        proxy = True
