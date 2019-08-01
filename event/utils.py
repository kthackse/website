from django.utils import timezone

from event.enums import EventApplicationStatus
from event.models import Event, Application, FAQItem


def get_next_or_past_event(published=True):
    event = (
        Event.objects.filter(published=published, ends_at__gte=timezone.now())
        .order_by("starts_at")
        .first()
    )
    if event:
        event.passed = False
        return event
    event = Event.objects.filter(published=published).order_by("ends_at").first()
    if event:
        event.passed = True
        return event
    return None


def get_next_events(published=True):
    return Event.objects.filter(published=published).order_by("starts_at")


def get_event(code, published=True):
    event = Event.objects.filter(code=code, published=published).first()
    if event.application_status == EventApplicationStatus.OPEN:
        return event
    return None


def get_application(event_id, user_id):
    return Application.objects.filter(event_id=event_id, user_id=user_id).first()


def get_application_by_resume(resume):
    return Application.objects.filter(resume=resume).first()


def get_applications(event_id):
    return Application.objects.filter(event_id=event_id)


def get_faq_items(event_id):
    return FAQItem.objects.filter(event_id=event_id, active=True).order_by("order")
