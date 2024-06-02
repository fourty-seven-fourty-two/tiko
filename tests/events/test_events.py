from datetime import timedelta

import pytest
from django.utils import timezone

from events import models as events_models

from tests import factories
from tests.utils import authenticate


pytestmark = pytest.mark.django_db


@pytest.fixture()
def sequential_events():
    """
    Generates 4 events, starting from now:
    - starting right now
    - starting in 2 hours
    - starting in 5 hours
    - starting in 1 day
    """
    now = timezone.now()

    # create events in non-linear order to avoid false positive scenarios
    event1 = factories.EventFactory(
        start_time=now,
    )
    event4 = factories.EventFactory(
        start_time=now + timedelta(days=1),
    )
    event2 = factories.EventFactory(
        start_time=now + timedelta(hours=2),
    )
    event3 = factories.EventFactory(
        start_time=now + timedelta(hours=5),
    )

    return event1, event2, event3, event4


def to_event_id_list(*events: events_models.Event) -> list[str]:
    return list(map(str, [e.pk for e in events]))


class TestEventsList:
    def test_empty_list(self, api_client, user):
        authenticate(api_client, user)
        response = api_client.get("/v1/events/")
        assert response.status_code == 200
        assert response.json()["results"] == []

    def test_sorting(self, authenticated_client, sequential_events):
        event1, event2, event3, event4 = sequential_events

        expected_ids = to_event_id_list(event1, event2, event3, event4)

        response = authenticated_client.get("/v1/events/", {"sort": "start_time"})
        assert response.status_code == 200
        assert [entry["id"] for entry in response.json()["results"]] == expected_ids

        # reverse order
        response = authenticated_client.get("/v1/events/", {"sort": "-start_time"})
        assert response.status_code == 200
        assert [entry["id"] for entry in response.json()["results"]] == list(
            reversed(expected_ids)
        )

    def test_filter_by_start_date(self, authenticated_client, sequential_events):
        now = timezone.now()
        event1, event2, event3, event4 = sequential_events

        # narrow amount of events to three
        response = authenticated_client.get(
            "/v1/events/", {"starts_before": (now + timedelta(hours=10)).isoformat()}
        )
        assert response.status_code == 200
        assert [
            entry["id"] for entry in response.json()["results"]
        ] == to_event_id_list(event1, event2, event3)

        # narrow amount of events to one
        response = authenticated_client.get(
            "/v1/events/",
            {
                "starts_before": (now + timedelta(hours=10)).isoformat(),
                "starts_after": (now + timedelta(hours=3)).isoformat(),
            },
        )
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["id"] == str(event3.pk)

    def test_filter_by_status(self, api_client, user):
        authenticate(api_client, user)

        now = timezone.now()

        past_event = factories.EventFactory(
            start_time=now - timedelta(hours=2), end_time=now - timedelta(hours=1)
        )
        ongoing_event = factories.EventFactory(
            start_time=now - timedelta(hours=2), end_time=now + timedelta(hours=1)
        )
        upcoming_event = factories.EventFactory(
            start_time=now + timedelta(hours=2), end_time=now + timedelta(hours=3)
        )

        response = api_client.get("/v1/events/", {"status": "past"})
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["id"] == str(past_event.pk)

        response = api_client.get("/v1/events/", {"status": "ongoing"})
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["id"] == str(ongoing_event.pk)

        response = api_client.get("/v1/events/", {"status": "upcoming"})
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["id"] == str(upcoming_event.pk)

    def test_only_attending(self, api_client, user, sequential_events):
        authenticate(api_client, user)
        event = factories.EventFactory()
        event.attendees.add(user)
        response = api_client.get("/v1/events/", {"attending": True})
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["id"] == str(event.pk)

    def test_only_created(self, api_client, user, sequential_events):
        authenticate(api_client, user)
        event = factories.EventFactory()
        event.attendees.add(user)

        created_event = factories.EventFactory(creator=user)
        response = api_client.get("/v1/events/", {"created": True})
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["results"][0]["id"] == str(created_event.pk)

    def test_list_pagination(self, api_client, user, sequential_events):
        authenticate(api_client, user)

        response = api_client.get("/v1/events/", {"offset": 1, "limit": 2})

        assert response.status_code == 200
        assert response.json()["count"] == 4
        assert len(response.json()["results"]) == 2
        assert response.json()["results"][0]["id"] == str(sequential_events[1].pk)
        assert response.json()["results"][1]["id"] == str(sequential_events[2].pk)


