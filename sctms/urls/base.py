from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin as admin
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseNotFound

admin.autodiscover()


sections = {
    'admin': patterns('',
        (r'^admin/', include(admin.site.urls))
    ),
    'cms': patterns('',
        (r'^', include('cms.urls', namespace='cms'))
    ),
    'pages': patterns('',
        (r'^p/', include('pages.urls', namespace='pages'))
    ),
    'irc': patterns('',
        url(r'^$', direct_to_template, {
            'template': 'irc.html',
            'extra_context': {'main_menu_selected': 'irc'}
        }, name='irc')
    ),
    'tms': patterns('',
        (r'^', include('tms.urls', namespace='tms'))
    ),
}

# insert to the pattern list to cut-off access to some urls, while keeping
# the ability to reverse-resolve them
_404_below_this_ = patterns('',
    url('', lambda request: HttpResponseNotFound('404 - Page find not could')))


def pattern_list(*args):
    """
    Merge more urlpatterns into one
    """
    return sum(args, patterns('',))


# Single-domain configuration for development
urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^cms/', include('cms.urls', namespace='cms')),
    (r'^p/', include('pages.urls', namespace='pages')),
    url(r'^irc/$', direct_to_template,
        {'template': 'irc.html', 'extra_context': {'main_menu_selected': 'irc'}},
        name='irc'),
    (r'', include('tms.urls', namespace='tms')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        # serve static files only for development
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
