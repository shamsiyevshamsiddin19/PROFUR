"""Ombor API manzillari: /api/v1/receipts/, /issues/, /stock/, /movements/."""

from rest_framework.routers import SimpleRouter

from .issue_views import StockIssueViewSet
from .stock_views import MovementViewSet, StockViewSet
from .views import ReceiptViewSet

app_name = "inventory"

router = SimpleRouter()
router.register("receipts", ReceiptViewSet, basename="receipt")
router.register("issues", StockIssueViewSet, basename="issue")
router.register("stock", StockViewSet, basename="stock")
router.register("movements", MovementViewSet, basename="movement")

urlpatterns = router.urls
