import factory

from page.models import Page, Category
from user.models import User


class UserFactory(factory.DjangoModelFactory):
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda u: "{0}@not-kthack.com".format(u.name).lower())

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
