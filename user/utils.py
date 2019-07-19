from django.contrib.auth.decorators import user_passes_test


def is_participant(user):
    return user.is_participant
