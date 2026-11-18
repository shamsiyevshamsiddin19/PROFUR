"""DRF uchun maxsus ruxsatlar (permissions)."""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Faqat administrator roliga ega foydalanuvchilarga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_role
        )


class IsWarehouseManager(BasePermission):
    """Ombor mas'uli yoki administratorga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_warehouse_manager
        )


class IsProductionSupervisor(BasePermission):
    """Ishlab chiqarish nazoratchisi yoki administratorga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_production_supervisor
        )


class IsProjectManager(BasePermission):
    """Loyiha mas'uli yoki administratorga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_project_manager
        )
