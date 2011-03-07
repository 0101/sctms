from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^cms/', include('cms.urls')),
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
