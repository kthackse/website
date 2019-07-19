import os
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from versatileimagefield.fields import VersatileImageField

from event.enums import EventType, EventApplicationStatus, ApplicationStatus, DietType, TshirtSize, ReimbursementType, \
    ReimbursementStatus
from user.enums import UserType

from djmoney.models.fields import MoneyField


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
    return os.path.join("event/picture/", filename)


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField( max_length=255)
    code = models.CharField(max_length=31, unique=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in EventType)
    )
    picture = VersatileImageField(
        "Image", upload_to=path_and_rename
    )
    # TODO: Divide sponsors into categories
    city = models.CharField(max_length=255, default="Stockholm")
    country = models.CharField(max_length=255, default="Sweden")
    sponsors = models.ManyToManyField("user.Company", blank=True, null=True, related_name="sponsors")
    partners = models.ManyToManyField("user.Company", blank=True, null=True, related_name="partners")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    published = models.BooleanField(default=False)
    application_status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in EventApplicationStatus),
        default=EventApplicationStatus.PENDING.value
    )
    application_deadline = models.DateTimeField()
    custom_home = models.BooleanField(default=False)

    def clean(self):
        messages = dict()
        if Event.objects.filter(starts_at__lte=self.ends_at, ends_at__gte=self.starts_at).exclude(id=self.id).exists():
            temporal_overlap = "There's another event already taking place for the selected range of dates"
            messages["starts_at"] = temporal_overlap
            messages["ends_at"] = temporal_overlap
        if self.application_deadline > self.ends_at:
            messages["application_deadline"] = "The application deadline can't be after the event has ended"
        if messages:
            raise ValidationError(messages)


class ScheduleEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    event = models.ForeignKey("Event", on_delete=models.PROTECT)
    important = models.BooleanField(default=False)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(blank=True, null=True)

    def clean(self):
        messages = dict()
        if self.starts_at < self.event.starts_at:
            messages[
                "starts_at"
            ] = "The schedule event can't start before the event itself"
        if self.ends_at and self.ends_at > self.event.ends_at:
            messages[
                "ends_at"
            ] = "The schedule event can't end after the event itself"
        if messages:
            raise ValidationError(messages)


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("event.Event", on_delete=models.PROTECT)
    user = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, related_name="event_user"
    )
    invited_by = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="invited_by",
    )
    contacted_by = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="contacted_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in ApplicationStatus)
    )

    # Application details
    description = models.TextField(max_length=1000)
    projects = models.TextField(max_length=1000)
    newbie = models.BooleanField(default=False)

    # Reimbursement
    money_needed = MoneyField(
        max_digits=7, decimal_places=2, default_currency="SEK", blank=True, null=True
    )

    # Resume
    resume_available = models.BooleanField(default=False)

    # University
    university = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    graduation_year = models.PositiveIntegerField(default=timezone.now().year)

    # URLs
    github = models.URLField(blank=True, null=True)
    devpost = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Swag
    diet = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in DietType)
    )
    diet_other = models.CharField(max_length=255, blank=True, null=True)
    tshirt = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in TshirtSize)
    )
    hardware = models.CharField(max_length=255, null=True, blank=True)

    # Team
    team = models.ForeignKey("Team", on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        unique_together = ("event", "user")

    def is_invited(self):
        return self.invited_by is not None

    def is_contacted(self):
        return self.contacted_by is not None

    def is_firsttimer(self):
        return (
            Application.objects.filter(
                user=self.user, status=ApplicationStatus.CONFIRMED.value
            )
            is None
        )

    def is_reimbursementneeded(self):
        return self.money_needed.amount > Decimal(0.0)

    def clean(self):
        messages = dict()
        if self.user.type != UserType.PARTICIPANT.value:
            messages["user"] = "The user needs to be a participant"
        if self.team and self.team.event != self.event:
            messages["team"] = "The team needs to be from the same edition"
        if messages:
            raise ValidationError(messages)


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("event.Event", on_delete=models.PROTECT)
    creator = models.ForeignKey("user.User", on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31)
    lemma = models.CharField(max_length=127, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("event", "creator"), ("event", "code"))


def valid_vote(vote):
    return 0 <= vote <= 10


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey("Application", on_delete=models.PROTECT)
    voted_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    # Vote result
    vote_tech = models.IntegerField(validators=[valid_vote])
    vote_personal = models.SmallIntegerField(validators=[valid_vote])
    vote_total = models.FloatField()

    class Meta:
        unique_together = ("application", "voted_by")

    def clean(self):
        messages = dict()
        if not self.voted_by.is_organiser():
            messages["user"] = "A user must be an organiser in order to vote"
        if messages:
            raise ValidationError(messages)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey("Application", on_delete=models.PROTECT)
    commented_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)

    def clean(self):
        messages = dict()
        if not self.commented_by.is_organiser():
            messages["user"] = "A user must be an organiser in order to make a comment"
        if messages:
            raise ValidationError(messages)


class Reimbursement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applications = models.ManyToManyField("Application")
    reimbursed_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    # Money
    money_assigned = MoneyField(
        max_digits=7, decimal_places=2, default_currency="SEK", blank=True, null=True
    )
    comment = models.TextField(max_length=1000)

    # Details
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in ReimbursementType)
    )
    receipt = models.FileField(null=True, blank=True, upload_to="receipt")
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in ReimbursementStatus)
    )
    expires_at = models.DateTimeField()

    # TODO: Check only one reimbursement per application
