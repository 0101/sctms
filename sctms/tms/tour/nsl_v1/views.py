from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import View, TemplateView

from tms.views import TournamentView
from tms.models import Round


class Index(TournamentView):

    def get(self, request, tournament):
        return HttpResponseRedirect(tournament.get_url('playoff'))


class Info(TournamentView):
    template = 'info.html'


class Players(TournamentView):
    template = 'players.html'


class SwissRounds(TournamentView):
    template = 'round.html'

    def get(self, request, tournament):
        if tournament.current_round:
            return HttpResponseRedirect(tournament.current_round
                                        .get_absolute_url())
        return self.render_to_response({'selected_round': None})


class SwissRound(TournamentView):
    template = 'round.html'

    def get(self, request, tournament, id=None):
        round = get_object_or_404(Round, parent_node=tournament.swiss, id=id)
        return self.render_to_response({'selected_round': round})


class Playoff(TournamentView):
    template = 'playoff.html'

    def get(self, request, tournament):
        rounds = tournament.playoff.rounds
        context = {}
        if rounds:
            #FIXME: don't have a top16 bracket display yet...
            rounds = list(list(rounds)[-3:])
            context['rounds'] = rounds
            context['player_count'] = 2 ** len(rounds)

        return self.render_to_response(context)
