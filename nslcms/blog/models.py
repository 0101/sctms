from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

class Topic(models.Model):
    author = models.ForeignKey(User, unique=True)
    category = models.ForeignKey(Category)
    date = models.DateTimeField('date published')
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=150)
    hits = models.IntegerField()
    
    def __unicode__(self):
        return self.title
    
  
class Comment(models.Model):
    author = models.ForeignKey(User, unique=True)
    topic = models.ForeignKey(Topic)
    title = models.CharField(max_length=100)
    date = models.DateTimeField('date published')    
    up = models.IntegerField()
    down = models.IntegerField()
    
    def __unicode__(self):
        return self.title
    
class BlogEntry(models.Model):
    topic = models.ForeignKey(Topic)
    text = models.TextField()
    
    def __unicode__(self):
        return self.topic
    
    
class CommentEntry(models.Model):
    topic = models.ForeignKey(Comment)
    text = models.TextField()
    
    def __unicode__(self):
        return self.topic

  