from datetime import date, datetime, timedelta
from random import randint

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import timeuntil, timesince, slugify

from django_extensions.db.fields import AutoSlugField

from tms.cachecontrol import CacheNotifierModel, bind_clear_cache, ClearCacheMixin, SAVE
from tms.managers import TournamentManager
from tms.utils import cached, invalidate_template_cache, odd, split, merge


class Player(models.Model):
    user = models.ForeignKey(User, unique=True)
    character_name = models.CharField(max_length=50)
    character_code = models.PositiveSmallIntegerField()
    bnet_url = models.URLField(null=True, blank=True)
    contact = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _('Player')
        verbose_name_plural = _('Players')
        unique_together = 'character_name', 'character_code'
        ordering = 'character_name',

    def __unicode__(self):
        return self.character_name

    @property
    def matches(self):
        return Match.objects.filter(Q(player1=self) | Q(player2=self))

    def matches_in(self, tournament):
        return self.matches.filter(round__tournament=tournament)

    def get_absolute_url(self):
        return reverse('tms:player_profile',
                       kwargs={'username': self.user.username})

    def get_stats(self):
        return PlayerStats(self)


class Map(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _(u'Map')
        verbose_name_plural = _(u'Maps')

    def __unicode__(self):
        return self.name


class PlayerRanking(object):

    def __init__(self, tournament):
        self.tournament = tournament
        self.players = []
        self.player_dict = {}
        for player in tournament.players.order_by('user__username'):
            player_data = {'player': player}
            # get user from db, so that it gets cached
            player.user
            self.players.append(player_data)
            self.player_dict[player] = player_data

    def __contains__(self, player):
        return player in self.player_dict

    def __getitem__(self, index):
        return self.players.__getitem__(index)

    def __iter__(self):
        return self.players.__iter__()

    def field(self, function):
        """
        Adds a field (column) to the ranking table. Can be used as decorator.
        """
        for row in self.players:
            field = function.__name__
            player = row['player']
            row[field] = function(player, self.tournament, self.player_dict)

    def get_for_player(self, player):
        return self.player_dict[player]

    def sort_by(self, *fields):
        self.players.sort(key=lambda r: [r.get(f) for f in fields], reverse=True)
        for i in range(len(self.players)):
            self.players[i]['rank'] = i + 1


class PlayerStats(object):

    def __init__(self, player):
        self.player = player

    def rank(self):
        # TODO: ugh...
        r = 0
        for tournament in self.player.tournament_set.all():
            for place, players in tournament.get_final_placing(limit=3):
                if self.player in players:
                    if place == 1:
                        r = r + 1 if r >= 3 else 3
                    else:
                        r = (4 - place) if (4 - place) > r else r
        return r


class Tournament(CacheNotifierModel, ClearCacheMixin):
    name = models.CharField(max_length=50, unique=True)
    slug = AutoSlugField(populate_from='name')
    registration_deadline = models.DateTimeField(blank=True, help_text='Defaults to a week from today')
    additional_information = models.TextField(blank=True)
    players = models.ManyToManyField(Player, blank=True)
    map_pool = models.ManyToManyField(Map, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True)
    format_class = models.CharField(_('Format'), max_length=50)

    objects = TournamentManager()

    class Meta:
        verbose_name = _(u'Tournament')
        verbose_name_plural = _(u'Tournaments')

    def __unicode__(self):
        return self.name

    def __contains__(self, player):
        return self.players.filter(id=player.id).count() != 0

    def _create_ranking(self):
        ranking = PlayerRanking(self)

        @ranking.field
        def wins(player, tournament, data):
            return player.matches_in(tournament).filter(winner=player).count()

        @ranking.field
        def match_count(player, tournament, data):
            return player.matches_in(tournament).filter(finished=True).count()

        @ranking.field
        def win_ratio(player, tournament, data):
            match_count = data[player]['match_count']
            win_count = data[player]['wins']
            return (float(win_count) / match_count) if match_count else None

        @ranking.field
        def win_percent(player, tournament, data):
            wr = data[player]['win_ratio']
            return '%.0f' % (wr * 100) if wr is not None else 'N/A'

        @ranking.field
        def losses(player, tournament, data):
            return player.matches_in(tournament).filter(loser=player).count()

        @ranking.field
        def loss_ratio(player, tournament, data):
            match_count = data[player]['match_count']
            loss_count = data[player]['losses']
            return (float(loss_count) / match_count) if match_count else None

        @ranking.field
        def loss_percent(player, tournament, data):
            lr = data[player]['loss_ratio']
            return '%.0f' % (lr * 100) if lr is not None else 'N/A'

        @ranking.field
        def points(player, tournament, data):
            return data[player]['wins'] * 3

        @ranking.field
        def won_against(player, tournament, data):
            players = Player.objects.filter(id__in=(
                player.matches_in(tournament).filter(winner=player).values('loser')
            ))
            return [data[p] for p in players]

        @ranking.field
        def lost_against(player, tournament, data):
            players = Player.objects.filter(id__in=(
                player.matches_in(tournament).filter(loser=player).values('winner')
            ))
            return [data[p] for p in players]

        @ranking.field
        def played_against(player, tournament, data):
            p = data[player]
            players = set(
                [pd['player'] for pd in p['won_against'] + p['lost_against']]
            )
            return [data[p] for p in players]

        @ranking.field
        def buchholz(player, tournament, data):
            return sum([pd['points'] for pd in data[player]['played_against']])

        @ranking.field
        def games_won(player, tournament, data):
            s = (player.match_player1.filter(round__tournament=tournament)
                 .aggregate(s=Sum('player1_score'))['s'] or 0)
            s += (player.match_player2.filter(round__tournament=tournament)
                  .aggregate(s=Sum('player2_score'))['s'] or 0)
            return s

        @ranking.field
        def games_lost(player, tournament, data):
            s = (player.match_player1.filter(round__tournament=tournament)
                 .aggregate(s=Sum('player2_score'))['s'] or 0)
            s += (player.match_player2.filter(round__tournament=tournament)
                  .aggregate(s=Sum('player1_score'))['s'] or 0)
            return s

        @ranking.field
        def score(player, tournament, data):
            return data[player]['games_won'] - data[player]['games_lost']

        @ranking.field
        def playoff_wins(player, tournament, data):
            lookup = {'round__tournament': tournament,
                      'round__type__in': Round.TYPES_PLAYOFF}
            return player.won_matches.filter(**lookup).count()

        ranking.sort_by('playoff_wins',
                        'points',
                        'buchholz',
                        'score',
                        'games_won')
        return ranking

    def _get_ranking_cache_key(self):
        return 'tournament-ranking-%s' % self.pk

    @property
    @cached
    def format(self):
        return tournament_formats.get(self.format_class)(self)

    @property
    @cached
    def current_round(self):
        try:
            now = datetime.now()
            return self.rounds.filter(start__lte=now, end__gt=now)[0]
        except IndexError:
            return None

    @property
    @cached
    def last_round(self):
        try:
            return self.round_set.order_by('-end')[0]
        except IndexError:
            return None

    @property
    def ranking(self):
        key = self._get_ranking_cache_key()
        ranking = cache.get(key)
        if not ranking:
            ranking = self._create_ranking()
            cache.set(key, ranking)
        return ranking

    @property
    def registration_open(self):
        return self.registration_deadline > datetime.now()

    @property
    def rounds(self):
        if self.round_set.count() == 0:
            if not getattr(self, '_rounds_recursion_check', False):
                self._rounds_recursion_check = True
                self.format.create_rounds_if_possible()
                self._rounds_recursion_check = False
        return self.round_set.order_by('order')

    def clear_ranking_cache(self):
        cache.delete(self._get_ranking_cache_key())
        invalidate_template_cache('players', self.id)

    def get_absolute_url(self):
        return reverse('tms:tournament', kwargs={'slug': self.slug})

    def get_final_placing(self, *args, **kwargs):
        return self.format.get_final_placing(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.registration_deadline:
            self.registration_deadline = date.today() + timedelta(7)
        super(Tournament, self).save(*args, **kwargs)

    @classmethod
    def clear_cache_tournament(cls, tournament, action):
        tournament.clear_ranking_cache()

    @classmethod
    def clear_cache_round(cls, round, action):
        round.tournament.clear_ranking_cache()

    @classmethod
    def clear_cache_match(cls, match, action):
        match.round.tournament.clear_ranking_cache()


class FastTournament(Tournament):
    """
    Tournament model proxy which only creates limited version of ranking.

    Primarily used for faster homepage load times with empty cache.
    """
    class Meta:
        proxy = True

    def _create_ranking(self):
        """
        Creates simplified version of ranking
        """
        ranking = PlayerRanking(self)

        @ranking.field
        def playoff_wins(player, tournament, data):
            lookup = {'round__tournament': tournament,
                      'round__type__in': Round.TYPES_PLAYOFF}
            return player.won_matches.filter(**lookup).count()

        ranking.sort_by('playoff_wins')
        return ranking

    def _get_ranking_cache_key(self):
        return 'fast-tournament-ranking-%s' % self.pk

    @property
    def ranking(self):
        """
        Returns ragular ranking if it's already created. Otherwise returns
        limited version which is faster to create.
        """
        full_ranking_key = Tournament._get_ranking_cache_key(self)
        full_ranking = cache.get(full_ranking_key)
        return full_ranking or super(FastTournament, self).ranking


class Round(CacheNotifierModel, ClearCacheMixin):
    TYPE_RANDOM = 'random'
    TYPE_SWISS = 'swiss'
    TYPE_ROBIN = 'round_robin'
    TYPE_SINGLE_ELIM = 'single_elimination'
    TYPE_DOUBLE_ELIM_WB = 'double_elimination_wb'
    TYPE_DOUBLE_ELIM_LB = 'double_elimination_lb'
    TYPE_DOUBLE_ELIM_FIN = 'double_elimination_fin'
    # TODO: remove:
    TYPES_PLAYOFF = (
        TYPE_SINGLE_ELIM,
    )
    TYPE_CHOICES = (
        (TYPE_RANDOM, _('Random pairs')),
        (TYPE_SWISS, _('Swiss system')),
        (TYPE_ROBIN, _('Round-robin')),
        (TYPE_SINGLE_ELIM, _('Single elimination')),
        (TYPE_DOUBLE_ELIM_WB, _('Double elimination - Winners bracket')),
        (TYPE_DOUBLE_ELIM_LB, _('Double elimination - Losers bracket')),
        (TYPE_DOUBLE_ELIM_FIN, _('Double elimination - Final')),
    )
    STATUS_NOT_STARTED = 'not_yet_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_OVER = 'over'
    tournament = models.ForeignKey(Tournament)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    bo = models.PositiveSmallIntegerField(default=3)
    first_map = models.ForeignKey(Map, null=True, blank=True)
    description = models.CharField(max_length=50, blank=True)
    type = models.SlugField(choices=TYPE_CHOICES)
    order = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _(u'Round')
        verbose_name_plural = _(u'Rounds')

    def __unicode__(self):
        return self.description

    @property
    def all_finished(self):
        return self.match_set.filter(finished=False).count() == 0

    @property
    @cached
    def index(self):
        if self.id:
            id_list = list(zip(*self.tournament.rounds.values_list('id'))[0])
            return id_list.index(self.id) + 1
        else:
            return self.tournament.rounds.count() + 1

    @property
    @cached
    def matches(self):
        """
        Returns this round's matches.
        If they are not definded, generates them if possible.
        """
        if self.match_set.count() == 0:
            MatchMaker().create_matches_if_possible(self)

        return self.match_set.all()

    @property
    def status(self):
        now = datetime.now()
        if self.start >= now or not self.start:
            return Round.STATUS_NOT_STARTED
        if self.end < now:
            return Round.STATUS_OVER
        return Round.STATUS_IN_PROGRESS

    @property
    @cached
    def previous_round(self):
        try:
            return (self.tournament.round_set.order_by('-order')
                    .filter(order__lt=self.order)[0])
        except IndexError:
            return None

    @property
    @cached
    def next_round(self):
        try:
            return (self.tournament.round_set.order_by('order')
                    .filter(order__gt=self.order)[0])
        except IndexError:
            return None

    def clear_template_cache(self):
        invalidate_template_cache('rounds', self.tournament.id, self)

    def get_absolute_url(self):
        return reverse('tms:tournament_round',
            kwargs={'slug': self.tournament.slug, 'id': self.id})

    def is_in_progress(self):
        return self.status == Round.STATUS_IN_PROGRESS

    def is_not_yet_started(self):
        return self.status == Round.STATUS_NOT_STARTED

    def is_over(self):
        return self.status == Round.STATUS_OVER

    def save(self, *args, **kwargs):
        self.description = self.description or _('Round %s') % self.index
        self.order = self.order or self.index
        super(Round, self).save(*args, **kwargs)

    def start_next_if_possible(self):
        """
        Checks if this round ended ahead of schedule and starts the next one
        if it is the case. Assuming this round is currently in progress.
        """
        if not (self.is_in_progress() and self.all_finished and self.next_round):
            return

        self.end = self.next_round.start = datetime.now()
        self.save()
        self.next_round.save()

    def time_info(self):
        if self.previous_round and not self.start:
            return _('starts when %s is finished') % self.previous_round
        if self.is_not_yet_started():
            return _('starts in %s') % timeuntil(self.start)
        if self.is_in_progress():
            return _('ends in %s') % timeuntil(self.end)
        return _('ended %s ago') % timesince(self.end)

    @classmethod
    def clear_cache_round(cls, round, action):
        round.clear_template_cache()
        invalidate_template_cache('rounds', round.tournament.id, None)

    @classmethod
    def clear_cache_match(cls, match, action):
        match.round.clear_template_cache()

    @classmethod
    def clear_cache_replay(cls, replay, action):
        replay.match.round.clear_template_cache()


class MatchMaker(object):

    def create_matches_if_possible(self, round):
        if getattr(self, 'can_make_' + round.type, lambda *a: True)(round):
            self.create_matches(round)

    def is_previous_round_over(self, round):
        if round.previous_round:
            return round.previous_round.end < datetime.now()
        else:
            return True

    def is_registration_closed(self, round):
        return not round.tournament.registration_open

    def reg_closed_and_previous_over(self, round):
        return (self.is_registration_closed(round) and
                self.is_previous_round_over(round))

    can_make_random = is_registration_closed
    can_make_swiss = reg_closed_and_previous_over
    can_make_single_elimination = reg_closed_and_previous_over
    can_make_double_elimination = reg_closed_and_previous_over

    def create_matches(self, round):
        # if there already are some matches, something's probably wrong
        assert round.match_set.count() == 0, ('Trying to create matches when '
                                              'some already exist.')

        make_pairs = getattr(self, 'make_pairs_' + round.type, lambda *a: ())

        for p1, p2 in make_pairs(round, list(round.tournament.ranking)):
            Match.objects.create(
                round=round,
                player1=p1['player'],
                player2=p2['player'],
            )

    def make_pairs_random(self, round, ranking):
        pop_random = lambda x: x.pop(randint(0, len(x) - 1))
        while len(ranking) > 1:
            yield pop_random(ranking), pop_random(ranking)


    def make_pairs_swiss(self, round, ranking):
        if odd(ranking):
            #TODO: ensure the same player doesn't get popped in multiple rounds
            ranking.pop(randint(0, len(ranking) - 1))

        group = []
        pairs = []
        points = ranking[0]['points']

        def pair(group):
            assert not odd(group)
            half = len(group) / 2
            return zip(group[:half], group[half:])

        for player in ranking:
            if player['points'] == points or odd(group):
                group.append(player)
            else:
                pairs += pair(group)
                group = [player]
                points = player['points']
        pairs += pair(group)

        #TODO: check players don't get opponents they already played with
        return pairs

    def make_pairs_single_elimination(self, round, ranking):
        previous_round = round.previous_round

        if previous_round and previous_round.type == Round.TYPE_SINGLE_ELIM:
            previous_winners = [m.winner for m in previous_round.matches]
            # this is expected to return items from ranking...
            players = [{'player': p} for p in previous_winners]
            if odd(players):
                # something's wrong, abort
                return []
            return split(players, 2)
        else:
            playoff_rounds_count = (round.tournament.rounds
                                    .filter(type=Round.TYPE_SINGLE_ELIM)
                                    .count())
            player_count = 2 ** playoff_rounds_count
            players = ranking[:player_count]
            half = player_count / 2
            pairs = zip(players[:half], reversed(players[half:]))

            for i in range(1, playoff_rounds_count - 1):
                half = len(pairs) / 2 / i
                pairs = merge(merge(map(
                    lambda x, y: [x, y],
                    split(pairs, i)[:half],
                    reversed(split(pairs, i)[half:])
                )))
            return pairs


class Match(CacheNotifierModel):
    round = models.ForeignKey(Round)
    player1 = models.ForeignKey(Player, related_name='match_player1')
    player2 = models.ForeignKey(Player, related_name='match_player2')
    player1_score = models.PositiveSmallIntegerField(default=0)
    player2_score = models.PositiveSmallIntegerField(default=0)
    finished = models.BooleanField()
    reported_by = models.ForeignKey(User, null=True, blank=True)
    winner = models.ForeignKey(Player, null=True, blank=True, editable=False,
                               related_name='won_matches')
    loser = models.ForeignKey(Player, null=True, blank=True, editable=False,
                              related_name='lost_matches')

    class Meta:
        verbose_name = _(u'Match')
        verbose_name_plural = _(u'Matches')

    def __unicode__(self):
        return "%s %s:%s %s" % (self.player1, self.player1_score,
                                self.player2_score, self.player2)

    def __contains__(self, player):
        return player == self.player1 or player == self.player2

    @property
    @cached
    def replays(self):
        return self.replay_set.all()

    def save(self, *args, **kwargs):
        if self.finished and self.player1_score != self.player2_score:
            self.winner = (self.player1 if self.player1_score >
                           self.player2_score else self.player2)
            self.loser = (self.player1 if self.player2 == self.winner
                          else self.player2)
        else:
            self.winner = None
            self.loser = None
        super(Match, self).save(*args, **kwargs)
        self.round.start_next_if_possible()


def replay_upload_path(instance, filename):
    match = instance.match
    return u'replays/%s/%s/%s-%s/%s' % (
        slugify(match.round.tournament),
        slugify(match.round),
        match.player1.user,
        match.player2.user,
        filename,
    )

class Replay(CacheNotifierModel):
    file = models.FileField(upload_to=replay_upload_path, max_length=512)
    match = models.ForeignKey(Match)
    map = models.ForeignKey(Map, null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _(u'Replay')
        verbose_name_plural = _(u'Replays')

    def __unicode__(self):
        return self.file.name.split('/')[-1]

    @property
    def player1(self):
        return self.match.player1

    @property
    def player2(self):
        return self.match.player2

    @property
    @cached
    def round(self):
        return self.match.round

    @property
    def tournament(self):
        return self.round.tournament


bind_clear_cache(Round)
bind_clear_cache(Tournament)


from tms.tournaments import tournament_formats
