"""Django ma'muriyat panelida foydalanuvchilarni boshqarish."""

from accounts.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Kengaytirilgan foydalanuvchi ma'muriyati."""

    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
    ]
    list_filter = ["role", "is_active", "is_staff"]
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "PROFUR Ma'lumotlari",
            {
                "fields": ("role", "phone"),
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "PROFUR Ma'lumotlari",
            {
                "fields": ("role", "phone"),
            },
        ),
    )
