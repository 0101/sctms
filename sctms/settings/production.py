# common production settings

from settings import *

DOMAINS = {
    'default': 'thensl.cz',
    'tms': 'tour.thensl.cz',
    'irc': 'chat.thensl.cz',
}

SESSION_COOKIE_DOMAIN = '.thensl.cz'

MEDIA_URL = 'http://nslstatic.mazec.org/'

ADMIN_MEDIA_PREFIX = 'http://adminstatic.mazec.org/'
