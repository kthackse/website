import re

from django.conf import settings

from app.variables import HACKATHON_ORGANIZER_EMAIL_REGEX


def get_substitutions_templates():
    return {
        "hk_app_name": getattr(settings, "HACKATHON_APP_NAME", None),
        "hk_name": getattr(settings, "HACKATHON_NAME", None),
        "hk_description": getattr(settings, "HACKATHON_DESCRIPTION", None),
        "hk_timezone": getattr(settings, "HACKATHON_TIMEZONE", None),
        "hk_domain": getattr(settings, "HACKATHON_DOMAIN", None),
        "hk_email_contact": getattr(settings, "HACKATHON_EMAIL_CONTACT", None),
        "hk_email_webdev": getattr(settings, "HACKATHON_EMAIL_WEBDEV", None),
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
    return c


def is_email_organizer(email):
    return re.match(HACKATHON_ORGANIZER_EMAIL_REGEX, email)
