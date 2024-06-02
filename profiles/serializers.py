from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        UserModel = get_user_model()

        user = UserModel.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )

        return user

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "password", "email")
        write_only_fields = ("password",)
        read_only_fields = ("id",)
