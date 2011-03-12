from urls.base import pattern_list, sections, _404_below_this_


urlpatterns = pattern_list(
    sections['irc'],
    _404_below_this_,
    sections['admin'],
    sections['pages'],
    sections['cms'],
    sections['tms'],
)
