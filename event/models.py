import uuid

from django.core.exceptions import ValidationError
from django.db import models

from event.enums import EventType


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Name", max_length=255)
    code = models.CharField(verbose_name="Code", max_length=31, unique=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in EventType)
    )
    # TODO: Divide sponsors into categories
    sponsors = models.ManyToManyField("Company")
    partners = models.ManyToManyField("Company")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()


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
                "starts_at"
            ] = "The schedule event can't end after the event itself"
        if messages:
            raise ValidationError(messages)
