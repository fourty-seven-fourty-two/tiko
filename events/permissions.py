from rest_framework.permissions import BasePermission

from events import models as event_models


class IsEventOwner(BasePermission):

    def has_object_permission(self, request, view, obj: event_models.Event) -> bool:
        return request.user == obj.creator
