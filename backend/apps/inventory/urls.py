"""Ombor API manzillari: receipts, issues, returns, write-offs, stock, movements."""

from rest_framework.routers import SimpleRouter

from .approval_views import StockReturnViewSet, WriteOffViewSet
from .issue_views import StockIssueViewSet
from .notification_views import NotificationViewSet
from .stock_views import MovementViewSet, StockViewSet
from .views import ReceiptViewSet

app_name = "inventory"

router = SimpleRouter()
router.register("notifications", NotificationViewSet, basename="notification")
router.register("receipts", ReceiptViewSet, basename="receipt")
router.register("issues", StockIssueViewSet, basename="issue")
router.register("returns", StockReturnViewSet, basename="return")
router.register("write-offs", WriteOffViewSet, basename="write-off")
router.register("stock", StockViewSet, basename="stock")
router.register("movements", MovementViewSet, basename="movement")

urlpatterns = router.urls