class TestResponseToEvents:
    def test_accept_event(self, api_client, user):
        authenticate(api_client, user)

        event = factories.EventFactory(capacity=1, start_time=timezone.now() + timedelta(hours=2))
        response = api_client.get("/v1/events/", {"attending": True})
        assert response.status_code == 200
        assert response.json()["count"] == 0

        response = api_client.post(f"/v1/events/{event.pk}/attend/")
        assert response.status_code == 204

        # make sure action is no-op
        response = api_client.post(f"/v1/events/{event.pk}/attend/")
        assert response.status_code == 204

        response = api_client.get("/v1/events/", {"attending": True})
        assert response.status_code == 200
        assert response.json()["count"] == 1

        user2 = factories.UserFactory()
        authenticate(api_client, user2)
        response = api_client.post(f"/v1/events/{event.pk}/attend/")
        assert response.status_code == 400

    def test_cancel_event(self, api_client, user):
        authenticate(api_client, user)

        event = factories.EventFactory(start_time=timezone.now() + timedelta(hours=2))
        event.attendees.add(user)
        response = api_client.get("/v1/events/", {"attending": True})
        assert response.status_code == 200
        assert response.json()["count"] == 1

        response = api_client.post(f"/v1/events/{event.pk}/cancel/")
        assert response.status_code == 204

        # test action is no-op
        response = api_client.post(f"/v1/events/{event.pk}/cancel/")
        assert response.status_code == 204

        response = api_client.get("/v1/events/", {"attending": True})
        assert response.status_code == 200
        assert response.json()["count"] == 0


class TestCreateEvent:
    def test_create_event(self, authenticated_client):
        response = authenticated_client.post(
            "/v1/events/",
            {
                "title": "test event",
                "description": "test event",
                "start_time": (timezone.now() + timedelta(hours=2)).isoformat(),
                "end_time": (timezone.now() + timedelta(hours=3)).isoformat(),
                "capacity": 1,
            },
        )
        assert response.status_code == 201

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "title": "test event",
                "description": "test event",
                "start_time": (timezone.now() + timedelta(hours=2)).isoformat(),
                "end_time": (timezone.now() + timedelta(hours=1)).isoformat(),
            },
            {
                "title": "test event",
                "description": "test event",
                "start_time": (timezone.now() - timedelta(hours=2)).isoformat(),
                "end_time": (timezone.now() + timedelta(hours=1)).isoformat(),
            },
        ],
    )
    def test_fields_validation(self, authenticated_client, payload):
        response = authenticated_client.post("/v1/events/", payload)
        assert response.status_code == 400


class TestUpdateEvent:
    def test_update_event(self, api_client, user):
        authenticate(api_client, user)

        title = "title"
        description = "description"
        start_time = (timezone.now() + timedelta(hours=2)).isoformat()
        end_time = (timezone.now() + timedelta(hours=3)).isoformat()
        capacity = 1

        event = factories.EventFactory(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            capacity=capacity,
            creator=user,
        )

        updated_title = "updated_title"
        updated_description = "updated_description"
        updated_start_time = (timezone.now() + timedelta(hours=5)).isoformat()
        updated_end_time = (timezone.now() + timedelta(hours=10)).isoformat()
        updated_capacity = 10

        response = api_client.put(
            f"/v1/events/{event.pk}/",
            {
                "title": updated_title,
                "description": updated_description,
                "start_time": updated_start_time,
                "end_time": updated_end_time,
                "capacity": updated_capacity,
            },
        )
        assert response.status_code == 200

    def test_update_event_permissions(self, authenticated_client):
        event = factories.EventFactory()

        # update of the event that doesn't belong to current user doesn't work
        response = authenticated_client.put(f"/v1/events/{event.pk}/", {})
        assert response.status_code == 403
