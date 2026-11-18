"""Django ma'muriyat panelida foydalanuvchilar va rollarni boshqarish."""

from accounts.models import Role, User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Rollar boshqaruvi (OQ-037)."""

    list_display = ["name", "code", "is_system"]
    list_filter = ["is_system"]
    search_fields = ["name", "code", "description"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Kengaytirilgan foydalanuvchi ma'muriyati."""

    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "primary_role",
        "is_active",
        "is_staff",
    ]
    list_filter = ["roles", "is_active", "is_staff"]
    filter_horizontal = ["roles", "groups", "user_permissions"]
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "PROFUR Ma'lumotlari",
            {
                "fields": ("roles", "phone"),
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "PROFUR Ma'lumotlari",
            {
                "fields": ("roles", "phone"),
            },
        ),
    )
