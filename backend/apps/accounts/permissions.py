"""DRF uchun ruxsat kodlari asosidagi tekshiruvlar."""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Rol boshqaruvini administratorga ochadi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_role
        )


class HasPermissionCode(BasePermission):
    """Ko‘rinish yoki sinf belgilagan ruxsatni foydalanuvchi rollaridan tekshiradi."""

    required_permission = ""

    def has_permission(self, request, view) -> bool:
        code = getattr(view, "required_permission", self.required_permission)
        return bool(
            request.user
            and request.user.is_authenticated
            and code
            and request.user.has_permission_code(code)
        )


class IsWarehouseManager(HasPermissionCode):
    """Ombor boshqaruvi ruxsatini tekshiradi."""

    required_permission = "manage_inventory"


class IsProductionSupervisor(HasPermissionCode):
    """Ishlab chiqarishni boshqarish ruxsatini tekshiradi."""

    required_permission = "manage_production"


class IsProjectManager(HasPermissionCode):
    """Loyihalarni boshqarish ruxsatini tekshiradi."""

    required_permission = "manage_projects"
