"""Xarajatlar API'sining manzillari uchun view'lar.

Xarajat yozuvlari o'chirilmaydi va tahrirlanmaydi (TZ 6.8), shuning uchun
``ExpenseViewSet`` faqat ko'rish va yaratishga ruxsat beradi. ``PUT``,
``PATCH`` va ``DELETE`` so'rovlariga 405 qaytadi.
"""

from django.db.models import QuerySet
from rest_framework import mixins, viewsets

from .models import Expense, ExpenseType
from .permissions import HasActionPermission
from .serializers import (
    ExpenseFilterSerializer,
    ExpenseSerializer,
    ExpenseTypeSerializer,
)


class ExpenseTypeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Xarajat turlari: ro'yxat, bitta tur, yangi tur va tahrirlash (PATCH).

    Tur o'chirilmaydi: uni yashirish uchun ``is_active=false`` yuboriladi.
    """

    serializer_class = ExpenseTypeSerializer
    permission_classes = [HasActionPermission]
    http_method_names = ["get", "post", "patch", "head", "options"]
    required_permissions = {
        "list": ["expenses.view_expensetype"],
        "retrieve": ["expenses.view_expensetype"],
        "create": ["expenses.add_expensetype"],
        "partial_update": ["expenses.change_expensetype"],
    }

    def get_queryset(self) -> QuerySet[ExpenseType]:
        """Turlarni qaytaradi; ``?is_active=true`` bo'lsa faqat faollarini."""
        queryset = ExpenseType.objects.all()
        if self.request.query_params.get("is_active") == "true":
            queryset = queryset.filter(is_active=True)
        return queryset


class ExpenseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Qo'shimcha xarajatlar: ro'yxat (filtr bilan), bitta yozuv va yangi yozuv."""

    serializer_class = ExpenseSerializer
    permission_classes = [HasActionPermission]
    required_permissions = {
        "list": ["expenses.view_expense"],
        "retrieve": ["expenses.view_expense"],
        "create": ["expenses.add_expense"],
    }

    def get_queryset(self) -> QuerySet[Expense]:
        """Xarajatlarni qaytaradi; ro'yxatda so'rovdagi filtrlarni qo'llaydi.

        Noto'g'ri filtr qiymati (masalan, sana formati) 400 xato beradi.
        """
        queryset = Expense.objects.select_related("expense_type")
        if self.action != "list":
            return queryset

        filters = ExpenseFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        params = filters.validated_data
        if "expense_type" in params:
            queryset = queryset.filter(expense_type__code=params["expense_type"])
        if "project_id" in params:
            queryset = queryset.filter(project_id=params["project_id"])
        if "date_from" in params:
            queryset = queryset.filter(spent_on__gte=params["date_from"])
        if "date_to" in params:
            queryset = queryset.filter(spent_on__lte=params["date_to"])
        return queryset

    def perform_create(self, serializer: ExpenseSerializer) -> None:
        """Yangi xarajatni saqlaydi va uni kiritgan foydalanuvchini yozib qo'yadi."""
        serializer.save(created_by=self.request.user)
