import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField

from application.enums import StatusType, SexType, DietType, TshirtSize
from user.enums import UserType


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("event.Event", on_delete=models.PROTECT)
    user = models.ForeignKey("user.User", on_delete=models.PROTECT)
    invited_by = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, blank=True, null=True
    )
    contacted_by = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in StatusType)
    )

    # Application details
    description = models.TextField(max_length=1000)
    projects = models.TextField(max_length=1000)

    # Reimbursement
    reimbursement_needed = models.BooleanField(default=False)
    reimbursement_amount = MoneyField(
        max_digits=7, decimal_places=2, default_currency="SEK", blank=True, null=True
    )

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

    class Meta:
        unique_together = ("event", "user")

    def is_invited(self):
        return self.invited_by is not None

    def is_contacted(self):
        return self.contacted_by is not None

    def is_underage(self):
        return self.age < 18

    def is_firsttimer(self):
        return (
            Application.objects.filter(
                user=self.user, status=StatusType.CONFIRMED.value
            )
            is None
        )

    def clean(self):
        messages = dict()
        if self.user.type != UserType.PARTICIPANT.value:
            messages["user"] = "The user needs to be a participant"
        if self.age < 14:
            messages["age"] = "The minimum age is 14"
        if messages:
            raise ValidationError(messages)
