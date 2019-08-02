import re

import html2text as html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from app.variables import HACKATHON_ORGANIZER_EMAIL_REGEX, HACKATHON_EMAIL_PREFIX, HACKATHON_EMAIL_NOREPLY, \
    HACKATHON_EMAIL_CONTACT, HACKATHON_NAME


def get_substitutions_templates():
    return {
        "hk_app_name": getattr(settings, "HACKATHON_APP_NAME", None),
        "hk_name": getattr(settings, "HACKATHON_NAME", None),
        "hk_description": getattr(settings, "HACKATHON_DESCRIPTION", None),
        "hk_timezone": getattr(settings, "HACKATHON_TIMEZONE", None),
        "hk_domain": getattr(settings, "HACKATHON_DOMAIN", None),
        "hk_email_contact": getattr(settings, "HACKATHON_EMAIL_CONTACT", None),
        "hk_email_webdev": getattr(settings, "HACKATHON_EMAIL_WEBDEV", None),
        "hk_email_sponsorship": getattr(settings, "HACKATHON_EMAIL_SPONSORSHIP", None),
        "hk_sn_facebook": getattr(settings, "HACKATHON_SN_FACEBOOK", None),
        "hk_sn_twitter": getattr(settings, "HACKATHON_SN_TWITTER", None),
        "hk_sn_instagram": getattr(settings, "HACKATHON_SN_INSTAGRAM", None),
        "hk_sn_youtube": getattr(settings, "HACKATHON_SN_YOUTUBE", None),
        "hk_sn_linkedin": getattr(settings, "HACKATHON_SN_LINKEDIN", None),
        "hk_sn_medium": getattr(settings, "HACKATHON_SN_MEDIUM", None),
        "hk_sn_github": getattr(settings, "HACKATHON_SN_GITHUB", None),
    }


def variables_processor(request):
    c = get_substitutions_templates()
    from event.utils import get_next_or_past_event
    event = get_next_or_past_event()
    if event:
        c["event"] = event
        c["background_video"] = (event.background.name[-4:] == ".mp4")
        c["background_image"] = (event.background.name[-4:] in [".png", ".jpg", ".jpeg", ".gif", ".svg"])
    return c


def is_email_organizer(email):
    return re.match(HACKATHON_ORGANIZER_EMAIL_REGEX, email)


def get_notification_template(type: str, method: str, task: str, format: str):
    return settings.NOTIFY_TEMPLATES[method][type][task][format]


def send_email(
    subject,
    body,
    to,
    from_email=None,
    reply_to=None,
    tags=None,
    track_clicks=False,
    fail_silently=False,
    attachments=None,
):
    if tags is None:
        tags = []

    tags += HACKATHON_NAME.lower()

    if to and not isinstance(to, (list, tuple)):
        to = [to]

    if reply_to and not isinstance(reply_to, (list, tuple)):
        reply_to = [reply_to]

    body_plain = html2text.html2text(body)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_plain,
        from_email=from_email or HACKATHON_NAME + "<" + HACKATHON_EMAIL_NOREPLY + ">",
        to=to,
        reply_to=reply_to or [HACKATHON_NAME + "<" + HACKATHON_EMAIL_CONTACT + ">"],
        attachments=attachments,
    )

    msg.attach_alternative(body, "text/html")

    if tags:
        msg.tags = tags

    msg.track_clicks = track_clicks

    return msg.send(fail_silently=fail_silently)
