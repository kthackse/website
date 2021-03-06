# Generated by Django 2.2.3 on 2019-07-29 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
import versatileimagefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Offer",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=31, unique=True)),
                (
                    "logo",
                    versatileimagefield.fields.VersatileImageField(
                        upload_to="job/logo/", verbose_name="Image"
                    ),
                ),
                (
                    "type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "INTERNAL"), (1, "EXTERNAL")], default=0
                    ),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "DRAFT"),
                            (1, "PENDING_DRAFT"),
                            (2, "PUBLISHED"),
                            (3, "ARCHIVED"),
                            (4, "REMOVED"),
                        ],
                        default=0,
                    ),
                ),
                ("description", models.TextField(max_length=1000)),
                ("url", models.TextField(max_length=1000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="user.Company"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Application",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "PENDING"),
                            (1, "PENDING_ANSWER"),
                            (2, "ACCEPTED"),
                            (3, "REJECTED"),
                        ],
                        default=0,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "offer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="job.Offer"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="job_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
