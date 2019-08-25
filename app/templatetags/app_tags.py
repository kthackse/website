import math
import os

from django import template
from django.utils import timezone

from app import settings
from event.enums import ApplicationStatus
from user.enums import SexType

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.filter
def time_left(time: timezone.datetime):
    return time - timezone.now()


@register.filter
def timedelta_display(time: timezone.timedelta):
    seconds = time.total_seconds()
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "{:02d}:{:02d}:{:02d}".format(math.floor(h), math.floor(m), math.floor(s))


@register.filter
def days_left(timedelta: timezone.timedelta):
    return int(timedelta.total_seconds() // (60 * 60 * 24))


@register.filter
def file_name(value):
    return os.path.basename(value.file.name)


@register.filter
def display_departments(departments):
    return " / ".join([d.name for d in departments])


@register.filter
def response_title(code):
    if float(code) / 100.0 == 2.0:
        return "Success " + str(code)
    return "Error " + str(code)


@register.filter
def application_status(status):
    return ApplicationStatus(status).name.capitalize()


@register.filter
def user_sex(status):
    return SexType(status).name.capitalize()
