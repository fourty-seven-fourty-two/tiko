from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model  # If used custom user model

from profiles import serializers as profile_serializers


class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = (permissions.AllowAny,)
    serializer_class = profile_serializers.UserSerializer
