from django.conf.urls.defaults import patterns, url
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

import datetime, array

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from cms.models import Comment, BlogEntry, CommentForm



def index(request):
    latest_entry_list = BlogEntry.objects.all().order_by('-date').filter(showfront=1)[:10]
    for entry in latest_entry_list:
        comment_entry_list = Comment.objects.all().filter(topic=entry)
        entry.comments = comment_entry_list.count()
    c = {'latest_entry_list': latest_entry_list}
    return direct_to_template(request, 'cms/index.html', c)
    
def detail(request, slug):
    entry = get_object_or_404(BlogEntry, slug=slug)
    comment_entry_list = Comment.objects.all().filter(topic=entry).order_by('date')
    i = 1
    for comment in comment_entry_list:
        comment.number = i
        i += 1
    entry.comments = comment_entry_list.count()    
    c = {'entry': entry, 'comment_entry_list': comment_entry_list}
    entry.hits += 1
    entry.save()
    return direct_to_template(request, 'cms/detail.html', c)

@login_required
def add_comment(request, slug):
    entry = get_object_or_404(BlogEntry, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.topic = entry
            comment.date = datetime.datetime.now()
            comment.save()
            comment_entry_list = Comment.objects.all().filter(topic=entry).order_by('date')
            c = {'entry': entry, 'comment_entry_list': comment_entry_list}
            return HttpResponseRedirect(reverse('cms:detail', kwargs={'slug':entry.slug})+'#end')
                 
    else:
        form = CommentForm()
        
    c = {'entry' : entry, 'form' : form}
    return direct_to_template(request, 'cms/comment.html', c)
            
