# Generated by Django 2.2.4 on 2019-08-31 07:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("event", "0028_message")]

    operations = [
        migrations.AlterModelOptions(name="message", options={}),
        migrations.AddField(
            model_name="message",
            name="recipient_email",
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="message",
            name="recipient",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]