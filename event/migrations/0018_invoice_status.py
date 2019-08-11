# Generated by Django 2.2.4 on 2019-08-11 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0017_invoice_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'DRAFT'), (1, 'SENT')], default=0),
        ),
    ]