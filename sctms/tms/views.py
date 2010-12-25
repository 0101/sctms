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
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template

from nyxauth import NyxAuth

from tms.cachecontrol import cache_control
from tms.forms import PlayerForm, ResultForm, ReplayForm
from tms.models import Tournament, Round, Match, PlayerRanking, Player, FastTournament


def _configure_user(user):
    user.is_active = True
    user.is_staff = True
    user.save()
    user.groups.add(Group.objects.get(name='players'))
    return user


def index(request, template='tms/index.html'):
    context = {'tournaments': Tournament.objects,
               'tournaments_fast': FastTournament.objects}
    return direct_to_template(request, template, context)


def registration(request, template='tms/registration.html'):
    """
    Displays registration form. After submitting :model:`auth.User` account is
    created along with a new :model:`tms.Player` object.
    """
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST, prefix='user')
        player_form = PlayerForm(request.POST, prefix='player')

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
        player_form = PlayerForm(prefix='player')

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
            Player.objects.get(user=user)
        except Player.DoesNotExist:
            request.session[TmsNyxAuth.USER_SESSION_KEY] = user
            return HttpResponseRedirect(reverse('tms:nyxauth:account_setup'))
        else:
            return super(TmsNyxAuth, self).post_auth(request, user)

    @transaction.commit_on_success
    def account_setup(self, request, template='tms/registration.html'):
        if request.method == 'POST':
            player_form = PlayerForm(request.POST)

            if player_form.is_valid():
                user = request.session[TmsNyxAuth.USER_SESSION_KEY]
                user = _configure_user(user)
                user.save()

                player = player_form.save(commit=False)
                player.user = user
                player.save()

                messages.success(request, _('Registration successfull.'))
                return super(TmsNyxAuth, self).post_auth(request, user)
        else:
            player_form = PlayerForm()

        context = {
            'player_form': player_form,
        }
        return direct_to_template(request, template, context)

    def urls(self):
        return super(TmsNyxAuth, self).urls() + patterns('',
            url(r'^create-account/$', self.account_setup, name='account_setup'),
        )


class tournament_view(object):
    def __init__(self, template):
        self.template = template

    def __call__(self, function):
        def wrapped(request, slug, **kwargs):
            tournament = get_object_or_404(Tournament, slug=slug)
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
        return HttpResponseRedirect(tournament.current_round.get_absolute_url())
    return {'selected_round': None}


@tournament_view(template='round.html')
def tournament_round(request, tournament, id=None):
    round = get_object_or_404(Round, tournament=tournament, id=id)
    return {'selected_round': round}


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
        tournament.players.add(player)
        cache_control.trigger(tournament, 'player_add')
        messages.success(request, _('You have joined %s!') % tournament.name)
        return HttpResponseRedirect(tournament.get_absolute_url())


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
        tournament.players.remove(player)
        cache_control.trigger(tournament, 'player_remove')
        messages.success(request, _('You have left %s.') % tournament.name)
        return HttpResponseRedirect(reverse('tms:index'))


def player_profile(request, username, template='tms/player_profile.html'):
    player = get_object_or_404(Player, user__username=username)

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
            replay.save()
            return HttpResponse('ok')

    return HttpResponseForbidden()
