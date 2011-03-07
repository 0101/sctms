from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template, redirect_to

admin.autodiscover()

urlpatterns = patterns('cms.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<slug>[\w_-]+)/detail/$', 'detail', name='detail'),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        # serve static files only for development
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
