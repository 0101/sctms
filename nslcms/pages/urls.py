from django.conf.urls.defaults import *


urlpatterns = patterns('pages.views',
    url(r'^(?P<slug>[\w_-]+)/$', 'page', name='page'),
)
