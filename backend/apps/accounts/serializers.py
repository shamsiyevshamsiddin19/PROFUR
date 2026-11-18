"""Foydalanuvchi ma'lumotlarini seriyalashtiruvchi serializerlar."""

from accounts.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Foydalanuvchi profil ma'lumotlarini qaytaruvchi serializer."""

    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_display",
            "phone",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined", "role_display"]


class LoginSerializer(serializers.Serializer):
    """Tizimga kirish ma'lumotlarini tekshiruvchi serializer."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Login yoki parol noto'g'ri kiritildi.")
        if not user.is_active:
            raise serializers.ValidationError("Ushbu hisob faolsizlantirilgan.")

        attrs["user"] = user
        return attrs
