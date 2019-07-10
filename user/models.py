import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone

from user.enums import GroupType, DepartmentType


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    name = models.CharField(verbose_name="First name", max_length=255)
    surname = models.CharField(verbose_name="Last name", max_length=255)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    group = models.ForeignKey("Group", on_delete=models.PROTECT, null=True)
    departments = models.ManyToManyField("Department", null=True)
    company = models.ForeignKey("Company", on_delete=models.PROTECT, null=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def is_organiser(self):
        return self.group.type == GroupType.ORGANISER.value

    def is_participant(self):
        return self.group.type == GroupType.PARTICIPANT.value

    def is_sponsor(self):
        return self.group.type == GroupType.SPONSOR.value

    def is_media(self):
        return self.group.type == GroupType.MEDIA.value

    def is_admin(self):
        return DepartmentType.ADMIN.value in [d.type for d in self.departments.all()]

    def is_director(self):
        return DepartmentType.DIRECTOR.value in [d.type for d in self.departments.all()]

    def clean(self):
        messages = dict()
        if not self.group:
            messages["group"] = "An user must belong to a group"
        if not self.is_organiser() and self.departments.count() > 0:
            messages["departments"] = "An user must be an organiser in order to belong to a department"
        if not self.is_sponsor() and self.company:
            messages["company"] = "An user must be a sponsor in order to belong to a company"
        if messages:
            raise ValidationError(messages)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Name", max_length=255)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in GroupType),
        default=GroupType.PARTICIPANT.value,
    )


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Name", max_length=255)
    code = models.CharField(verbose_name="Code", max_length=31, unique=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in GroupType),
        default=GroupType.PARTICIPANT.value,
    )

    def clean(self):
        messages = dict()
        if self.code in [d.code for d in Department.objects.all()]:
            messages["code"] = "The code for this department is already being used"
        if self.type in [d.type for d in Department.objects.all()]:
            messages["type"] = "There can be at most one department per type"
        if messages:
            raise ValidationError(messages)


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Name", max_length=255)
    code = models.CharField(verbose_name="Code", max_length=31, unique=True)

    def clean(self):
        messages = dict()
        if self.code in [c.code for c in Company.objects.all()]:
            messages["code"] = "The code for this company is already being used"
        if messages:
            raise ValidationError(messages)
