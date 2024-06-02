from drf_spectacular.utils import extend_schema
from rest_framework import decorators, pagination, permissions, response, viewsets

from events import filters as events_filters
from events import models as events_models
from events import permissions as events_permissions
from events import serializers as events_serializers


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = (
        events_models.Event.objects.all()
        .select_related("creator")
        .prefetch_related("attendees")
        .order_by(
            "start_time",
        )
    )
    serializer_class = events_serializers.EventSerializer
    filterset_class = events_filters.EventsListFilter

    def get_permissions(self):
        classes = self.permission_classes
        if self.action == "update":
            classes += (events_permissions.IsEventOwner,)
        return [permission() for permission in classes]

    @extend_schema(
        responses={204: None},
    )
    @decorators.action(
        methods=[
            "POST",
        ],
        detail=True,
        url_path="attend",
    )
    def attend(self, request, *args, **kwargs):
        """
        Adds user to attendance list. This is noop action - if user is in the list,
        request is ignored
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        serializer.attend(instance)

        return response.Response(status=204)

    @extend_schema(
        responses={204: None},
    )
    @decorators.action(
        methods=[
            "POST",
        ],
        detail=True,
        url_path="cancel",
    )
    def cancel(self, request, *args, **kwargs):
        """
        Excludes user from attendance list. This is noop action - if user not in the list,
        request is ignored
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        serializer.cancel(instance)

        return response.Response(status=204)
