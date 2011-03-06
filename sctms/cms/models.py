from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Categories')
        
    def __unicode__(self):
        return self.name
                        

class BlogEntry(models.Model):
    author = models.ForeignKey(User, unique=True)
    category = models.ForeignKey(Category)
    date = models.DateTimeField('date published')
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=150)
    hits = models.IntegerField()
    up = models.IntegerField()
    down = models.IntegerField()    
    text = models.TextField()    
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _(u'Blog Entry')
        verbose_name_plural = _(u'Blog Entries')
            
    
  
class Comment(models.Model):
    author = models.ForeignKey(User, unique=True)
    topic = models.ForeignKey(BlogEntry)
    title = models.CharField(max_length=100)
    date = models.DateTimeField('date published')    
    up = models.IntegerField()
    down = models.IntegerField()
    text = models.TextField()    
    
    def __unicode__(self):
        return self.title
    

  