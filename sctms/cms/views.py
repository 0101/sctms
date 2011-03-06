# Create your views here.

from django.template import Context, loader
from cms.models import Comment, BlogEntry
from django.http import HttpResponse


def index(request):
    latest_entry_list = BlogEntry.objects.all().order_by('date')[:5]
    t = loader.get_template('cms/index.html')
    c = Context({
        'latest_entry_list': latest_entry_list,
    })
    return HttpResponse(t.render(c))