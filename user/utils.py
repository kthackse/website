from uuid import UUID

from user.models import User


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
