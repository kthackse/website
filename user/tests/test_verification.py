import pytest

from app.tests.factories import UserFactory


@pytest.mark.django_db
def test_test():
    user = UserFactory()
    assert user
