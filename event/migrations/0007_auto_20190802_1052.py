# Generated by Django 2.2.3 on 2019-08-02 08:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [("user", "0004_auto_20190802_1046"), ("event", "0006_subscriber")]

    operations = [
        migrations.AlterModelOptions(
            name="scheduleevent",
            options={
                "verbose_name": "Schedule in event",
                "verbose_name_plural": "Schedules     in events",
            },
        ),
        migrations.RemoveField(model_name="event", name="partners"),
        migrations.RemoveField(model_name="event", name="sponsors"),
        migrations.AddField(
            model_name="event",
            name="companies_public",
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name="CompanyEvent",
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
                    "tier",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (10, "TERA"),
                            (20, "GIGA"),
                            (30, "MEGA"),
                            (40, "KILO"),
                            (50, "MILI"),
                            (60, "PARTNER"),
                            (70, "SUPPORT"),
                        ]
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="user.Company"
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="event.Event"
                    ),
                ),
            ],
            options={
                "verbose_name": "Company in event",
                "verbose_name_plural": "Companies in events",
                "unique_together": {("event", "company")},
            },
        ),
    ]
