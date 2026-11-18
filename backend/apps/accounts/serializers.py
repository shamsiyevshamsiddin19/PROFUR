"""Foydalanuvchi va rollar ma'lumotlarini seriyalashtiruvchi serializerlar."""

from accounts.models import Role, User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    """Rol ma'lumotlarini seriyalashtiruvchi serializer (OQ-037)."""

    permissions = serializers.ListField(
        child=serializers.CharField(allow_blank=False), required=False
    )

    def validate_code(self, value):
        if (
            self.instance
            and (self.instance.is_system or self.instance.code == "ADMIN")
            and value != self.instance.code
        ):
            raise serializers.ValidationError(
                _("Tizimli rol kodini o'zgartirib bo'lmaydi.")
            )
        return value

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
        read_only_fields = ["id", "is_system"]


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
            existing_user = User.objects.filter(username=username).first()
            if (
                existing_user
                and existing_user.check_password(password)
                and not existing_user.is_active
            ):
                raise serializers.ValidationError(_("Ushbu hisob faolsizlantirilgan."))
            raise serializers.ValidationError(
                _("Login yoki parol noto'g'ri kiritildi.")
            )
        if not user.is_active:
            raise serializers.ValidationError(_("Ushbu hisob faolsizlantirilgan."))

        attrs["user"] = user
        return attrs


class UserAdminCreateSerializer(serializers.ModelSerializer):
    """Admin tomonidan yangi foydalanuvchi yaratish (OQ-040)."""

    password = serializers.CharField(write_only=True, required=True, min_length=6)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        required=False,
        write_only=True,
        source="roles",
    )
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
            "password",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role_ids",
            "roles",
            "role_codes",
            "primary_role",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined", "role_codes", "primary_role", "roles"]

    def validate(self, attrs):
        """Yangi akkaunt parolini loyiha sozlamalaridagi validatorlar bilan tekshiradi."""
        candidate = User(
            **{
                key: attrs.get(key, "")
                for key in ("username", "email", "first_name", "last_name")
            }
        )
        try:
            validate_password(attrs["password"], candidate)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": error.messages}) from error
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        if roles:
            user.roles.set(roles)
        return user


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """Admin tomonidan foydalanuvchini tahrirlash va rollarni almashtirish (OQ-040)."""

    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        required=False,
        write_only=True,
        source="roles",
    )
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
            "phone",
            "role_ids",
            "roles",
            "role_codes",
            "primary_role",
            "is_active",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "date_joined",
            "role_codes",
            "primary_role",
            "roles",
        ]

    def validate(self, attrs):
        actor = self.context["request"].user
        if self.instance.pk == actor.pk:
            if attrs.get("is_active") is False:
                raise serializers.ValidationError(
                    {"is_active": _("O'z hisobingizni faolsizlantira olmaysiz.")}
                )
            roles = attrs.get("roles")
            if (
                roles is not None
                and not actor.is_superuser
                and not any(role.code == "ADMIN" for role in roles)
            ):
                raise serializers.ValidationError(
                    {"role_ids": _("O'zingizdan ADMIN rolini olib tashlay olmaysiz.")}
                )
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if validated_data:
            instance.save(update_fields=list(validated_data))
        if roles is not None:
            instance.roles.set(roles)
        return instance


class PasswordResetSerializer(serializers.Serializer):
    """Admin tomonidan foydalanuvchi parolini tiklash (OQ-040)."""

    new_password = serializers.CharField(write_only=True, required=True, min_length=6)

    def validate_new_password(self, value):
        if not value or len(value.strip()) < 6:
            raise serializers.ValidationError(
                _("Yangi parol kamida 6 ta belgidan iborat bo'lishi kerak.")
            )
        try:
            validate_password(value, self.context.get("user"))
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error
        return value
