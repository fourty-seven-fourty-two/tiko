from rest_framework_simplejwt.tokens import RefreshToken


def authenticate(client, user):
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
