# Generated by Django 2.2.4 on 2019-10-19 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("app", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="fileverified",
            name="ip",
            field=models.CharField(blank=True, max_length=255, null=True),
        )
    ]
