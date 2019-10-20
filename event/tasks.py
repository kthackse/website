from celery import shared_task
from django.template.loader import render_to_string

from app.enums import MailTag
from app.processor import variables_processor
from app.utils import get_notification_template, send_email
from event.enums import MessageType
from event.models import Subscriber, Event, Invoice, Letter
from event.utils.messages import save_message_with_email, save_message


@shared_task
def send_subscriber_new(subscriber: Subscriber, event: Event = None):
    context = variables_processor()
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

    print("HMMM")

    save_message_with_email(
        (event.id if event else None),
        subscriber.email,
        subject,
        body,
        MessageType.SUBSCRIBED,
    )

    send_email(
        subject=subject, body=body, to=subscriber.email, tags=[MailTag.SUBSCRIBE]
    )


@shared_task
def send_subscriber_resubscribed(subscriber: Subscriber, event: Event = None):
    context = variables_processor()
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

    save_message_with_email(
        (event.id if event else None),
        subscriber.email,
        subject,
        body,
        MessageType.SUBSCRIBED,
    )

    send_email(
        subject=subject, body=body, to=subscriber.email, tags=[MailTag.SUBSCRIBE]
    )


@shared_task
def send_invoice(invoice: Invoice, request=None):
    context = variables_processor()
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
            invoice.invoice.file.name[invoice.invoice.file.name.rfind("/") + 1 :],
            invoice.invoice.file.read(),
            "application/pdf",
        )
    ]

    save_message(
        invoice.company_event.event.id,
        invoice.responsible_company.id,
        subject,
        body,
        MessageType.INVOICE,
        attachment=invoice.invoice,
    )

    send_email(
        subject=subject,
        body=body,
        to=invoice.responsible_company.email,
        tags=[MailTag.INVOICE],
        attachments=attachments,
    )

    invoice.mark_as_sent(request=request)


@shared_task
def send_letter_underage(letter: Letter, request=None):
    context = variables_processor()
    context["letter"] = letter
    template = get_notification_template(
        method="email", type="hackerxperience", task="letter_underage", format="html"
    )
    subject = get_notification_template(
        method="email", type="hackerxperience", task="letter_underage", format="subject"
    ).format(event_name=str(letter.application.event))
    body = render_to_string(template, context)
    attachments = [
        (
            letter.letter.file.name[letter.letter.file.name.rfind("/") + 1 :],
            letter.letter.file.read(),
            "application/pdf",
        )
    ]

    save_message(
        letter.application.event.id,
        letter.application.user.id,
        subject,
        body,
        MessageType.LETTER,
        attachment=letter.letter,
    )

    send_email(
        subject=subject,
        body=body,
        to=letter.application.user.email,
        tags=[MailTag.LETTER],
        attachments=attachments,
    )

    letter.mark_as_sent(request=request)
