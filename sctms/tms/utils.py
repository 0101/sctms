from random import randint
import sys

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import clear_url_caches
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote


def cached(func):
    """Decorator that caches function's return value on given object"""
    def wrapped(object, *args):
        cache_attr = '_cached_%s' % func.__name__
        if not hasattr(object, cache_attr):
            setattr(object, cache_attr, {})
        cache = getattr(object, cache_attr)
        try:
            return cache[args]
        except KeyError:
            cache[args] = value = func(object, *args)
            return value
        except TypeError:
            return func(*args)
    return wrapped


def is_manager(user):
    if not user.is_authenticated():
        return False
    try:
        user.groups.get(name='managers')
    except ObjectDoesNotExist:
        return False
    else:
        return True


def invalidate_template_cache(fragment_name, *variables):
    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)


def reload_url_patterns():
    from tms import urls as tms_urls
    reload(tms_urls)
    # TODO: reload ROOT_URLCONF
    clear_url_caches()


def odd(x):
    "Returns whether the length of x is odd"
    return len(x) % 2 == 1


def split(sequence, size):
    "Splits the squence into chunks of given size"
    return [sequence[i:i+size] for i in range(0, len(sequence), size)]


def merge(x):
    "Merges a sequence of lists into one list"
    return sum(x, [])


def pop_random(x):
    return x.pop(randint(0, len(x) - 1))


def do_nothing(*args, **kwargs):
    pass


def is_valid_pairing(pairing):
    " returns if no pair played against each other before "
    for p1, p2 in pairing:
        if p2['player'] in p1['played_against']:
            return False
    return True


def import_players():
    from django.contrib.auth.models import User
    from tms.models import PlayerProfile
    from tms.views import _configure_user

    data="""MARTYMARTY,http://eu.battle.net/sc2/en/profile/210242/1/marty/,marty,249
SAVANNAH,http://eu.battle.net/sc2/en/profile/202925/1/Savannah/,Savannah,765
JANDOS,http://eu.battle.net/sc2/en/profile/204174/1/Jandos/,Jandos,213
KULHY,http://eu.battle.net/sc2/en/profile/806297/1/StarCore/,StarCore,403
MCKIDNEY,http://eu.battle.net/sc2/en/profile/212958/1/mcKidney/,mcKidney,154
ARCHITECH,http://eu.battle.net/sc2/en/profile/983045/1/architech/,architech,365
CUBIK07,http://eu.battle.net/sc2/en/profile/644462/1/ShutUpDonnie/,ShutUpDonnie,492
TOMMY_ZLEE,http://eu.battle.net/sc2/en/profile/614918/1/Darkko/,Darkko,595
SUNBEAM,http://eu.battle.net/sc2/en/profile/575982/1/Sunbeam/,Sunbeam,126
ASS_KICKER,http://eu.battle.net/sc2/en/profile/676307/1/uzzi/,uzzi,944
EPICFAIL,http://eu.battle.net/sc2/en/profile/706958/1/OxFF/,OxFF,563
WOODMAKER,http://eu.battle.net/sc2/en/profile/820215/1/woodmaker/,woodmaker,626
STRANGERD,http://eu.battle.net/sc2/en/profile/1144885/1/StrangerD/,StrangerD,510
DEFILER,http://eu.battle.net/sc2/en/profile/307907/1/defiler/,defiler,634
GWINN,http://eu.battle.net/sc2/en/profile/1437124/1/Gwinn/,Gwinn,369
PLECH,,Polymorph,719
DESTROYER,http://eu.battle.net/sc2/en/profile/572398/1/DestroyER/,DestroyER,140
PANVA,http://eu.battle.net/sc2/en/profile/483330/1/PanvA/,PanvA,757
ATMKO,http://eu.battle.net/sc2/en/profile/744901/1/ATM/,ATM,991
SKELLYUS,http://eu.battle.net/sc2/en/profile/355039/1/Matess/,Matess,714
GAPPO,http://eu.battle.net/sc2/en/profile/436115/1/Gappo/,Gappo,967
MONGHOL,http://eu.battle.net/sc2/en/profile/1348061/1/Monghol/,Monghol,204"""

    for d in data.split('\n'):
        username, bnet_url, name, code = d.split(',')
        if User.objects.filter(username=username).count() > 0:
            print 'user %s already exists' % username
            continue
        user = User.objects.create_user(username, '', 'sc')
        user = _configure_user(user)
        user.set_unusable_password()
        user.save()
        PlayerProfile.objects.create(
            user=user,
            bnet_url=bnet_url,
            character_name=name,
            character_code=code,
            contact='http://www.nyx.cz/index.php?l=mail;recipient=%s' % username,
        )
        print 'created user %s' % user


