"""Foydalanuvchi va rollarni boshqaruvchi ma'lumotlar modellari (OQ-037)."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    Foydalanuvchi rollari modeli.

    OQ-037 talabi bo'yicha administrator istalgan nomdagi yangi rollarni yaratishi,
    ruxsatlarini sozlashi va foydalanuvchiga bir nechta rol berishi mumkin.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Rol kodi"),
        help_text=_(
            "Tizimda tekshirish uchun unikal identifikator (masalan: ADMIN, WAREHOUSE_MANAGER)"
        ),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Rol nomi"),
        help_text=_("Foydalanuvchi interfeysida ko'rinadigan nom"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Tavsif"),
    )
    permissions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Ruxsatlar"),
        help_text=_(
            "Ruxsatlar ro'yxati (masalan: ['view_catalog', 'add_receipt', 'manage_users'])"
        ),
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name=_("Tizimli rol"),
        help_text=_(
            "Tizimning asosiy rollari tasodifan o'chirib yuborilmasligi uchun belgi"
        ),
    )

    class Meta:
        verbose_name = _("Rol")
        verbose_name_plural = _("Rollar")
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class User(AbstractUser):
    """
    Kengaytirilgan foydalanuvchi modeli.

    Foydalanuvchi bir vaqtning o'zida bir nechta rolga ega bo'lishi mumkin.
    """

    roles = models.ManyToManyField(
        Role,
        related_name="users",
        blank=True,
        verbose_name=_("Rollar"),
        help_text=_("Foydalanuvchiga biriktirilgan rollar"),
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Telefon raqami"),
    )

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")
        ordering = ["id"]

    def __str__(self) -> str:
        full_name = self.get_full_name()
        display = full_name if full_name else self.username
        roles_str = ", ".join(self.role_codes) if self.role_codes else "Rolsiz"
        return f"{display} [{roles_str}]"

    @property
    def role_codes(self) -> list[str]:
        """Foydalanuvchining barcha rollari kodlari ro'yxati."""
        return list(self.roles.values_list("code", flat=True))

    @property
    def primary_role(self) -> str:
        """Asosiy birinchi rol kodini qaytaradi (yoki WORKER)."""
        codes = self.role_codes
        return codes[0] if codes else "WORKER"

    @property
    def role(self) -> str:
        """Orqaga moslik uchun asosiy rol kodini qaytaradi."""
        return self.primary_role

    def has_role(self, role_code: str) -> bool:
        """Foydalanuvchida berilgan rol kodi borligini tekshiradi."""
        if self.is_superuser:
            return True
        return self.roles.filter(code=role_code).exists()

    def has_permission_code(self, permission_code: str) -> bool:
        """
        Foydalanuvchining rollari ichida berilgan ruxsat kodi borligini tekshiradi.
        Rol nomining o'zi vakolat bermaydi; ruxsat kodi yoki '*' bo'lishi shart.
        """
        if self.is_superuser:
            return True
        for role_obj in self.roles.all():
            perms = role_obj.permissions or []
            if "*" in perms or permission_code in perms:
                return True
            for perm in perms:
                if perm.endswith(".*"):
                    prefix = perm[:-2]
                    if permission_code == prefix or permission_code.startswith(
                        prefix + "."
                    ):
                        return True
        return False

    @property
    def is_admin_role(self) -> bool:
        """Administrator yoki superuser ekanligini tekshiradi."""
        return (
            self.is_superuser
            or self.has_permission_code("*")
            or self.has_permission_code("accounts.manage_users")
            or self.has_permission_code("accounts.manage_roles")
        )

    @property
    def is_warehouse_manager(self) -> bool:
        """Ombor mas'uli yoki admin ekanligini tekshiradi."""
        return (
            self.is_admin_role
            or self.has_permission_code("manage_inventory")
            or self.has_permission_code("inventory.view_stock")
            or self.has_permission_code("inventory.add_receipt")
        )

    @property
    def is_production_supervisor(self) -> bool:
        """Ishlab chiqarish nazoratchisi yoki admin ekanligini tekshiradi."""
        return (
            self.is_admin_role
            or self.has_permission_code("manage_production")
            or self.has_permission_code("production.*")
        )

    @property
    def is_project_manager(self) -> bool:
        """Loyiha mas'uli yoki admin ekanligini tekshiradi."""
        return (
            self.is_admin_role
            or self.has_permission_code("manage_projects")
            or self.has_permission_code("projects.*")
        )

    @property
    def is_worker(self) -> bool:
        """Ishchi ekanligini tekshiradi."""
        return self.has_role("WORKER")
