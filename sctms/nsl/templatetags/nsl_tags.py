from django.template import Library, Node

from tms.utils import is_manager


register = Library()

@register.inclusion_tag('includes/user-bar.html', takes_context=True)
def user_bar(context):
    user = context['user']
    user.is_manager = is_manager(user)
    context.update({'user': user})
    return context
