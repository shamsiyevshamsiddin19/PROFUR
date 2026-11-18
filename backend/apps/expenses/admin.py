"""Xarajatlarni Django admin panelida ko'rish."""

from django.contrib import admin

from .models import Expense, ExpenseType


@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    """Xarajat turlarini qo'shish, tahrirlash va faolsizlantirish."""

    list_display = ["code", "name_uz", "name_ru", "name_en", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "name_uz", "name_ru", "name_en"]

    def has_delete_permission(self, request, obj=None) -> bool:
        """Turni o'chirishni yopadi: tarix uchun u faqat faolsizlantiriladi."""
        return False


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Xarajatlarni faqat ko'rish uchun: yozuvlar o'zgartirilmaydi va o'chirilmaydi."""

    list_display = ["spent_on", "expense_type", "amount", "currency", "project_id"]
    list_filter = ["expense_type", "spent_on"]
    search_fields = ["note"]

    def has_change_permission(self, request, obj=None) -> bool:
        """Mavjud xarajatni tahrirlashni yopadi (TZ 6.8)."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Xarajatni o'chirishni yopadi (TZ 6.8)."""
        return False
