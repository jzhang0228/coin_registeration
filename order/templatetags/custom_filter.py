from django import template
register = template.Library()

@register.filter(name='get_len')
def get_len(field):
    return len(field)