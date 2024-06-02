import pytest
from rest_framework_simplejwt.tokens import Token, RefreshToken

from tests import const, factories

pytestmark = pytest.mark.django_db


def test_auth_with_token(api_client):
    user = factories.UserFactory()
    response = api_client.post(
        "/v1/profile/token/",
        {"username": user.username, "password": const.DEFAULT_PASSWORD},
    )
    assert response.status_code == 200, response.content
    assert "refresh" in response.json()
    assert "access" in response.json()
