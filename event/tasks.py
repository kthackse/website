from celery import shared_task
from django.template.loader import render_to_string

from app.enums import MailTag
from app.utils import get_notification_template, send_email, get_substitutions_templates
from event.models import Subscriber, Event, Invoice


@shared_task
def send_subscriber_new(subscriber: Subscriber, event: Event = None):
    context = get_substitutions_templates()
    context["subscriber"] = subscriber
    if event:
        context["event"] = event
    template = get_notification_template(
        method="email", type="subscribe", task="new", format="html"
    )
    subject = get_notification_template(
        method="email", type="subscribe", task="new", format="subject"
    )
    body = render_to_string(template, context)

    send_email(
        subject=subject, body=body, to=subscriber.email, tags=[MailTag.SUBSCRIBE]
    )


@shared_task
def send_subscriber_resubscribed(subscriber: Subscriber, event: Event = None):
    context = get_substitutions_templates()
    context["subscriber"] = subscriber
    if event:
        context["event"] = event
    template = get_notification_template(
        method="email", type="subscribe", task="resubscribe", format="html"
    )
    subject = get_notification_template(
        method="email", type="subscribe", task="resubscribe", format="subject"
    )
    body = render_to_string(template, context)

    send_email(
        subject=subject, body=body, to=subscriber.email, tags=[MailTag.SUBSCRIBE]
    )


@shared_task
def send_invoice(invoice: Invoice, request=None):
    context = get_substitutions_templates()
    context["invoice"] = invoice
    context["event"] = invoice.company_event.event
    context["user"] = invoice.responsible_company
    template = get_notification_template(
        method="email", type="sponsorship", task="invoice", format="html"
    )
    subject = get_notification_template(
        method="email", type="sponsorship", task="invoice", format="subject"
    ).format(event_name=str(invoice.company_event.event))
    body = render_to_string(template, context)
    attachments = [
        (
            invoice.invoice.name[invoice.invoice.name.rfind("/") + 1 :],
            invoice.invoice.read(),
            "application/pdf",
        )
    ]

    send_email(
        subject=subject,
        body=body,
        to=invoice.responsible_company.email,
        tags=[MailTag.INVOICE],
        attachments=attachments,
    )

    invoice.mark_as_sent(request=request)
