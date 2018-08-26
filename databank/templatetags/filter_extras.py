from django import template

register = template.Library()

@register.filter
def has_parent(props, parent):
    return props.filter(parent=parent).first()