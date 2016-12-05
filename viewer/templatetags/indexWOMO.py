from django import template
register = template.Library()

@register.filter
def indexWOMO(List, i):
    return List[int(i)]