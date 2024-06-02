import pytest

pytestmark = pytest.mark.django_db


def test_signup(api_client):
    username = "user"
    password = "password"
    email = "test@example.com"

    response = api_client.post(
        "/v1/profile/signup/",
        {"username": username, "password": password, "email": email},
    )
    assert response.status_code == 201, response.data
