"""DRF uchun maxsus ruxsatlar (permissions)."""

from accounts.models import UserRole
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Faqat administrator roliga ega foydalanuvchilarga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == UserRole.ADMIN or request.user.is_superuser)
        )


class IsWarehouseManager(BasePermission):
    """Ombor mas'uli yoki administratorga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in (UserRole.ADMIN, UserRole.WAREHOUSE_MANAGER)
                or request.user.is_superuser
            )
        )


class IsProductionSupervisor(BasePermission):
    """Ishlab chiqarish nazoratchisi yoki administratorga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in (UserRole.ADMIN, UserRole.PRODUCTION_SUPERVISOR)
                or request.user.is_superuser
            )
        )


class IsProjectManager(BasePermission):
    """Loyiha mas'uli yoki administratorga ruxsat beradi."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in (UserRole.ADMIN, UserRole.PROJECT_MANAGER)
                or request.user.is_superuser
            )
        )
