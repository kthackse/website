import os

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def time_left(time: timezone.datetime):
    return time - timezone.now()


@register.filter
def days_left(timedelta: timezone.timedelta):
    return int(timedelta.total_seconds() // (60*60*24))


@register.filter
def days_left(timedelta: timezone.timedelta):
    return int(timedelta.total_seconds() // (60*60*24))


@register.filter
def file_name(value):
    return os.path.basename(value.file.name)
