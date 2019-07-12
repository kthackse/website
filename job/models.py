import uuid

from django.db import models

from job.enums import OfferStatus, ApplicationStatus


class Offer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31, unique=True)
    created_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    company = models.ForeignKey("user.Company", on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in OfferStatus),
        default=OfferStatus.DRAFT.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("user.User", on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in ApplicationStatus),
        default=OfferStatus.DRAFT.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)

