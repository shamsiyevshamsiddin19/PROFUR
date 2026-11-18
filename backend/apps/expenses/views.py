"""Xarajatlar API'sining manzillari uchun view'lar.

Xarajat yozuvlari o'chirilmaydi va tahrirlanmaydi (TZ 6.8), shuning uchun
``ExpenseViewSet`` faqat ko'rish va yaratishga ruxsat beradi. ``PUT``,
``PATCH`` va ``DELETE`` so'rovlariga 405 qaytadi.

Ruxsatlar jamoa qoidasi bo'yicha ``accounts.permissions.HasPermissionCode``
orqali tekshiriladi: kod foydalanuvchi rolidagi ``Role.permissions``
ro'yxatida bo'lishi kerak (docs/06-api-contract/auth-api.md).

``POST`` (yaratish va ``reverse``) ``Idempotency-Key`` sarlavhasini qabul
qiladi: internet uzilib so'rov qayta yuborilsa, ikkinchi xarajat yozilmaydi.
Qoida ombor API'si bilan bir xil va o'sha kalitlar jadvalidan foydalanadi.
Sarlavha hozircha ixtiyoriy (eski mijozlar buzilmasligi uchun).
"""

from accounts.permissions import HasPermissionCode
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ErrorDetail
from rest_framework.request import Request
from rest_framework.response import Response

from apps.inventory.issue_views import IdempotentCreateMixin

from . import services
from .models import Expense, ExpenseType
from .serializers import (
    ExpenseFilterSerializer,
    ExpenseReverseSerializer,
    ExpenseSerializer,
    ExpenseTypeSerializer,
)

REVERSE_MESSAGES = {
    "already_reversed": _("Bu xarajat avval bekor qilingan."),
    "reversal_not_reversible": _("Teskari yozuvni bekor qilib bo'lmaydi."),
}


class ExpenseConflictError(APIException):
    """409: xarajatni bekor qilib bo'lmaydi (``already_reversed`` va boshqalar)."""

    status_code = status.HTTP_409_CONFLICT

    def __init__(self, code: str):
        """Xato kodiga mos tarjima qilingan matn bilan javob tuzadi."""
        super().__init__(
            {"detail": ErrorDetail(str(REVERSE_MESSAGES[code]), code), "code": code}
        )


class ActionPermissionMixin:
    """Har bir DRF amali uchun alohida ruxsat kodini tanlaydi.

    ``HasPermissionCode`` view'dan bitta ``required_permission`` kutadi. Bu
    mixin uni joriy amalga qarab ``action_permissions`` lug'atidan oladi.
    Manzilda yo'q metod (``DELETE`` kabi) uchun ko'rish ruxsati so'raladi:
    ko'ra oladigan foydalanuvchi 405, qolganlar 403 oladi.
    """

    permission_classes = [HasPermissionCode]
    action_permissions: dict[str, str] = {}
    view_permission = ""

    @property
    def required_permission(self) -> str:
        """Joriy amal uchun kerakli ruxsat kodini qaytaradi."""
        return self.action_permissions.get(self.action, self.view_permission)


class ExpenseTypeViewSet(
    ActionPermissionMixin,
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
    http_method_names = ["get", "post", "patch", "head", "options"]
    view_permission = "expenses.view_expensetype"
    action_permissions = {
        "create": "expenses.add_expensetype",
        "partial_update": "expenses.change_expensetype",
    }

    def get_queryset(self) -> QuerySet[ExpenseType]:
        """Turlarni qaytaradi; ``?is_active=true`` bo'lsa faqat faollarini."""
        queryset = ExpenseType.objects.all()
        if self.request.query_params.get("is_active") == "true":
            queryset = queryset.filter(is_active=True)
        return queryset


class ExpenseViewSet(
    IdempotentCreateMixin,
    ActionPermissionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Qo'shimcha xarajatlar: ro'yxat (filtr bilan), bitta yozuv va yangi yozuv."""

    serializer_class = ExpenseSerializer
    idempotency_endpoint = "expenses:create"
    view_permission = "expenses.view_expense"
    action_permissions = {
        "create": "expenses.add_expense",
        "reverse": "expenses.reverse_expense",
    }

    def get_queryset(self) -> QuerySet[Expense]:
        """Xarajatlarni qaytaradi; ro'yxatda so'rovdagi filtrlarni qo'llaydi.

        Noto'g'ri filtr qiymati (masalan, sana formati) 400 xato beradi.
        """
        queryset = Expense.objects.select_related("expense_type", "reversal")
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

    def replay_body(self, body: dict, user) -> dict:
        """Xarajat javobida yashiriladigan narx maydoni yo'q: tana o'zgarmaydi."""
        return body

    def run_once(self, request: Request, endpoint: str, perform) -> Response:
        """Kalit bo'lsa ``perform`` ni idempotent bajaradi, bo'lmasa oddiy bajaradi.

        ``perform`` javob tanasini qaytaradi. Kalitsiz so'rov ham bitta
        tranzaksiyada bajariladi, javob ``201``.
        """
        if "Idempotency-Key" not in request.headers:
            with transaction.atomic():
                return Response(perform(), status=status.HTTP_201_CREATED)
        self.idempotency_endpoint = endpoint
        return self.idempotent_create(request, perform)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Xarajat yozadi. ``Idempotency-Key`` bilan qayta yuborish ikkinchisini yozmaydi."""

        def perform() -> dict:
            """Tanani tekshiradi, xarajatni saqlaydi va javob tanasini qaytaradi."""
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return serializer.data

        return self.run_once(request, "expenses:create", perform)

    @action(detail=True, methods=["post"])
    def reverse(self, request: Request, pk: str | None = None) -> Response:
        """Xarajatni teskari yozuv bilan bekor qiladi (TZ 6.8, BR-12).

        Javob ``201``: ``{"reversal": {...}, "replacement": {...} | null}``.
        Asl yozuv o'zgarmaydi. Ikkinchi marta bekor qilish — 409; xuddi shu
        ``Idempotency-Key`` bilan qayta yuborilsa — birinchi javob ``200``.
        """
        expense = self.get_object()

        def perform() -> dict:
            """Sababni tekshiradi, teskari (va yangi) yozuvni saqlaydi."""
            body = ExpenseReverseSerializer(
                data=request.data, context={"request": request}
            )
            body.is_valid(raise_exception=True)
            try:
                reversal, replacement = services.reverse_expense(
                    expense=expense,
                    reason=body.validated_data["reason"],
                    replacement=body.validated_data.get("replacement"),
                    user=request.user,
                )
            except services.ExpenseNotReversibleError as error:
                raise ExpenseConflictError(error.code) from error
            context = self.get_serializer_context()
            return {
                "reversal": ExpenseSerializer(reversal, context=context).data,
                "replacement": (
                    ExpenseSerializer(replacement, context=context).data
                    if replacement
                    else None
                ),
            }

        return self.run_once(request, f"expenses:reverse:{expense.pk}", perform)
