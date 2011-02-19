from django import template

register = template.Library()

@register.inclusion_tag('forms/field.html')
def field(field, extra_class=''):
    widget_class = field.field.widget.__class__.__name__
    return locals()
