import uuid

from django.db import models

from event.enums import EventType


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Name", max_length=255)
    code = models.CharField(verbose_name="Code", max_length=31, unique=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in EventType)
    )
