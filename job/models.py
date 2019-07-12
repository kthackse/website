import uuid

from django.core.exceptions import ValidationError
from django.db import models
from versatileimagefield.fields import VersatileImageField

from job.enums import OfferStatus, ApplicationStatus, OfferType


class Offer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31, unique=True)
    logo = VersatileImageField("Image", upload_to="job/logo/")
    created_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    company = models.ForeignKey("user.Company", on_delete=models.PROTECT)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in OfferType), default=OfferType.INTERNAL.value
    )
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in OfferStatus),
        default=OfferStatus.DRAFT.value,
    )
    description = models.TextField(max_length=1000)
    url = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer = models.ForeignKey("Offer", on_delete=models.PROTECT)
    user = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, related_name="job_user"
    )
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in ApplicationStatus),
        default=OfferStatus.DRAFT.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        messages = dict()
        if self.offer.type == OfferType.EXTERNAL.value:
            messages[
                "offer"
            ] = "An application can only be made to an internal job offer"
        if messages:
            raise ValidationError(messages)
