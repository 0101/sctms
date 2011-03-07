from datetime import datetime
from random import randint

from django.conf.urls.defaults import patterns, url
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template

from nyxauth import NyxAuth

from django.template import loader
from cms.models import Comment, BlogEntry



def index(request):
    latest_entry_list = BlogEntry.objects.all().order_by('date')[:5]
    t = loader.get_template('cms/index.html')
    c = RequestContext(request, {
        'latest_entry_list': latest_entry_list,
    })
    return render_to_response('cms/index.html', c,context_instance=RequestContext(request))