from datetime import datetime
from random import randint

from django.conf.urls.defaults import patterns, url
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template

from nyxauth import NyxAuth

from tms.forms import PlayerProfileForm, ResultForm, ReplayForm
from tms.models import (OldTournament, Round, Match, PlayerProfile,
                        FastOldTournament, Competitor, Replay, Tournament,
                        Player)


def _configure_user(user):
    user.is_active = True
    user.is_staff = True
    user.save()
    user.groups.add(Group.objects.get(name='players'))
    return user


def index(request, template='tms/index.html'):

    #TODO: ...

    return HttpResponseRedirect(reverse('tms:nsl-season-4:index'))

    def player_info(t):
        if request.user.is_authenticated():
            player = request.user.get_profile()
            try:
                match = player.matches.filter(round=t.current_round)[0]
            except IndexError:
                pass
            else:
                match.opponent = (match.player1 if match.player2 == player
                                  else match.player2)
                t.player_match = match
        return t

    context = {
        'tournaments': {
            'ongoing': map(player_info, OldTournament.objects.ongoing()),
            'future': OldTournament.objects.future(),
            'past': FastOldTournament.objects.past(),
        },
        'newstyle_tournaments': Tournament.objects.all(),
    }
    return direct_to_template(request, template, context)


def registration(request, template='tms/registration.html'):
    """
    Displays registration form. After submitting :model:`auth.User` account is
    created along with a new :model:`tms.PlayerProfile` object.
    """
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST, prefix='user')
        player_form = PlayerProfileForm(request.POST, prefix='player')

        if user_form.is_valid() and player_form.is_valid():
            user = user_form.save(commit=False)
            user = _configure_user(user)

            credentials = {'username': user.username,
                           'password': user_form.cleaned_data['password1']}
            auth.login(request, auth.authenticate(**credentials))

            player = player_form.save(commit=False)
            player.user = user
            player.save()

            msg = _('Registration successfull. '
                    'You are now logged in as %s') % user.username
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('tms:index'))

    else:
        user_form = UserCreationForm(prefix='user')
        player_form = PlayerProfileForm(prefix='player')

    context = {
        'user_form': user_form,
        'player_form': player_form,
    }
    return direct_to_template(request, template, context)


def logout(request):
    auth.logout(request)
    messages.info(request, _('You have been logged out.'))
    return HttpResponseRedirect(reverse('tms:index'))


class TmsNyxAuth(NyxAuth):

    USER_SESSION_KEY = 'tms-nyx-auth-temp-user'

    def post_auth(self, request, user):
        try:
            PlayerProfile.objects.get(user=user)
        except PlayerProfile.DoesNotExist:
            request.session[TmsNyxAuth.USER_SESSION_KEY] = user
            return HttpResponseRedirect(reverse('tms:nyxauth:account_setup'))
        else:
            return super(TmsNyxAuth, self).post_auth(request, user)

    @transaction.commit_on_success
    def account_setup(self, request, template='tms/registration.html'):
        if request.method == 'POST':
            player_form = PlayerProfileForm(request.POST)

            if player_form.is_valid():
                user = request.session[TmsNyxAuth.USER_SESSION_KEY]
                user = _configure_user(user)
                user.save()

                player = player_form.save(commit=False)
                player.user = user
                player.from_nyx = True
                player.save()

                messages.success(request, _('Registration successfull.'))
                return super(TmsNyxAuth, self).post_auth(request, user)
        else:
            player_form = PlayerProfileForm()

        context = {
            'player_form': player_form,
        }
        return direct_to_template(request, template, context)

    def urls(self):
        return super(TmsNyxAuth, self).urls() + patterns('',
            url(r'^create-account/$', self.account_setup, name='account_setup'),
        )


class TournamentView(TemplateView):

    tournament = None

    @property
    def template_root(self):
        return self.tournament.template_root

    def dispatch(self, request, *args, **kwargs):
        self.tournament = Tournament.objects.get(pk=self.tournament.pk)
        kwargs['tournament'] = self.tournament
        return super(TournamentView, self).dispatch(request, *args, **kwargs)

    def get(self, request, tournament):
        return self.render_to_response({})

    def get_template_names(self):
        if self.template:
            return [self.template_root + self.template,
                    'tms/tournaments/' + self.template]
        else:
            return super(TournamentView, self).get_template_names()

    def render_to_response(self, context, **response_kwargs):
        context.update({
            'tournament': self.tournament,
            'current_view': self.__class__.__name__.lower(),
        })
        return (super(TournamentView, self)
                .render_to_response(context, **response_kwargs))


