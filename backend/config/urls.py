"""
URL configuration for PROFUR backend.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Loyiha holatini tekshirish uchun sog'liq (health) API nuqtasi."""
    return JsonResponse({"status": "ok", "service": "profur-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/auth/", include("accounts.urls")),
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/", include("apps.expenses.urls")),
    path("api/v1/", include("apps.inventory.urls")),
]
