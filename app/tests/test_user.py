from unittest import mock

import factory
import pytest
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from app.tests.factories import UserFactory, VerifiedUserFactory
from app.variables import HACKATHON_APP_NAME
from user.enums import UserType
from user.utils import generate_verify_key


@pytest.mark.django_db
def test_login():
    # Create a user
    password = factory.Faker("word")
    user = UserFactory(
        password=factory.PostGenerationMethodCall("set_password", password)
    )

    # Create a client
    client = Client()

    # Login
    assert client.login(username=user.email, password=password)


@pytest.mark.django_db
def test_verification():
    # Create a user
    password = factory.Faker("word")
    user = UserFactory(
        password=factory.PostGenerationMethodCall("set_password", password)
    )

    # Create a client and login
    client = Client()
    client.login(username=user.email, password=password)

    # User is not verified by default
    assert not user.email_verified

    # User is required to be verified
    request = client.get(reverse("app_dashboard"))
    assert isinstance(request, HttpResponseRedirect)
    assert request.status_code == 302
    assert request.url == reverse("user_verify")
    request = client.get(reverse("app_dashboard"), follow=True)
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert "<title>Verify your email | " + HACKATHON_APP_NAME + "</title>" in content
    assert user.email in content
    assert reverse("user_sendverification") in content

    # Profile page is available without verification
    request = client.get(reverse("user_profile"))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert "<title>Your profile | " + HACKATHON_APP_NAME + "</title>" in content
    assert user.name in content
    assert user.surname in content
    assert reverse("user_downloadpersonaldata") in content
    assert reverse("user_deactivate") in content

    # However, another user profile page is not available
    request = client.get(reverse("user_profileother", kwargs=dict(id=user.id)))
    assert isinstance(request, HttpResponseRedirect)
    assert request.status_code == 302
    assert request.url == reverse("user_verify")

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

    # Dashboard is now available
    request = client.get(reverse("app_dashboard"))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert "<title>Dashboard | " + HACKATHON_APP_NAME + "</title>" in content


@pytest.mark.django_db
def test_privacy():
    # Create a user
    password = factory.Faker("word")
    user = VerifiedUserFactory(
        password=factory.PostGenerationMethodCall("set_password", password)
    )

    # Create a client
    client = Client()

    # Picture not available without login
    request = client.get(user.picture.url)
    assert isinstance(request, HttpResponseRedirect)
    assert request.status_code == 302
    assert request.url == reverse("user_login") + "?next=" + user.picture.url

    # Login as the same user
    client.login(username=user.email, password=password)

    # Picture now available
    request = client.get(user.picture.url)
    assert isinstance(request, StreamingHttpResponse)

    # Logout
    client.logout()

    # Create another user and login
    password2 = factory.Faker("word")
    user2 = VerifiedUserFactory(
        password=factory.PostGenerationMethodCall("set_password", password2)
    )
    client.login(username=user2.email, password=password2)

    # Picture still available
    request = client.get(user.picture.url)
    assert isinstance(request, StreamingHttpResponse)

    # First user hides picture to participants
    user.picture_public_participants = False
    user.save()

    # Picture still available as it's the default picture
    request = client.get(user.picture.url)
    assert isinstance(request, StreamingHttpResponse)

    user.picture.delete_sized_images()
    user.picture.save(
        "new_profile.png", ContentFile(open("app/static/favicon.png", "rb").read())
    )
    user.save()

    # Picture no longer available as it has changed and not available to participants
    request = client.get(user.picture.url)
    assert not isinstance(request, StreamingHttpResponse)

    # Logout, create another user as sponsor and login
    client.logout()
    password3 = factory.Faker("word")
    user3 = VerifiedUserFactory(
        password=factory.PostGenerationMethodCall("set_password", password3),
        type=UserType.SPONSOR.value,
    )
    client.login(username=user3.email, password=password3)

    # Picture still available
    request = client.get(user.picture.url)
    assert isinstance(request, StreamingHttpResponse)

    # First user hides picture to sponsors and recruiters
    user.picture_public_sponsors_and_recruiters = False
    user.save()

    # Picture no longer available as it's not available to sponsors or recruiters
    request = client.get(user.picture.url)
    assert not isinstance(request, StreamingHttpResponse)

    # Logout, create another user as organiser and login
    client.logout()
    password4 = factory.Faker("word")
    user4 = VerifiedUserFactory(
        password=factory.PostGenerationMethodCall("set_password", password4),
        type=UserType.ORGANISER.value,
    )
    client.login(username=user4.email, password=password4)

    # Picture still available as the user is an organiser
    request = client.get(user.picture.url)
    assert isinstance(request, StreamingHttpResponse)
