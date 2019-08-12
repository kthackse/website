from django import template

from event.enums import ApplicationStatus

register = template.Library()


@register.filter
def application_status(status):
    return ApplicationStatus(status).name
