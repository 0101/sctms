from datetime import datetime

from django.db import models
from django.db.models.query import QuerySet


class OldTournamentManager(models.Manager):

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
                                    .exclude(round=None)
                                    .order_by('-registration_deadline'))


class LeafClassQuerySet(QuerySet):

    def __getitem__(self, k):
        result = super(LeafClassQuerySet, self).__getitem__(k)
        if isinstance(result, models.Model):
            return result.as_leaf_class()
        else:
            return result

    def __iter__(self):
        for item in super(LeafClassQuerySet, self).__iter__():
            yield item.as_leaf_class()

    def get(self, *args, **kwargs):
        return super(LeafClassQuerySet, self).get(*args, **kwargs).as_leaf_class()


class LeafClassManager(models.Manager):

    def get_query_set(self):
        return LeafClassQuerySet(self.model, using=self._db)


class ThisTypeOnlyManager(models.Manager):

    def get_query_set(self):
        original_qs = super(ThisTypeOnlyManager, self).get_query_set()
        return original_qs.filter(type_id=self.model.get_id())
