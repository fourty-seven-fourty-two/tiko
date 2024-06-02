from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from events import models as event_models
from profiles import serializers as profile_serializers


class EventSerializer(serializers.ModelSerializer):
    creator = profile_serializers.UserSerializer(read_only=True)
    attendees = profile_serializers.UserSerializer(many=True, read_only=True)

    class Meta:
        model = event_models.Event
        fields = (
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "creator",
            "attendees",
        )
        read_only_fields = ("id", "creator", "attendees")

    def validate_start_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Start time has to be in the future")
        return value

    def validate_end_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("End time has to be in the future")
        return value

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError(
                {"start_time": "Start time must be less than end time."}
            )
        return attrs

    def create(self, validated_data):
        return event_models.Event(
            title=validated_data["title"],
            description=validated_data["description"],
            start_time=validated_data["start_time"],
            end_time=validated_data["end_time"],
            creator=self.context["request"].user,
        )

    def update(self, instance: event_models.Event, validated_data):
        if not instance.is_upcoming():
            raise serializers.ValidationError(
                "Can't edit started or finished event", code="read_only_event"
            )

        if self.partial:
            self._partial_update(instance, validated_data)
        else:
            self._full_update(instance, validated_data)

        instance.save(update_fields=validated_data.keys())
        return instance

    def _partial_update(self, instance, validated_data):
        instance.title = validated_data.get("title")
        instance.description = validated_data.get("description", instance.description)
        instance.start_time = validated_data.get("start_time", instance.start_time)
        instance.end_time = validated_data.get("end_time", instance.end_time)

    def _full_update(self, instance, validated_data):
        instance.title = validated_data["title"]
        instance.description = validated_data["description"]
        instance.start_time = validated_data["start_time"]
        instance.end_time = validated_data["end_time"]

    def attend(self, instance: event_models.Event) -> event_models.Event:
        user = self.context["request"].user

        if not instance.is_upcoming():
            raise serializers.ValidationError(
                "Can't attend started or finished event", code="read_only_event"
            )

        with transaction.atomic():
            if user not in instance.attendees.all():
                if instance.attendees.count() == instance.capacity:
                    raise serializers.ValidationError(
                        "Event capacity is full", code="capacity_exhausted"
                    )
                self.instance.attendees.add(user)
                instance.refresh_from_db()
        return instance

    def cancel(self, instance: event_models.Event) -> event_models.Event:
        user = self.context["request"].user

        if not instance.is_upcoming():
            raise serializers.ValidationError(
                "Can't cancel started or finished event", code="read_only_event"
            )

        with transaction.atomic():
            if user in instance.attendees.all():
                self.instance.attendees.remove(user)
                instance.refresh_from_db()
        return instance
