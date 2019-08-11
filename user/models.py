import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField
from versatileimagefield.fields import VersatileImageField

from app.utils import is_email_organizer
from user.enums import UserType, DepartmentType, SexType


class UserManager(BaseUserManager):
    def create_participant(
        self, email, name, surname, password, phone, birthday, sex, city, country
    ):
        if not email:
            raise ValueError("A user must have an email")

        user = self.model(
            email=email,
            name=name,
            surname=surname,
            type=UserType.PARTICIPANT.value,
            phone=phone,
            birthday=birthday,
            sex=sex,
            city=city,
            country=country,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email,
        name,
        surname,
        type=UserType.PARTICIPANT.value,
        password=None,
        is_admin=False,
    ):
        if not email:
            raise ValueError("A user must have an email")

        user = self.model(
            email=email, name=name, surname=surname, type=type, is_admin=is_admin
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password):
        user = self.create_user(
            email, name, surname, UserType.ORGANISER.value, password, is_admin=True
        )
        # department = Department.objects.filter(type=DepartmentType.ADMIN.value).first()
        # if not department:
        #     department = Department(
        #         name="Admin", code="admin", type=DepartmentType.ADMIN.value
        #     )
        #     department.save(using=self._db)
        # user.departments.add(department)
        user.save(using=self._db)
        return user


def path_and_rename(instance, filename):
    """
    Stack Overflow
    Django ImageField change file name on upload
    https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
    """
    ext = filename.split(".")[-1]
    # get filename
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        # set filename as random string
        filename = "{}.{}".format(uuid.uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join("user/picture/", filename)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(verbose_name="First name", max_length=255)
    surname = models.CharField(verbose_name="Last name", max_length=255)

    email_verified = models.BooleanField(default=False)
    verify_key = models.CharField(max_length=127, blank=True, null=True)
    verify_expiration = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    type = models.PositiveSmallIntegerField(
        choices=((u.value, u.name) for u in UserType),
        default=UserType.PARTICIPANT.value,
    )
    is_admin = models.BooleanField(default=False)
    departments = models.ManyToManyField("Department", blank=True)
    company = models.ForeignKey(
        "Company", on_delete=models.PROTECT, null=True, blank=True
    )
    events = models.ManyToManyField("event.Event", blank=True)

    # Personal information
    picture = VersatileImageField(
        "Image", upload_to=path_and_rename, default="user/picture/profile.png"
    )
    picture_public_participants = models.BooleanField(default=True)
    picture_public_sponsors_and_recruiters = models.BooleanField(default=True)
    sex = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in SexType), default=SexType.NONE
    )
    birthday = models.DateField(blank=True, null=True)
    # TODO: Validate phone
    phone = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    @property
    def is_organiser(self):
        return self.type == UserType.ORGANISER.value

    @property
    def is_director(self):
        return self.is_admin or (
            self.type == UserType.ORGANISER.value
            and DepartmentType.DIRECTOR.value
            in self.departments.all().values_list("type", flat=True)
        )

    @property
    def is_sponsorship(self):
        return (
            self.is_admin
            or (
                self.type == UserType.ORGANISER.value
                and DepartmentType.DIRECTOR.value
                in self.departments.all().values_list("type", flat=True)
            )
            or (
                self.type == UserType.ORGANISER.value
                and DepartmentType.SPONSORSHIP.value
                in self.departments.all().values_list("type", flat=True)
            )
        )

    @property
    def is_participant(self):
        return self.type == UserType.PARTICIPANT.value

    @property
    def is_mentor(self):
        return self.type == UserType.MENTOR.value

    @property
    def is_sponsor(self):
        return self.type == UserType.SPONSOR.value

    @property
    def is_recruiter(self):
        return self.type == UserType.RECRUITER.value

    @property
    def is_media(self):
        return self.type == UserType.MEDIA.value

    @property
    def is_director(self):
        return DepartmentType.DIRECTOR.value in [d.type for d in self.departments.all()]

    @property
    def is_underage(self):
        # TODO: Check if underage correctly
        try:
            return (timezone.now().date() - self.birthday) < timezone.timedelta(
                days=365 * 18
            )
        except TypeError:
            return False

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.name + " " + self.surname

    def get_dict(self):
        return {
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "picture": self.picture,
            "picture_public_participants": self.picture_public_participants,
            "picture_public_sponsors_and_recruiters": self.picture_public_sponsors_and_recruiters,
            "sex": self.sex,
            "birthday": self.birthday,
            "phone": self.phone,
            "city": self.city,
            "country": self.country,
            "type": self.type,
            "departments": list(self.departments.all()),
        }

    def disable_verify(self):
        self.email_verified = False
        self.save()

    def update_verify(
        self, verify_key, verify_expiration=timezone.now() + timezone.timedelta(hours=1)
    ):
        self.verify_key = verify_key
        self.verify_expiration = verify_expiration
        self.save()

    def verify(self, verify_key):
        if timezone.now() <= self.verify_expiration and self.verify_key == verify_key:
            self.email_verified = True
            self.save()

    def clean(self):
        messages = dict()
        if not self.is_organiser and self.departments.count() > 0:
            messages[
                "departments"
            ] = "A user must be an organiser in order to belong to a department"
        if not (self.is_sponsor or self.is_recruiter) and self.company:
            messages[
                "company"
            ] = "A user must be a sponsor or a recruiter in order to belong to a company"
        # Check properly if 14 already or not
        if self.birthday and (
            timezone.now().date() - self.birthday
        ) < timezone.timedelta(days=14 * 365):
            messages["age"] = "The minimum age is 14"
        if messages:
            raise ValidationError(messages)

    def save(self, *args, **kwargs):
        self.clean()
        if is_email_organizer(self.email):
            self.type = UserType.ORGANISER.value
        # if self.picture:
        #    self.picture = self.picture.thumbnail["500x500"]
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
        # if (
        #     self.type is not DepartmentType.ADMIN.value
        #     and Department.objects.filter(type=DepartmentType.ADMIN.value).count() < 1
        # ):
        #     messages["type"] = "The admin department has to exist"
        if messages:
            raise ValidationError(messages)


def path_and_rename_company(instance, filename):
    """
    Stack Overflow
    Django ImageField change file name on upload
    https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
    """
    ext = filename.split(".")[-1]
    # get filename
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        # set filename as random string
        filename = "{}.{}".format(uuid.uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join("user/company/", filename)


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31, unique=True)
    logo = VersatileImageField("Image", upload_to=path_and_rename_company)
    website = models.URLField(blank=True, null=True)
    organisation_name = models.CharField(max_length=255, blank=True, null=True)
    organisation_number = models.CharField(max_length=255, blank=True, null=True)
    address_1 = models.CharField(max_length=255, blank=True, null=True)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    @property
    def org_name(self):
        if self.organisation_name:
            return self.organisation_name
        return self.name + " AB"

    def clean(self):
        messages = dict()
        if self.code in [c.code for c in Company.objects.all().exclude(id=self.id)]:
            messages["code"] = "The code for this company is already being used"
        if messages:
            raise ValidationError(messages)


class UserChange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.PROTECT)
    changed_by = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="changed_by"
    )
    field = models.CharField(max_length=255)
    value_previous = models.CharField(max_length=255, blank=True, null=True)
    value_current = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def is_changedbyuser(self):
        return self.user == self.changed_by
