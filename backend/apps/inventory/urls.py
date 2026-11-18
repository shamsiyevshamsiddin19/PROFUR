"""Ombor API manzillari: /api/v1/receipts/, /stock/, /movements/."""

from rest_framework.routers import SimpleRouter

from .stock_views import MovementViewSet, StockViewSet
from .views import ReceiptViewSet

app_name = "inventory"

router = SimpleRouter()
router.register("receipts", ReceiptViewSet, basename="receipt")
router.register("stock", StockViewSet, basename="stock")
router.register("movements", MovementViewSet, basename="movement")

urlpatterns = router.urls
