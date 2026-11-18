"""Ombor API manzillari: /api/v1/receipts/."""

from rest_framework.routers import SimpleRouter

from .views import ReceiptViewSet

app_name = "inventory"

router = SimpleRouter()
router.register("receipts", ReceiptViewSet, basename="receipt")

urlpatterns = router.urls
