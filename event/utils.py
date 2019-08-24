import random
import string

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from event.enums import EventApplicationStatus, CompanyTier, SubscriberStatus, EventType
from event.models import (
    Event,
    Application,
    FAQItem,
    Subscriber,
    CompanyEvent,
    Invoice,
    Team,
)
from event.tasks import send_subscriber_new, send_subscriber_resubscribed

from django.core.validators import validate_email


def get_next_or_past_event(published=True):
    event = (
        Event.objects.filter(
            published=published,
            ends_at__gte=timezone.now(),
            type=EventType.HACKATHON.value,
        )
        .order_by("starts_at")
        .first()
    )
    if event:
        event.passed = False
        return event
    event = (
        Event.objects.filter(published=published, type=EventType.HACKATHON.value)
        .order_by("ends_at")
        .first()
    )
    if event:
        event.passed = True
        return event
    return None


def get_next_events(published=True):
    return Event.objects.filter(published=published).order_by("starts_at")


def get_event(code, published=True, application_status=EventApplicationStatus.OPEN):
    event = Event.objects.filter(code=code, published=published).first()
    if not application_status or event.application_status == application_status:
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
        messages.add_message(
            request,
            messages.ERROR,
            "We are sorry, but we couldn't subscribe the email!",
        )
        return None
    subscriber = Subscriber.objects.filter(email=email).first()
    if not subscriber:
        subscriber = Subscriber(email=email)
        subscriber.save()
        subscriber.events.add(event)
        send_subscriber_new(subscriber, event=event)
        if request:
            messages.success(
                request, "Thank-you for subscribing, remember to verify your email!"
            )
        return subscriber
    elif subscriber.status == SubscriberStatus.UNSUBSCRIBED.value:
        subscriber.status = SubscriberStatus.SUBSCRIBED.value
        subscriber.save()
        send_subscriber_resubscribed(subscriber, event=event)
        if request:
            messages.success(request, "Thank-you for subscribing again!")
        return subscriber
    if request:
        messages.add_message(
            request,
            messages.ERROR,
            "We are sorry, but we couldn't subscribe the email!",
        )
    return None


def get_sponsors_in_event(event_id):
    return CompanyEvent.objects.filter(
        event_id=event_id, tier__lt=CompanyTier.PARTNER.value, public=True
    )


def get_partners_in_event(event_id):
    return CompanyEvent.objects.filter(
        event_id=event_id, tier=CompanyTier.PARTNER.value, public=True
    )


def get_organisers_in_event(event_id):
    return CompanyEvent.objects.filter(
        event_id=event_id, tier=CompanyTier.ORGANISER.value, public=True
    )


def get_invoice_by_invoice(invoice):
    return Invoice.objects.filter(invoice=invoice).first()


def get_applications_by_user(user_id):
    return Application.objects.filter(user_id=user_id)


def generate_code(length=8):
    return "".join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits)
        for _ in range(length)
    ).upper()


def create_team(event_id, user_id, name):
    team = Team(event_id=event_id, creator_id=user_id, name=name, code=generate_code())
    team.save()
    return team


def remove_team(event_id, user_id, team_id):
    team = Team.objects.filter(
        id=team_id, event_id=event_id, creator_id=user_id
    ).first()
    if team:
        team.delete()


def assign_team(event_id, user_id, team_code):
    application = Application.objects.filter(event_id=event_id, user_id=user_id).first()
    if application:
        team = Team.objects.filter(code=team_code).first()
        if team:
            if (
                Application.objects.filter(event_id=event_id, team_id=team.id).count()
                < 4
            ):
                application.team_id = team.id
                application.save()
                return True
    return False


def deassign_team(event_id, user_id):
    application = Application.objects.filter(event_id=event_id, user_id=user_id).first()
    if application:
        application.team = None
        application.save()
        return True
    return False


def get_teammates_by_user(user_id):
    event = get_next_or_past_event()
    if event:
        application = Application.objects.filter(
            event_id=event.id, user_id=user_id
        ).first()
        if application and application.team:
            return Application.objects.filter(
                event_id=event.id, team_id=application.team.id
            )
    return None
