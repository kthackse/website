import hashlib
from uuid import UUID

from django.utils import timezone
from django.utils.crypto import get_random_string

from user.models import User
from user.tasks import send_verify_email


def is_participant(user):
    return user.is_participant


def is_organiser(user):
    return user.is_organiser


def get_user_by_picture(picture):
    try:
        user_id = UUID(picture[:36])
        return User.objects.filter(
            id=user_id,
        ).first()
    except ValueError:
        return None


def get_organisers(event_id):
    return User.objects.filter(events__in=[event_id]).order_by("name")


def generate_verify_key(user: User):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    secret_key = get_random_string(32, chars)
    return hashlib.sha256((secret_key + user.email).encode("utf-8")).hexdigest()


def send_verify(user: User):
    user.disable_verify()
    verify_key = generate_verify_key(user)
    user.update_verify(verify_key=verify_key)
    send_verify_email(user=user, verify_key=verify_key)
