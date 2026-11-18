"""Ombor yozuvlari admin'da faqat ko'rish uchun: o'zgartirish API va xizmatlar orqali."""

from django.contrib import admin

from .models import Batch, StockBalance, StockMovement


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Batch)
class BatchAdmin(ReadOnlyAdmin):
    list_display = [
        "id",
        "material",
        "received_on",
        "quantity",
        "quantity_remaining",
        "unit_price",
        "currency",
    ]
    list_filter = ["received_on"]
    search_fields = ["material__name", "supplier", "document_number"]


@admin.register(StockBalance)
class StockBalanceAdmin(ReadOnlyAdmin):
    list_display = ["material", "quantity_on_hand", "updated_at"]
    search_fields = ["material__name"]


@admin.register(StockMovement)
class StockMovementAdmin(ReadOnlyAdmin):
    list_display = [
        "created_at",
        "type",
        "material",
        "quantity",
        "quantity_on_hand_after",
        "created_by",
    ]
    list_filter = ["type"]
    search_fields = ["material__name"]
