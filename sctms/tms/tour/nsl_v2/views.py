from django.http import HttpResponseRedirect

from tms.views import TournamentView, Join, Leave


class Index(TournamentView):
    """
    Landing URL of the tournament, should redirect to a page appropriate for
    current time and user.
    """

    def get(self, request, tournament):
        return HttpResponseRedirect(tournament.get_url('info'))


class Info(TournamentView):
    template = 'info.html'


class Players(TournamentView):
    template = 'players.html'
