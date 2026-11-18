"""Foydalanuvchi va uning rollarini boshqaruvchi ma'lumotlar modeli."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """PROFUR tizimidagi foydalanuvchi rollari."""

    ADMIN = "ADMIN", "Administrator"
    WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER", "Ombor mas'uli"
    PRODUCTION_SUPERVISOR = "PRODUCTION_SUPERVISOR", "Ishlab chiqarish nazoratchisi"
    PROJECT_MANAGER = "PROJECT_MANAGER", "Loyiha mas'uli"
    WORKER = "WORKER", "Ishchi"


class User(AbstractUser):
    """Kengaytirilgan foydalanuvchi modeli."""

    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.WORKER,
        verbose_name="Foydalanuvchi roli",
        help_text="Tizimdagi vakolat va ruxsatlar darajasini belgilaydi.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefon raqami",
    )

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["id"]

    def __str__(self) -> str:
        full_name = self.get_full_name()
        display = full_name if full_name else self.username
        return f"{display} ({self.get_role_display()})"

    @property
    def is_admin_role(self) -> bool:
        """Administrator yoki superuser ekanligini tekshiradi."""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_warehouse_manager(self) -> bool:
        """Ombor mas'uli yoki admin ekanligini tekshiradi."""
        return self.role == UserRole.WAREHOUSE_MANAGER or self.is_admin_role

    @property
    def is_production_supervisor(self) -> bool:
        """Ishlab chiqarish nazoratchisi yoki admin ekanligini tekshiradi."""
        return self.role == UserRole.PRODUCTION_SUPERVISOR or self.is_admin_role

    @property
    def is_project_manager(self) -> bool:
        """Loyiha mas'uli yoki admin ekanligini tekshiradi."""
        return self.role == UserRole.PROJECT_MANAGER or self.is_admin_role

    @property
    def is_worker(self) -> bool:
        """Ishchi ekanligini tekshiradi."""
        return self.role == UserRole.WORKER
