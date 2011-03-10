from urls.base import pattern_list, sections, _404_below_this_


urlpatterns = pattern_list(
    sections['admin'],
    sections['pages'],
    sections['cms'],
    _404_below_this_,
    sections['tms'],
    sections['irc'],
)
