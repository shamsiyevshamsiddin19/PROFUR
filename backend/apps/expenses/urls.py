"""Xarajatlar API'si manzillari. ``config/urls.py`` da ``api/v1/`` ostiga ulanadi.

- ``expense-types/`` va ``expense-types/<id>/`` — xarajat turlari
- ``expenses/`` va ``expenses/<id>/`` — xarajat yozuvlari
"""

from rest_framework.routers import SimpleRouter

from .views import ExpenseTypeViewSet, ExpenseViewSet

router = SimpleRouter()
router.register("expense-types", ExpenseTypeViewSet, basename="expense-type")
router.register("expenses", ExpenseViewSet, basename="expense")

urlpatterns = router.urls
