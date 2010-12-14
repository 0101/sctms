from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
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


def odd(x):
    "Returns whether the length of x is odd"
    return len(x) % 2 == 1


def split(sequence, size):
    "Splits the squence into chunks of given size"
    return [sequence[i:i+size] for i in range(0, len(sequence), size)]


def merge(x):
    "Merges a sequence of lists into one list"
    return sum(x, [])


def do_nothing(*args, **kwargs):
    pass


def import_players():
    from django.contrib.auth.models import User
    from tms.models import Player

    data = """MARTYMARTY,http://eu.battle.net/sc2/en/profile/210242/1/marty/,marty,249
JANDOS,http://eu.battle.net/sc2/en/profile/204174/1/Jandos/,Jandos,213
SUNBEAM,http://eu.battle.net/sc2/en/profile/575982/1/Sunbeam/,Sunbeam,126
ARCHITECH,http://eu.battle.net/sc2/en/profile/983045/1/architech/,architech,365
CUBIK07,http://eu.battle.net/sc2/en/profile/644462/1/ShutUpDonnie/,ShutUpDonnie,492
SAVANNAH,http://eu.battle.net/sc2/en/profile/202925/1/Savannah/,Savannah,765
TOMMY_ZLEE,http://eu.battle.net/sc2/en/profile/614918/1/Darkko/,Darkko,595
SHARNY,http://eu.battle.net/sc2/en/profile/487923/1/Sharny/,Sharny,980
PERRY,http://eu.battle.net/sc2/en/profile/904228/1/perryone/,perryone,722
OGLOKOOG,http://eu.battle.net/sc2/en/profile/971744/1/Oglokoog/,Oglokoog,592
ASS_KICKER,http://eu.battle.net/sc2/en/profile/676307/1/uzzi/,uzzi,944
MCKIDNEY,http://eu.battle.net/sc2/en/profile/212958/1/mcKidney/,mcKidney,154
LOBIN,http://eu.battle.net/sc2/en/profile/1073892/1/Lobin/,Lobin,989
KULHY,http://eu.battle.net/sc2/en/profile/806297/1/StarCore/,StarCore,403
EPICFAIL,http://eu.battle.net/sc2/en/profile/706958/1/OxFF/,OxFF,563
BIOH,http://eu.battle.net/sc2/en/profile/300429/1/SPDB/,SPDB,854
JUNGLER,http://eu.battle.net/sc2/en/profile/1067753/1/Jungler/,jungler,905
REESHA,http://eu.battle.net/sc2/en/profile/1096458/1/Firael/,Firael,115
XTREE,http://eu.battle.net/sc2/en/profile/693362/1/xTree/,xtree,387
TEROX,http://eu.battle.net/sc2/en/profile/406042/1/terox/,terox,442"""

    for d in data.split('\n'):
        username, bnet_url, name, code = d.split(',')
        if User.objects.filter(username=username).count() > 0:
            print 'user %s already exists' % username
            continue
        user = User.objects.create_user(username, '', 'sc')
        Player.objects.create(
            user=user,
            bnet_url=bnet_url,
            character_name=name,
            character_code=code,
            contact='http://www.nyx.cz/index.php?l=mail;recipient=%s' % username,
        )
        print 'created user %s' % user


def import_round(data, round_id):
    from tms.models import Match, Round, Player

    round = Round.objects.get(id=round_id)

    matches = data.split('\n')
    for match in matches:
        p1, s1, s2, p2 = match.split(',')
        Match.objects.create(
            round=round,
            player1=Player.objects.get(user__username=p1),
            player2=Player.objects.get(user__username=p2),
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
