import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField

from app.utils import is_email_organizer
from user.enums import UserType, DepartmentType, SexType


class UserManager(BaseUserManager):
    def create_user(
        self, email, name, surname, type=UserType.PARTICIPANT.value, password=None
    ):
        if not email:
            raise ValueError("A user must have an email")

        user = self.model(email=email, name=name, surname=surname, type=type)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password):
        user = self.create_user(
            email, name, surname, UserType.ORGANISER.value, password
        )
        department = Department.objects.filter(type=DepartmentType.ADMIN.value).first()
        if not department:
            department = Department(
                name="Admin", code="admin", type=DepartmentType.ADMIN.value
            )
            department.save(using=self._db)
        user.departments.add(department)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(verbose_name="First name", max_length=255)
    surname = models.CharField(verbose_name="Last name", max_length=255)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    type = models.PositiveSmallIntegerField(
        choices=((u.value, u.name) for u in UserType),
        default=UserType.PARTICIPANT.value,
    )
    departments = models.ManyToManyField("Department")
    company = models.ForeignKey(
        "Company", on_delete=models.PROTECT, null=True, blank=True
    )

    # Personal information
    sex = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in SexType), default=SexType.NONE
    )
    age = models.IntegerField(default=18, blank=True, null=True)
    phone = PhoneNumberField()
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def is_organiser(self):
        return self.type == UserType.ORGANISER.value

    def is_participant(self):
        return self.type == UserType.PARTICIPANT.value

    def is_mentor(self):
        return self.type == UserType.MENTOR.value

    def is_sponsor(self):
        return self.type == UserType.SPONSOR.value

    def is_recruiter(self):
        return self.type == UserType.RECRUITER.value

    def is_media(self):
        return self.type == UserType.MEDIA.value

    def is_admin(self):
        return DepartmentType.ADMIN.value in [d.type for d in self.departments.all()]

    def is_director(self):
        return DepartmentType.DIRECTOR.value in [d.type for d in self.departments.all()]

    def is_underage(self):
        return self.age < 18

    @property
    def is_staff(self):
        return self.is_organiser()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.name + " " + self.surname

    def clean(self):
        messages = dict()
        if not self.is_organiser() and self.departments.count() > 0:
            messages[
                "departments"
            ] = "A user must be an organiser in order to belong to a department"
        if (not self.is_sponsor() or not self.is_recruiter()) and self.company:
            messages[
                "company"
            ] = "A user must be a sponsor or a recruiter in order to belong to a company"
        if self.age < 14:
            messages["age"] = "The minimum age is 14"
        if messages:
            raise ValidationError(messages)

    def save(self, *args, **kwargs):
        self.clean()
        if is_email_organizer(self.email):
            self.type = UserType.ORGANISER.value
        return super().save(*args, **kwargs)


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31, unique=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in DepartmentType)
    )

    def __str__(self):
        return self.name

    def clean(self):
        messages = dict()
        if self.code in [d.code for d in Department.objects.all().exclude(id=self.id)]:
            messages["code"] = "The code for this department is already being used"
        if self.type in [d.type for d in Department.objects.all().exclude(id=self.id)]:
            messages["type"] = "There can be at most one department per type"
        if (
            self.type is not DepartmentType.ADMIN.value
            and Department.objects.filter(type=DepartmentType.ADMIN.value).count() == 1
        ):
            messages["type"] = "The admin department has to exist"
        if messages:
            raise ValidationError(messages)


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31, unique=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    def clean(self):
        messages = dict()
        if self.code in [c.code for c in Company.objects.all().exclude(id=self.id)]:
            messages["code"] = "The code for this company is already being used"
        if messages:
            raise ValidationError(messages)
