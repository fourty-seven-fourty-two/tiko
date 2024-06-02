import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory
from tests.utils import authenticate


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture()
def authenticated_client(api_client, user):
    authenticate(api_client, user)
    return api_client
