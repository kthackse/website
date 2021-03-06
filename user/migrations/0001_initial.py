# Generated by Django 2.2.3 on 2019-07-29 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import user.enums
import user.models
import uuid
import versatileimagefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=255, verbose_name="First name")),
                ("surname", models.CharField(max_length=255, verbose_name="Last name")),
                ("email_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "PARTICIPANT"),
                            (1, "ORGANISER"),
                            (2, "VOLUNTEER"),
                            (3, "MENTOR"),
                            (4, "SPONSOR"),
                            (5, "RECRUITER"),
                            (6, "MEDIA"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "picture",
                    versatileimagefield.fields.VersatileImageField(
                        default="user/picture/profile.png",
                        upload_to=user.models.path_and_rename,
                        verbose_name="Image",
                    ),
                ),
                ("picture_public_participants", models.BooleanField(default=True)),
                (
                    "picture_public_sponsors_and_recruiters",
                    models.BooleanField(default=True),
                ),
                (
                    "sex",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "NONE"), (1, "FEMALE"), (2, "MALE")],
                        default=user.enums.SexType(0),
                    ),
                ),
                ("birthday", models.DateField(blank=True, null=True)),
                ("phone", models.CharField(blank=True, max_length=255, null=True)),
                ("city", models.CharField(blank=True, max_length=255, null=True)),
                ("country", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Company",
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
            ],
            options={"verbose_name_plural": "Companies"},
        ),
        migrations.CreateModel(
            name="Department",
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
                    "type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "ADMIN"),
                            (1, "DIRECTOR"),
                            (2, "DESIGN"),
                            (3, "FINANCE"),
                            (4, "FUNDRAISING"),
                            (5, "HACKERXPERIENCE"),
                            (6, "LOGISTICS"),
                            (7, "MARKETING"),
                            (8, "PHOTOGRAPHY"),
                            (9, "STAFF"),
                            (10, "WEBDEV"),
                        ]
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserChange",
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
                ("field", models.CharField(max_length=255)),
                (
                    "value_previous",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("value_current", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "changed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="changed_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="user.Company",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="departments",
            field=models.ManyToManyField(blank=True, to="user.Department"),
        ),
    ]
