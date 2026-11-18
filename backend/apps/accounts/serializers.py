"""Foydalanuvchi va rollar ma'lumotlarini seriyalashtiruvchi serializerlar."""

from accounts.models import Role, User
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    """Rol ma'lumotlarini seriyalashtiruvchi serializer (OQ-037)."""

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "description",
            "permissions",
            "is_system",
        ]
        read_only_fields = ["id"]


class UserSerializer(serializers.ModelSerializer):
    """Foydalanuvchi profil ma'lumotlarini qaytaruvchi serializer."""

    roles = RoleSerializer(many=True, read_only=True)
    role_codes = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )
    primary_role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "roles",
            "role_codes",
            "primary_role",
            "phone",
            "is_active",
            "is_superuser",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "role_codes",
            "primary_role",
            "is_superuser",
        ]


class LoginSerializer(serializers.Serializer):
    """Tizimga kirish ma'lumotlarini tekshiruvchi serializer."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                _("Login yoki parol noto'g'ri kiritildi.")
            )
        if not user.is_active:
            raise serializers.ValidationError(_("Ushbu hisob faolsizlantirilgan."))

        attrs["user"] = user
        return attrs
