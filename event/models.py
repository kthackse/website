import uuid

from django.core.exceptions import ValidationError
from django.db import models

from event.enums import EventType, EventApplicationStatus


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField( max_length=255)
    code = models.CharField(max_length=31, unique=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in EventType)
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
