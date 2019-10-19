# Generated by Django 2.2.4 on 2019-10-19 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_add_status_and_codes'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='verification_until',
            field=models.DateTimeField(default='2019-10-01 00:00'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together={('verification_control', 'verification_code')},
        ),
    ]
