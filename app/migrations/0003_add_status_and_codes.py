# Generated by Django 2.2.4 on 2019-10-19 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_fileverified_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileverified',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'SUCCESS'), (1, 'FAILED')], default=1),
        ),
        migrations.AddField(
            model_name='fileverified',
            name='verification_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fileverified',
            name='verification_control',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='fileverified',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.File'),
        ),
    ]
