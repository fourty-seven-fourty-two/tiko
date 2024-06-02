import uuid

from django.conf import settings
from django.core import validators
from django.db import models
from django.utils import timezone


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
    )

    title = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        validators=[validators.MinLengthValidator(1)],
    )
    description = models.TextField(null=False, blank=False)

    capacity = models.PositiveIntegerField(
        default=1,
        null=False,
        blank=True,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(1000000),
        ],
    )  # max number of attendees

    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="accepted_events"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event"
        indexes = [
            models.Index(fields=["start_time", "end_time"]),
            models.Index(fields=["created_at"]),
        ]

    def is_upcoming(self):
        return timezone.now() < self.start_time
