from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404


from pages.models import Page


def page(request, slug, template='pages/page.html'):
    context = {'page': get_object_or_404(Page, slug=slug)}
    return direct_to_template(request, template, context)
