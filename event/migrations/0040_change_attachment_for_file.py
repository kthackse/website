# Generated by Django 2.2.4 on 2019-10-19 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("event", "0039_add_letter_type")]

    operations = [
        migrations.RemoveField(model_name="invoice", name="invoice"),
        migrations.RemoveField(model_name="message", name="attachment"),
        migrations.AddField(
            model_name="invoice",
            name="invoice",
            field=models.ForeignKey(
                default="", on_delete=django.db.models.deletion.PROTECT, to="app.File"
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="attachment",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.PROTECT,
                to="app.File",
                blank=True,
                null=True,
            ),
        ),
    ]
