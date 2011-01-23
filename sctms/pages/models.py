from django.db import models
from django.utils.translation import ugettext_lazy as _


class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    content = models.TextField()

    class Meta:
        verbose_name = _(u'Page')
        verbose_name_plural = _(u'Pages')
