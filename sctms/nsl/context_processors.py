from django.conf import settings


class __DomainGetter(object):
    def __getattr__(self, name):
        d = settings.DOMAINS
        return 'http://' + d.get(name, d['default'])

_domains = __DomainGetter()


def domains(request):
    return {
        'domains': _domains,
        'current_domain': getattr(settings, 'CURRENT_DOMAIN', None),
    }
