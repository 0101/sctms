from datetime import datetime, timedelta, time
from math import log

from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.utils.translation import ugettext as _

from tms.models import Round, Match, Rules


class __FormatLibrary(object):

    def __init__(self):
        self._registry = {}

    def register(self, cls):
        self._registry[cls.__name__] = {'class': cls, 'name': cls.name}

    def get(self, key):
        return self._registry[key]['class']

    def get_choices(self):
        return ((k, v['name']) for k, v in self._registry.items())

tournament_formats = __FormatLibrary()


class BaseTournamentFormat(object):

    def __init__(self, tournament):
        self.tournament = tournament

    @property
    def description(self):
        return self.__class__.__doc__

    @property
    def rules(self):
        try:
            return Rules.objects.get(format_class=self.__class__.__name__).text
        except Rules.DoesNotExist:
            return ''

    def create_rounds_if_possible(self):
        """
        Generates rounds for the tournament if registration is already closed.
        """
        if self.tournament.registration_deadline < datetime.now():
            try:
                self._create_rounds()
            except AttributeError:
                pass


class NyxLeague(BaseTournamentFormat):
    """
    A two-stage tournament. 6 rounds of a swiss-system tournament, followed by
    a single-elimination playoff for top [2^(round(log2(registered players))) / 4] players.
    """
    name = _('Nyx League')

    swiss_round_count = 6
    swiss_round_length = 5 # days
    playoff_length = 7 # days

    @transaction.commit_on_success
    def _create_rounds(self):
        assert self.tournament.round_set.count() == 0, 'rounds already exist'

        self._create_rounds_swiss()
        self._create_rounds_playoff()

    def _create_rounds_swiss(self):
        start_date = self.tournament.registration_deadline.date() + timedelta(1)
        # the day after registration deadline at 0:00
        start = datetime.combine(start_date, time())

        for i in range(self.swiss_round_count):
            length = self.swiss_round_length
            # every round should contain at least one weekend-day
            while start.weekday() + length < 6:
                length += 1
            end = start + timedelta(length)
            Round.objects.create(
                tournament=self.tournament,
                start=start,
                end=(end - timedelta(seconds=1)),
                type=(Round.TYPE_RANDOM if i == 0 else Round.TYPE_SWISS),
                bo=3,
            )
            start = end

    def _create_rounds_playoff(self):
        player_count = self.tournament.players.count()
        playoff_player_count = 2 ** (round(log(player_count, 2))) / 4
        playoff_round_count = int(log(playoff_player_count, 2))

        start = self.tournament.last_round.end
        end = start + timedelta(self.playoff_length)

        for i in range(playoff_round_count):
            Round.objects.create(
                tournament=self.tournament,
                type=Round.TYPE_SINGLE_ELIM,
                start=(start if i == 0 else None),
                end=end,
                bo=(7 if i == playoff_round_count - 1 else 5),
                description=(_('Finals') if i == playoff_round_count - 1 else
                             _('Round of %s') % (2 ** (playoff_round_count - i))),
            )

    def get_final_placing(self, limit=3):
        ranking = self.tournament.ranking
        ranking.sort_by('playoff_wins')

        place = 1
        wins = ranking[0]['playoff_wins']
        group = [ranking[0]['player']]
        for item in ranking[1:]:
            if item['playoff_wins'] == wins:
                group.append(item['player'])
            else:
                yield place, group
                place += 1
                if limit and place > limit:
                    break
                group = [item['player']]
                wins = item['playoff_wins']


class DoubleEliminationTournament(BaseTournamentFormat):
    """
    Double elimination tournament, winners bracket, losers bracket and all
    that good jazz.
    """
    name = _('Double Elimination Tournament')

    def get_final_placing(self, limit=4):
        rounds = self.tournament.rounds
        try:
            final = Match.objects.get(round__in=rounds,
                                      round__type=Round.TYPE_DOUBLE_ELIM_FIN)
        except MultipleObjectsReturned:
            # TODO: logging
            print '%s has multiple Grand Final matches!' % self.tournament
            return
        except Match.DoesNotExist:
            return

        yield 1, [final.winner]
        if limit == 1: return
        yield 2, [final.loser]
        if limit == 2: return

        lb = rounds.filter(type=Round.TYPE_DOUBLE_ELIM_LB).order_by('-order')
        try:
            yield 3, [lb[0].match_set.all()[0].loser]
            if limit == 3: return
            yield 4, [lb[1].match_set.all()[0].loser]
        except IndexError:
            return


tournament_formats.register(NyxLeague)
tournament_formats.register(DoubleEliminationTournament)
