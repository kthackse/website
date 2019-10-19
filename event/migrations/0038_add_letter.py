# Generated by Django 2.2.4 on 2019-10-18 21:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('event', '0037_event_logo_white'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='sent_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_sent_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=31)),
                ('letter', models.FileField(blank=True, null=True, upload_to='letter')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'DRAFT'), (1, 'SIGNED'), (2, 'SENT'), (3, 'CANCELLED')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.Application')),
                ('responsible', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('sent_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='letter_sent_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]