class LoginRequiredTournamentView(TournamentView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredTournamentView, self).dispatch(*args, **kwargs)


class tournament_view(object):
    def __init__(self, template):
        self.template = template

    def __call__(self, function):
        def wrapped(request, slug, **kwargs):
            tournament = get_object_or_404(OldTournament, slug=slug)
            result = function(request, tournament, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            context = result or {}
            context.update({
                'tournament': tournament,
                'current_view': function.__name__,
            })
            templates = [
                'tms/tournament/%s/%s' % (tournament.format_class, self.template),
                'tms/tournament/%s' % self.template,
            ]
            return render_to_response(templates, context,
                                      context_instance=RequestContext(request))
        return wrapped


@tournament_view(template='index.html')
def tournament(request, tournament): pass


@tournament_view(template='players.html')
def tournament_players(request, tournament): pass


@tournament_view(template='round.html')
def tournament_rounds(request, tournament):
    if tournament.current_round:

        #FIXME: after views refactoring
        if not (tournament.format_class == 'NyxLeague' and
                tournament.show_playoff() and
                tournament.current_round.type == Round.TYPE_SINGLE_ELIM):

            return HttpResponseRedirect(tournament.current_round.get_absolute_url())
    return {'selected_round': None}


@tournament_view(template='round.html')
def tournament_round(request, tournament, id=None):
    round = get_object_or_404(Round, tournament=tournament, id=id)

    #FIXME: after views refactoring
    if (tournament.format_class == 'NyxLeague' and tournament.show_playoff() and
        round.type == Round.TYPE_SINGLE_ELIM):
        return HttpResponseRedirect(reverse('tms:tournament_playoff',
                                            kwargs={'slug': tournament.slug}))

    return {'selected_round': round}


@tournament_view(template='playoff.html')
def tournament_playoff(request, tournament):
    rounds = tournament.rounds.filter(type=Round.TYPE_SINGLE_ELIM)
    if rounds:
        #FIXME: don't have a top16 bracket display yet...
        rounds = list(rounds)[-3:]
        player_count = 2 ** len(rounds)
        return {'rounds': rounds, 'player_count': player_count}


@login_required
@tournament_view(template='result_report.html')
def result_report(request, tournament):
    user = request.user
    player = user.get_profile()

    def fail_response(message, match=None):
        return {'message': message, 'match': match}

    if player not in tournament:
        return fail_response(_('You are not playing in this tournament!'))

    round = tournament.current_round
    if not round:
        return fail_response(_('No round is being played at the moment.'))

    try:
        match = round.matches.filter(Q(player1=player) | Q(player2=player))[0]
    except IndexError:
        return fail_response(_('You are not playing this round.'))

    if match.reported_by:
        return fail_response(_('Match result already reported by: %s') %
                             match.reported_by.username, match)

    if request.method == 'POST':
        form = ResultForm(request.POST, match=match)
        if form.is_valid():
            data = form.cleaned_data
            match.player1_score = data['player1_score']
            match.player2_score = data['player2_score']
            match.finished = True
            match.reported_by = user
            match.save()
            messages.success(request, _('Match result was saved.'))
            return HttpResponseRedirect(round.get_absolute_url())
    else:
        form = ResultForm(match=match)

    return {'form': form, 'match': match}


@login_required
@tournament_view(template='join.html')
def join_tournament(request, tournament):
    if not tournament.registration_open:
        return {'message': _('Registration closed.')}

    player = request.user.get_profile()

    if player in tournament:
        return {'message': _('You are already registered for this tournament.')}

    if request.method == 'POST':
        Competitor.objects.create(player=player, tournament=tournament)
        messages.success(request, _('You have joined %s!') % tournament.name)
        return HttpResponseRedirect(tournament.get_absolute_url())


class Join(LoginRequiredTournamentView):
    template = 'join.html'

    def get(self, request, tournament):
        self._validate_attempt(request, tournament)
        return self.render_to_response({})

    def post(self, request, tournament):
        if self._validate_attempt(request, tournament):
            Player.objects.create(user=request.user, node=tournament)
            messages.success(request, _('You have joined %s!') % tournament.name)
        return HttpResponseRedirect(tournament.get_absolute_url())

    def _validate_attempt(self, request, tournament):
        if not tournament.registration_open:
            messages.error(request, _('Registration closed.'))
            return False
        if request.user in tournament:
            messages.error(request, _('You are already registered '
                                      'for this tournament.'))
            return False
        return True


@login_required
@tournament_view(template='leave.html')
def leave_tournament(request, tournament):
    if not tournament.registration_open:
        return {'message': _('You cannot leave a tournament '
                             'after registration deadline.')}

    player = request.user.get_profile()

    if player not in tournament:
        return {'message': _('You are not registered for this tournament.')}

    if request.method == 'POST':
        Competitor.objects.get(player=player, tournament=tournament).delete()
        messages.success(request, _('You have left %s.') % tournament.name)
        return HttpResponseRedirect(reverse('tms:index'))


class Leave(LoginRequiredTournamentView):
    template = 'leave.html'

    def get(self, request, tournament):
        self._validate_attempt(request, tournament)
        return self.render_to_response({})

    def post(self, request, tournament):
        if self._validate_attempt(request, tournament):
            Player.objects.get(user=request.user, node=tournament.pk).delete()
            messages.success(request, _('You have left %s.') % tournament.name)
        return HttpResponseRedirect(reverse('tms:index'))

    def _validate_attempt(self, request, tournament):
        if not tournament.registration_open:
            messages.error(request, _('You cannot leave a tournament '
                                      'after registration deadline.'))
            return False
        if request.user not in tournament:
            messages.error(request, _('You are not registered '
                                      'for this tournament.'))
            return False
        return True


def player_profile(request, username, template='tms/player_profile.html'):
    player = get_object_or_404(PlayerProfile, user__username=username)

    def ongoing_info(tournament):
        return tournament, tournament.ranking.get_for_player(player)['rank']

    def past_info(tournament):
        for place, players in tournament.get_final_placing():
            if player in players:
                return tournament, place
        return tournament, None

    tournaments = {
        'ongoing': map(ongoing_info, player.tournament_set.ongoing()),
        'future': player.tournament_set.future(),
        'past': map(past_info, player.tournament_set.past()),
    }

    context = {'player': player, 'tournaments': tournaments}

    if request.is_ajax():
        # content for lightbox
        template = 'tms/includes/profile-content.html'

    return direct_to_template(request, template, context)


def match_replays(request, id, template='tms/match_replays.html'):
    match = get_object_or_404(Match, id=id)

    if request.is_ajax():
        template = 'tms/includes/replays-content.html'

    context = {
        'match': match,
        'session_key': request.session.session_key,
    }
    return direct_to_template(request, template, context)


@csrf_exempt
def upload_replay(request, id):
    session = SessionStore(session_key=request.POST.get('session_key'))
    user_id = session.get('_auth_user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            match = Match.objects.get(id=id)
        except ObjectDoesNotExist:
            HttpResponseBadRequest()
        form = ReplayForm(request.POST, request.FILES)
        if form.is_valid():
            replay = form.save(commit=False)
            replay.match = match
            replay.uploaded_by = user
            replay.save()
            return HttpResponse('ok')

    return HttpResponseForbidden()


@login_required
def delete_replay(request):
    if request.method != 'POST':
        return HttpResponseForbidden()

    try:
        id = int(request.POST.get('id') or '')
    except ValueError:
        return HttpResponseForbidden()

    try:
        replay = Replay.objects.get(id=id, uploaded_by=request.user)
    except Replay.DoesNotExist:
        return HttpResponseForbidden()

    replay.delete()
    return HttpResponse('ok')


def banner(request):
    max = 26
    url = '/site_media/img/banner/i%02d.jpg'
    number = (datetime.now().hour + datetime.now().day) % max
    return HttpResponseRedirect(url % number)


def status(request, template='tms/status.html'):
    """
    Simple status of ongoing tournaments.
    """
    context = {'ongoing_tournaments': OldTournament.objects.ongoing()}
    return direct_to_template(request, template, context)
