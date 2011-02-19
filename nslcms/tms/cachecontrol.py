from django.db import models

from tms.utils import merge, do_nothing


SAVE = 'save'
DELETE = 'delete'
ANY = 'any'


class __CacheControl(object):

    def __init__(self):
        self._registry = {}

    def bind(self, model, action, function):
        key = (model, action)
        if key in self._registry:
            self._registry[key].append(function)
        else:
            self._registry[key] = [function]

    def trigger(self, obj, action):
        keys = [(obj.__class__, action),
                (obj.__class__, ANY),
                (ANY, ANY),]
        for fn in merge([self._registry.get(key, []) for key in keys]):
            fn(obj.__class__, obj, action)


cache_control = __CacheControl()


def bind_clear_cache(destination_model, source_model=ANY, action=ANY):
    """
    Shortcut for binding Model.clear_cache method to cache_control
    """
    cache_control.bind(source_model, action, destination_model.clear_cache)


class CacheNotifierModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(CacheNotifierModel, self).save(*args, **kwargs)
        cache_control.trigger(self, SAVE)

    def delete(self, *args, **kwargs):
        super(CacheNotifierModel, self).delete(*args, **kwargs)
        cache_control.trigger(self, DELETE)


class ClearCacheMixin(object):

    @classmethod
    def clear_cache(cls, model, obj, action):
        fn = getattr(cls, 'clear_cache_' + model.__name__.lower(), do_nothing)
        fn(obj, action)
