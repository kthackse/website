# Generated by Django 2.2.4 on 2019-10-20 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("event", "0042_allow_null_letter_responsible")]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="status",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "DRAFT"), (1, "SENT"), (2, "SIGNED"), (3, "CANCELLED")],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="letter",
            name="status",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "DRAFT"), (1, "SENT"), (2, "SIGNED"), (3, "CANCELLED")],
                default=0,
            ),
        ),
    ]
