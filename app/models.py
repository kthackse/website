import uuid

from django.db import models
from django.utils import timezone

from app.enums import FileType, FileStatus, FileVerificationStatus


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to="file")
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in FileType), default=FileType.INVOICE.value
    )
    status = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in FileStatus), default=FileStatus.VALID.value
    )
    # 8 digit non-random control code based on ID and time of creation
    verification_control = models.CharField(max_length=255)
    # 32 digit random verification code
    verification_code = models.CharField(max_length=255)
    verification_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("verification_control", "verification_code")

    def save(self, *args, **kwargs):
        self.clean()
        self.verification_control = "".join(
            8 * [str(int(self.id) % int(timezone.now().strftime("%Y%m%d%H%M%S")))]
        )[:8]
        self.verification_code = str(uuid.uuid4()).replace("-", "").upper()
        self.verification_until = timezone.now() + timezone.timedelta(days=90)
        return super().save(*args, **kwargs)


class FileVerified(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey("File", on_delete=models.CASCADE, null=True, blank=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    status = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in FileVerificationStatus),
        default=FileVerificationStatus.FAILED.value,
    )
    verification_control = models.CharField(max_length=255, blank=True, null=True)
    verification_code = models.CharField(max_length=255, blank=True, null=True)
    verified_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.clean()
        self.file = File.objects.filter(
            verification_until__date__gte=timezone.now().date(),
            verification_control=self.verification_control,
            verification_code=self.verification_code,
        ).first()
        if self.file:
            self.status = FileVerificationStatus.SUCCESS
        return super().save(*args, **kwargs)
