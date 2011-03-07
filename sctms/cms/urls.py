from django.conf.urls.defaults import *

urlpatterns = patterns('cms.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<slug>[\w_-]+)/detail/$', 'detail', name='detail'),
    )