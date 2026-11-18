"""Katalog API manzillari: /api/v1/categories/ va /api/v1/materials/."""

from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, MaterialViewSet

app_name = "catalog"

router = SimpleRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("materials", MaterialViewSet, basename="material")

urlpatterns = router.urls
