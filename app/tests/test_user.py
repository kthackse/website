from unittest import mock
import pytest
from django.utils import timezone

from app.tests.factories import UserFactory
from user.utils import generate_verify_key


@pytest.mark.django_db
def test_verification():
    user = UserFactory()

    # User is not verified by default
    assert not user.email_verified

    # Generate and set a verify key
    verify_key = generate_verify_key(user)
    user.update_verify(verify_key=verify_key)

    # Verify user
    user.verify(verify_key=verify_key)
    assert user.email_verified

    # User is not verified again
    user.disable_verify()
    assert not user.email_verified

    # Generate and set a new verify key
    verify_key = generate_verify_key(user)
    user.update_verify(verify_key=verify_key)

    with mock.patch(
        "django.utils.timezone.now",
        return_value=timezone.now() + timezone.timedelta(hours=2),
    ):
        # Can't verify user as the key has expired
        user.verify(verify_key=verify_key)
        assert not user.email_verified

    # Verify user again without expiration
    user.verify(verify_key=verify_key)
    assert user.email_verified
