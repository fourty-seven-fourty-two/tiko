# Generated by Django 5.0.6 on 2024-06-02 18:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_event_created_at"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name="event",
            index=models.Index(
                fields=["start_time", "end_time"], name="event_start_t_849dac_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["created_at"], name="event_created_989bde_idx"),
        ),
    ]
