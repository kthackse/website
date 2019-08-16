import factory
import pytest
from django.http import HttpResponseNotFound, HttpResponse
from django.test import Client
from django.urls import reverse

from app.tests.factories import PageFactory, VerifiedUserFactory
from app.variables import HACKATHON_APP_NAME


@pytest.mark.django_db
def test_public():
    page = PageFactory()

    # Page public and unpublished by default
    assert page.public
    assert not page.published

    # Create a client
    client = Client()

    # Page is not available as it's not published
    request = client.get(reverse("page_page", kwargs=dict(category=page.category.code, code=page.code)))
    assert isinstance(request, HttpResponseNotFound)

    # Page is now published
    page.published = True
    page.save()

    # Page is now available as it has been published
    request = client.get(reverse("page_page", kwargs=dict(category=page.category.code, code=page.code)))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert "<title>" + page.title + " | " + HACKATHON_APP_NAME + "</title>" in content
    assert "<h1>" + page.title + "</h1>" in content
    assert page.content_plain in content

    # Page requires now login
    page.public = False
    page.save()

    # Page is not available as it's not public
    request = client.get(reverse("page_page", kwargs=dict(category=page.category.code, code=page.code)))
    assert isinstance(request, HttpResponseNotFound)

    # Create a user and login
    password = factory.Faker("word")
    user = VerifiedUserFactory(password=factory.PostGenerationMethodCall('set_password', password))
    client.login(username=user.email, password=password)

    # Page is now available after login
    request = client.get(reverse("page_page", kwargs=dict(category=page.category.code, code=page.code)))
    assert isinstance(request, HttpResponse)
    assert request.status_code == 200
    content = request.content.decode("utf-8")
    assert "<title>" + page.title + " | " + HACKATHON_APP_NAME + "</title>" in content
    assert "<h1>" + page.title + "</h1>" in content
    assert page.content_plain in content
