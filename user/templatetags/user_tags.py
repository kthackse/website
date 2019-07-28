from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def ownership(name: str):
    if name[-1] == "s":
        return name + "'"
    return name + "'s"
