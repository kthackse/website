import factory
from django.utils import timezone

from app.models import File, FileVerified
from app.variables import HACKATHON_NAME
from event.enums import EventType
from event.models import Event
from page.models import Page, Category
from user.models import User


class UserFactory(factory.DjangoModelFactory):
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    email = factory.LazyAttribute(
        lambda u: "{0}.{1}@not-kthack.com".format(u.name, u.surname).lower()
    )

    class Meta:
        model = User


class VerifiedUserFactory(UserFactory):
    email_verified = True


class CategoryFactory(factory.DjangoModelFactory):
    title = factory.Faker("word")
    code = factory.LazyAttribute(lambda u: "{0}".format(u.title).lower())

    class Meta:
        model = Category


class PageFactory(factory.DjangoModelFactory):
    title = factory.Faker("sentence").generate({}).replace(".", "")
    code = factory.LazyAttribute(
        lambda u: "{0}".format(u.title).replace(" ", "-").lower()
    )
    content_plain = factory.Faker("paragraph")

    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = Page


class EventFactory(factory.DjangoModelFactory):
    name = HACKATHON_NAME
    code = factory.LazyAttribute(lambda u: "{0}".format(u.name).lower())
    description = factory.Faker("paragraph")
    type = EventType.HACKATHON.value
    starts_at = timezone.now() + timezone.timedelta(hours=10 * 24)
    ends_at = factory.LazyAttribute(
        lambda u: u.starts_at + timezone.timedelta(hours=2 * 24)
    )
    application_available = factory.LazyAttribute(
        lambda u: u.starts_at - timezone.timedelta(hours=5 * 24)
    )
    application_deadline = factory.LazyAttribute(
        lambda u: u.starts_at - timezone.timedelta(hours=2 * 24)
    )

    class Meta:
        model = Event


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = File


class FileVerifiedFactory(factory.DjangoModelFactory):
    class Meta:
        model = FileVerified
