import pytz
from django import template
from django.utils import timezone

from app.variables import HACKATHON_TIMEZONE
from event.enums import ApplicationStatus

register = template.Library()


@register.filter
def application_status(status):
    return ApplicationStatus(status).name


@register.filter
def display_clock(time):
    base = int("1F54F", 16)
    hour = timezone.localtime(time, pytz.timezone(HACKATHON_TIMEZONE)).hour % 12
    if hour == 0:
        hour = 12
    return chr(base + hour)
