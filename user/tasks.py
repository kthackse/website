from celery import shared_task
from django.template.loader import render_to_string

from app.enums import MailTag
from app.utils import get_notification_template, send_email, get_substitutions_templates
from event.utils import get_next_or_past_event
from user.models import User


@shared_task
def send_verify_email(user: User, verify_key: str):
    context = get_substitutions_templates()
    context["user"] = user
    context["verify_key"] = verify_key
    context["event"] = get_next_or_past_event()
    template = get_notification_template(method="email", type="signup", task="verify", format="html")
    subject = get_notification_template(method="email", type="signup", task="verify", format="subject")
    body = render_to_string(template, context)

    send_email(
        subject=subject,
        body=body,
        to=user.email,
        tags=[MailTag.VERIFY],
    )
