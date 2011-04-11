from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View


class DynamicTemplateView(View):
    response_class = TemplateResponse

    def render_to_response(self, request, context, **response_kwargs):
        return self.response_class(
            request = self.request,
            template = self.get_template_names(request, context),
            context = context,
            **response_kwargs
        )

    def get_template_names(self, request, context):
        raise ImproperlyConfigured(
            'DynamicTemplateView requires an implementation '
            'of get_template_names()')


class AjaxTemplateView(DynamicTemplateView):
    template_name = None
    ajax_template_name = None

    def get_template_names(self, request, context):
        if self.template_name is None:
            raise ImproperlyConfigured(
                'AjaxTemplateView requires a definition of template_name')
        if self.ajax_template_name is None:
            raise ImproperlyConfigured(
                'AjaxTemplateView requires a definition of ajax_template_name')
        return self.ajax_template_name if request.is_ajax() else self.template_name


class UserProfile(AjaxTemplateView):
    template_name = 'nsl/user_profile.html'
    ajax_template_name = 'nsl/user_profile_content.html'

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        profile = user.get_profile()
        return self.render_to_response(request, {'profile': profile})
