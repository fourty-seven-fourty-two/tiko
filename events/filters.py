from django.utils import timezone
from django_filters import rest_framework as filters

EVENT_STATUS_CHOICES = (
    ("upcoming", "Upcoming"),
    ("past", "Past"),
    ("ongoing", "Ongoing"),
)


class EventsListFilter(filters.FilterSet):
    starts_before = filters.DateTimeFilter(field_name="start_time", lookup_expr="lte")
    starts_after = filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")

    attending = filters.BooleanFilter(method="filter_by_attending")
    created = filters.BooleanFilter(method="filter_by_created")

    status = filters.ChoiceFilter(
        choices=EVENT_STATUS_CHOICES, method="filter_by_status"
    )

    sort = filters.OrderingFilter(fields=(("start_time", "start_time"),))

    def filter_by_attending(self, queryset, name, value):
        return queryset.filter(attendees__in=[self.request.user])

    def filter_by_created(self, queryset, name, value):
        return queryset.filter(creator=self.request.user)

    def filter_by_status(self, queryset, name, value):
        now = timezone.now()
        match value:
            case "upcoming":
                return queryset.filter(start_time__gte=now)
            case "past":
                return queryset.filter(end_time__lte=now)
            case "ongoing":
                return queryset.filter(start_time__lte=now, end_time__gte=now)
        return queryset
