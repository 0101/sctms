from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum

from tms.models import TournamentNode, Tournament, node_link, Match
from tms.utils import cached

from tms.tour.nsl_v1 import views


class Ranking(object):

    def __init__(self, player_list, node):
        self.players = list(player_list)
        self.player_dict = dict([(p.user_id, p) for p in self.players])
        self.node = node

    def field(self, fn):
        for player in self.players:
            name = fn.__name__
            fn_val = fn(player, self.player_dict, self.node)
            extra = player.get('extra_' + name)
            value = fn_val + extra if extra else fn_val
            setattr(player, name, value)

    def sort(self, cmp):
        self.players.sort(cmp=cmp)
        self._add_rank()

    def _add_rank(self):
        for i, player in enumerate(self.players):
            player.rank = i + 1

    def save(self):
        for p in self.players:
            p.save()


class SwissSystem(TournamentNode):

    class Meta:
        proxy = True

    @property
    def rounds(self):
        return self.round_set.all()

    @property
    @cached
    def matches(self):
        return Match.objects.filter(round__parent_node=self)

    def get_round_url(self, round):
        return self.get_root().get_url('round', kwargs={'id': round.id})

    def _create_ranking(self):
        ranking = Ranking(self.player_set.all(), self)

        @ranking.field
        def wins(player, player_dict, node):
            return node.matches.filter(winner=player.user).count()

        @ranking.field
        def match_count(player, player_dict, node):
            return (node.matches
                    .filter(Q(player1=player.user)|Q(player2=player.user))
                    .filter(finished=True).count())

        @ranking.field
        def win_ratio(player, player_dict, node):
            return ((float(player.wins) / player.match_count)
                    if player.match_count else None)

        @ranking.field
        def win_percent(player, player_dict, node):
            return ('%.0f' % (player.win_ratio * 100)
                    if player.win_ratio is not None else 'N/A')

        @ranking.field
        def losses(player, player_dict, node):
            return node.matches.filter(loser=player.user).count()

        @ranking.field
        def loss_ratio(player, player_dict, node):
            return ((float(player.losses) / player.match_count)
                    if player.match_count else None)

        @ranking.field
        def loss_percent(player, player_dict, node):
            return ('%.0f' % (player.loss_ratio * 100)
                    if player.loss_ratio is not None else 'N/A')

        @ranking.field
        def points(player, player_dict, node):
            return player.wins * 3

        @ranking.field
        def won_against(player, player_dict, node):
            return [x['loser'] for x in
                    node.matches.filter(winner=player.user).values('loser')]

        @ranking.field
        def lost_against(player, player_dict, node):
            return [x['winner'] for x in
                    node.matches.filter(loser=player.user).values('winner')]

        @ranking.field
        def played_against(player, player_dict, node):
            return player.lost_against + player.won_against

        @ranking.field
        def buchholz(player, player_dict, node):
            return sum([player_dict[p].points for p in player.played_against])

        @ranking.field
        def games_won(player, player_dict, node):
            s = (node.matches.filter(player1=player.user)
                 .aggregate(s=Sum('player1_score'))['s'] or 0)
            s += (node.matches.filter(player2=player.user)
                 .aggregate(s=Sum('player2_score'))['s'] or 0)
            return s

        @ranking.field
        def games_lost(player, player_dict, node):
            s = (node.matches.filter(player1=player.user)
                 .aggregate(s=Sum('player2_score'))['s'] or 0)
            s += (node.matches.filter(player2=player.user)
                 .aggregate(s=Sum('player1_score'))['s'] or 0)
            return s

        @ranking.field
        def score(player, player_dict, node):
            return player.games_won - player.games_lost

        def compare(x, y):
            cmp = (
                (y.points - x.points) or
                (y.buchholz - x.buchholz) or
                (y.score - x.score)
            )
            if cmp == 0:
                if x.user_id in y.won_against:
                    return 1
                if y.user_id in x.won_against:
                    return -1
            return cmp

        ranking.sort(compare)
        ranking.save()


class Playoff(TournamentNode):

    class Meta:
        proxy = True

    @property
    def rounds(self):
        return self.round_set.all()


class NSL(Tournament):

    template_root = 'tms/tournaments/nsl_v1/'
    base_template = template_root + 'base.html'

    swiss = node_link(SwissSystem)
    playoff = node_link(Playoff)

    class Meta:
        proxy = True
        verbose_name = 'NSL Season'

    def get_urls(self):

        # initial keyword args for all views
        kw = {'tournament': self}

        return patterns('',
            url(r'^$', views.Index.as_view(**kw), name='index'),
            url(r'^info$', views.Info.as_view(**kw), name='info'),
            url(r'^players$', views.Players.as_view(**kw), name='players'),
            url(r'^rounds$', views.SwissRounds.as_view(**kw), name='rounds'),
            url(r'^round/(?P<id>\d+)$', views.SwissRound.as_view(**kw), name='round'),
            url(r'^playoff$', views.Playoff.as_view(**kw), name='playoff'),
        )
