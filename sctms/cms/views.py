# Create your views here.

from blog.models import Topic, BlogEntry
from django.http import HttpResponse

def index(request):
    latest_topic_list = Topic.objects.all().order_by('date')[:5]
    output = ', '.join([t.title for t in latest_topic_list])
    return HttpResponse(output)
    
def detail(request, poll_id):
    return HttpResponse("You're looking at poll %s." % poll_id)

def comments(request, poll_id):
    return HttpResponse("You're looking at the results of poll %s." % poll_id)

def comment(request, poll_id):
    return HttpResponse("You're voting on poll %s." % poll_id)
   