def import_round(data, round_id):
    from tms.models import Match, Round, PlayerProfile

    round = Round.objects.get(id=round_id)

    matches = data.split('\n')
    for match in matches:
        p1, s1, s2, p2 = match.split(',')
        Match.objects.create(
            round=round,
            player1=PlayerProfile.objects.get(user__username=p1),
            player2=PlayerProfile.objects.get(user__username=p2),
            player1_score=s1,
            player2_score=s2,
            finished=True,
        )

'''
def import_rounds():
    r1="""MARTYMARTY,2,0,JANDOS
MCKIDNEY,0,2,SHARNY
ASS_KICKER,0,2,PERRY
LOBIN,1,2,SUNBEAM
TOMMY_ZLEE,2,0,KULHY
EPICFAIL,0,2,ARCHITECH
OGLOKOOG,2,1,TEROX
REESHA,2,0,SAVANNAH
XTREE,0,2,CUBIK07
BIOH,2,0,JUNGLER"""

    import_round(r1, 18)
'''

def match_profile_to_user():
    from tms.models import Match, PlayerProfile

    for m in Match.objects.all():
        #m.player1_id = m.player1.user_id
        #m.player2_id = m.player2.user_id
        if m.winner_id is not None:
            m.winner = PlayerProfile.objects.get(id=m.winner_id).user

        if m.loser_id is not None:
            m.loser = PlayerProfile.objects.get(id=m.loser_id).user

        print m, m.winner, m.loser
        #m.converted = True
        m.save()


def migrate_playoff(old_tournament_slug, new_tournament_slug):
    from tms.models import Round, Tournament, OldTournament
    from tms.tour.nsl_v1.models import Playoff

    ot = OldTournament.objects.get(slug=old_tournament_slug)
    nt = Tournament.objects.get(slug=new_tournament_slug)

    if not nt.playoff:
        nt.playoff = Playoff.objects.create(parent_node=nt, name='Playoff')

    for round in Round.objects.filter(type=Round.TYPE_SINGLE_ELIM, tournament=ot):
        round.parent_node = nt.playoff
        round.save()


def migrate_playoff_s1():
    migrate_playoff('nyx-sc2-league-season-1', 'nsl-season-1')


def migrate_players(os_id, ns_id):
    from tms.models import OldTournament, Tournament, Player

    os = OldTournament.objects.get(id=os_id)
    ns = Tournament.objects.get(id=ns_id)
    sw = ns.swiss

    for c in os.competitor_set.all():
        Player.objects.create(
            node=ns,
            user=c.player.user,
        )
        Player.objects.create(
            node=sw,
            user=c.player.user,
            json_data=c.json_data
        )

def migrate_rounds(os_id, ns_id):
    from tms.models import OldTournament, Tournament, Round

    ns = Tournament.objects.get(id=ns_id)

    # swiss
    sw = ns.swiss
    assert sw
    for round in Round.objects.filter(tournament=os_id,
                                      type__in=(Round.TYPE_RANDOM,
                                                Round.TYPE_SWISS)):
        round.parent_node = sw
        round.save()
    sw._create_ranking()

    # playoff
    pl = ns.playoff
    assert pl
    for round in Round.objects.filter(tournament=os_id,
                                      type=Round.TYPE_SINGLE_ELIM):
        round.parent_node = pl
        round.save()


def migrate_players_s23():
    migrate_players(4, 12)
    migrate_players(5, 16)


def migrate_rounds_s23():
    migrate_rounds(4, 12)
    migrate_rounds(5, 16)
