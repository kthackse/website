from unittest import mock

import pytest
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from app.tests.factories import EventFactory
from app.variables import HACKATHON_APP_NAME
from event.utils import get_next_or_past_event


@pytest.mark.django_db
def test_home():
    # No future events
    assert not get_next_or_past_event()

    # Create client
    client = Client()

    # Home page doesn't contain any events
    request = client.get(reverse("app_home"))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert HACKATHON_APP_NAME in content
    assert "No events" in content
    assert reverse("user_login") in content
    assert reverse("user_signup") in content

    # Create event
    event = EventFactory()

    # No events are yet available, event is not published by default
    assert not get_next_or_past_event()

    # Publish previous created event
    event.published = True
    event.save()

    # One event is now available
    assert get_next_or_past_event()

    # Home page contains next event information
    request = client.get(reverse("app_home"))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert event.name + " " + str(event.starts_at.year) in content
    assert "will open soon" in content
    assert "Subscribe" in content

    # Make the dates of the event public
    event.dates_public = True
    event.save()

    # Home page contains next event dates
    request = client.get(reverse("app_home"))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert str(event.starts_at.day + 1) in content
    assert str(event.ends_at.day + 1) in content

    # Hide the subscribe form
    event.subscribe_public = False
    event.save()

    # Home page does no longer contain the subscribe form
    request = client.get(reverse("app_home"))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert not "Subscribe" in content

    with mock.patch(
        "django.utils.timezone.now",
        return_value=timezone.now() + timezone.timedelta(days=6),
    ):
        # Applications are now open on the home page
        request = client.get(reverse("app_home"))
        assert isinstance(request, HttpResponse)
        assert request.status_code == 200
        content = request.content.decode("utf-8")
        assert "Apply now" in content

    with mock.patch(
        "django.utils.timezone.now",
        return_value=timezone.now() + timezone.timedelta(days=9),
    ):
        # Applications have now been closed on the home page
        request = client.get(reverse("app_home"))
        assert isinstance(request, HttpResponse)
        assert request.status_code == 200
        content = request.content.decode("utf-8")
        print(content)
        assert "closed" in content
        assert "for next time" in content
