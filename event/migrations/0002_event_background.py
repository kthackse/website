# Generated by Django 2.2.3 on 2019-07-30 17:16

from django.db import migrations, models
import event.models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='background',
            field=models.FileField(default='', upload_to=event.models.path_and_rename_background),
            preserve_default=False,
        ),
    ]