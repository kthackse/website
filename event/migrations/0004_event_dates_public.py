# Generated by Django 2.2.3 on 2019-08-01 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("event", "0003_auto_20190801_1852")]

    operations = [
        migrations.AddField(
            model_name="event",
            name="dates_public",
            field=models.BooleanField(default=True),
        )
    ]
