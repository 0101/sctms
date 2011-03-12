from urls.base import pattern_list, sections, _404_below_this_


urlpatterns = pattern_list(
    sections['tms'],
    _404_below_this_,
    sections['admin'],
    sections['cms'],
    sections['irc'],
    sections['pages'],
)
