from datetime import datetime

from django.db import models


class TournamentManager(models.Manager):

    def exclude_owned(self):
        return self.get_query_set().filter(owner=None)

    def ongoing(self):
        return (self.exclude_owned().filter(round__start__lte=datetime.now())
                                    .filter(round__end__gte=datetime.now())
                                    .distinct())

    def future(self):
        return self.exclude_owned().exclude(round__start__lte=datetime.now())

    def past(self):
        return (self.exclude_owned().exclude(round__end__gte=datetime.now())
                                    .exclude(round=None))
