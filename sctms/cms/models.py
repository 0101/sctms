from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from jsonstore.models import JsonStore

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')
        
    def __unicode__(self):
        return self.name
                        

class BlogEntry(models.Model):
    author = models.ForeignKey(User)
    category = models.ForeignKey(Category)
    date = models.DateTimeField('date published')
    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='title')
    tags = models.CharField(max_length=150)
    hits = models.IntegerField(default=0)
    up = models.IntegerField(default=0)
    down = models.IntegerField(default=0)
    highlight = models.TextField(blank=True)
    text = models.TextField()
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _(u'Blog Entry')
        verbose_name_plural = _(u'Blog Entries')
    
    def slug_title(self):
        return '';
  
class Comment(models.Model):
    author = models.ForeignKey(User, unique=True)
    topic = models.ForeignKey(BlogEntry)
    title = models.CharField(max_length=100)
    date = models.DateTimeField('date published')    
    up = models.IntegerField(default=0)
    down = models.IntegerField(default=0)
    text = models.TextField()    
    
    def __unicode__(self):
        return self.title
    

  