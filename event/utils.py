from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from event.enums import EventApplicationStatus, CompanyTier, SubscriberStatus
from event.models import Event, Application, FAQItem, Subscriber, CompanyEvent
from event.tasks import send_subscriber_new, send_subscriber_resubscribed
from user.models import User

from django.core.validators import validate_email


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


def add_subscriber(email, event, request=None):
    try:
        validate_email(email)
    except ValidationError:
        messages.add_message(request, messages.ERROR, "We are sorry, but we couldn't subscribe the email!")
        return None
    subscriber = Subscriber.objects.filter(email=email).first()
    if not subscriber:
        subscriber = Subscriber(email=email)
        subscriber.events.add(event)
        subscriber.save()
        send_subscriber_new(subscriber, event=event)
        if request:
            messages.success(request, "Thank-you for subscribing, remember to verify your email!")
        return subscriber
    elif subscriber.status == SubscriberStatus.UNSUBSCRIBED.value:
        subscriber.status = SubscriberStatus.SUBSCRIBED.value
        subscriber.save()
        send_subscriber_resubscribed(subscriber, event=event)
        if request:
            messages.success(request, "Thank-you for subscribing again!")
        return subscriber
    if request:
        messages.add_message(request, messages.ERROR, "We are sorry, but we couldn't subscribe the email!")
    return None


def get_sponsors_in_event(event_id):
    return CompanyEvent.objects.filter(event_id=event_id, tier__lt=CompanyTier.PARTNER.value, public=True)


def get_partners_in_event(event_id):
    return CompanyEvent.objects.filter(event_id=event_id, tier=CompanyTier.PARTNER.value, public=True)
