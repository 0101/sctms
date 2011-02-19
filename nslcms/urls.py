from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^p/', include('pages.urls', namespace='pages')),
    (r'', include('tms.urls', namespace='tms')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        # serve static files only for development
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
