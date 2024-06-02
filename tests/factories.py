from datetime import timedelta

import factory.fuzzy
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from tests import const


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ("email",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"email{n}@test.com")
    password = const.DEFAULT_PASSWORD

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs["password"] = make_password(kwargs["password"])
        return super(UserFactory, cls)._create(model_class, *args, **kwargs)


class EventFactory(factory.django.DjangoModelFactory):
    creator = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Event {n}")
    description = factory.Sequence(lambda n: f"Event {n} description")
    capacity = 10
    start_time = timezone.now()
    end_time = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now() + timedelta(hours=1),
        end_dt=timezone.now() + timedelta(hours=10),
    )

    class Meta:
        model = "events.Event"
