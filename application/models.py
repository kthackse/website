import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField

from application.enums import (
    ApplicationStatus,
    DietType,
    TshirtSize,
    ReimbursementType,
    ReimbursementStatus,
)
from user.enums import UserType


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("event.Event", on_delete=models.PROTECT)
    user = models.ForeignKey("user.User", on_delete=models.PROTECT)
    invited_by = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, blank=True, null=True, related_name="invited_by"
    )
    contacted_by = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, blank=True, null=True, related_name="contacted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in ApplicationStatus)
    )

    # Application details
    description = models.TextField(max_length=1000)
    projects = models.TextField(max_length=1000)

    # Reimbursement
    money_needed = MoneyField(
        max_digits=7, decimal_places=2, default_currency="SEK", blank=True, null=True
    )

    # Location
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    # Resume
    resume = models.FileField(upload_to="resumes", null=True, blank=True)
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
    team = models.ForeignKey("Team", on_delete=models.PROTECT)

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
    applications = models.ManyToManyField("Application", blank=True, null=True)
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
