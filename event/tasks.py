from celery import shared_task
from django.template.loader import render_to_string

from app.enums import MailTag
from app.utils import get_notification_template, send_email
from app.variables import HACKATHON_DOMAIN, HACKATHON_NAME, HACKATHON_DESCRIPTION
from event.models import Subscriber, Event


@shared_task
def send_subscriber_new(subscriber: Subscriber, event: Event = None):
    context = dict(subscriber=subscriber, hk_domain=HACKATHON_DOMAIN, hk_name=HACKATHON_NAME, hk_description=HACKATHON_DESCRIPTION)
    if event:
        context["event"] = event
    template = get_notification_template(method="email", type="subscribe", task="new", format="html")
    subject = get_notification_template(method="email", type="subscribe", task="new", format="subject")
    body = render_to_string(template, context)

    send_email(
        subject=subject,
        body=body,
        to=subscriber.email,
        tags=[MailTag.SUBSCRIBE],
    )


@shared_task
def send_subscriber_resubscribed(subscriber: Subscriber, event: Event = None):
    context = dict(subscriber=subscriber, hk_domain=HACKATHON_DOMAIN, hk_name=HACKATHON_NAME, hk_description=HACKATHON_DESCRIPTION)
    if event:
        context["event"] = event
    template = get_notification_template(method="email", type="subscribe", task="resubscribe", format="html")
    subject = get_notification_template(method="email", type="subscribe", task="resubscribe", format="subject")
    body = render_to_string(template, context)

    send_email(
        subject=subject,
        body=body,
        to=subscriber.email,
        tags=[MailTag.SUBSCRIBE],
    )
