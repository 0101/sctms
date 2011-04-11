from django.conf.urls.defaults import patterns, url

from nsl.views import UserProfile


urlpatterns = patterns('',
    url(r'^user/(?P<username>[\w_-]+)', UserProfile.as_view(), name='user_profile'),
)
