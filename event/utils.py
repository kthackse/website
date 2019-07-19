from django.utils import timezone

from event.models import Event


def get_next_or_past_event(published=True):
    event = Event.objects.filter(published=published, ends_at__gte=timezone.now()).order_by("starts_at").first()
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
