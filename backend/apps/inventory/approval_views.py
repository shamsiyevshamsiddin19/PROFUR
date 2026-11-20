"""Tasdiqlanadigan ombor so'rovlari API'si (PCRM-44).

- ``/api/v1/returns/`` — qaytarish (OQ-003): ombor mas'uli tasdiqlaydi.
- ``/api/v1/write-offs/`` — hisobdan chiqarish (OQ-007): admin tasdiqlaydi.

So'rov yaratish (``POST``) ``Idempotency-Key`` bilan bir marta bajariladi.
``POST {id}/approve/`` va ``POST {id}/reject/`` takrorlansa, ikkinchi harakat
yozilmaydi: joriy holat 200 bilan qaytadi. Qarama-qarshi qaror — 409.
So'rovlar o'zgartirilmaydi va o'chirilmaydi (``PUT``/``PATCH``/``DELETE`` — 405).
"""

from accounts.permissions import HasPermissionCode
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.catalog.access import is_shop_worker, visible_materials

from . import services
from .approval_serializers import (
    DecisionSerializer,
    ReturnCreateSerializer,
    ReturnSerializer,
    WriteOffCreateSerializer,
    WriteOffSerializer,
)
from .issue_views import (
    CONFLICT_ERRORS,
    IdempotentCreateMixin,
    conflict_from,
    int_query_param,
)
from .models import RequestStatus, StockReturn, WriteOff
from .views import query_param_date

VIEW_STOCK = "inventory.view_stock"


def status_param(request: Request) -> str | None:
    """``?status=pending|approved|rejected`` filtrini o'qiydi; noto'g'ri bo'lsa 400."""
    value = request.query_params.get("status")
    if value and value not in RequestStatus.values:
        raise ValidationError(
            {"status": [ErrorDetail(str(_("Noma'lum holat.")), code="invalid_choice")]}
        )
    return value or None


class ApprovalRequestViewSet(
    IdempotentCreateMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Qaytarish va hisobdan chiqarish uchun umumiy oqim: so'rov, tasdiq, rad.

    Voris view quyidagilarni belgilaydi: ``create_serializer_class``,
    ``action_permissions`` (``create``/``approve``/``reject``),
    ``request_service``, ``approve_service``, ``reject_service`` va
    ``idempotency_endpoint``. Ko'rish uchun ``inventory.view_stock`` kerak.
    """

    permission_classes = [HasPermissionCode]
    http_method_names = ["get", "post", "head", "options"]
    create_serializer_class = None
    action_permissions: dict[str, str] = {}

    @property
    def required_permission(self) -> str:
        """Joriy amalga mos ruxsat kodi; boshqa amallar uchun ko'rish ruxsati."""
        return self.action_permissions.get(self.action, VIEW_STOCK)

    def filter_common(self, queryset: QuerySet) -> QuerySet:
        """``status``, ``date_from`` va ``date_to`` (yaratilgan sana) filtrlari."""
        if state := status_param(self.request):
            queryset = queryset.filter(status=state)
        if date_from := query_param_date(self.request, "date_from"):
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to := query_param_date(self.request, "date_to"):
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset

    def respond(self, obj, response_status: int = status.HTTP_200_OK) -> Response:
        """So'rovni bazadan qayta o'qib, javob shaklida qaytaradi."""
        fresh = self.get_queryset().get(pk=obj.pk)
        data = self.get_serializer(fresh).data
        return Response(data, status=response_status)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """So'rov yozadi. Qoldiq o'zgarmaydi; limit/qoldiq yetmasa 409."""
        serializer = self.create_serializer_class(
            data=request.data, context={"request": request}
        )

        def perform() -> dict:
            """Tanani tekshiradi, so'rovni saqlaydi va javob tanasini qaytaradi."""
            serializer.is_valid(raise_exception=True)
            try:
                obj = self.request_service(
                    user=request.user, **serializer.service_kwargs()
                )
            except CONFLICT_ERRORS as error:
                raise conflict_from(error) from error
            return self.respond(obj).data

        return self.idempotent_create(request, perform)

    def decide(self, request: Request, pk: str, service) -> Response:
        """Qarorni servis orqali bajaradi va so'rovning yangi holatini qaytaradi."""
        target = self.get_object()
        decision = DecisionSerializer(data=request.data)
        decision.is_valid(raise_exception=True)
        try:
            obj, _changed = service(
                target.pk, user=request.user, note=decision.validated_data["note"]
            )
        except CONFLICT_ERRORS as error:
            raise conflict_from(error) from error
        return self.respond(obj)

    @action(detail=True, methods=["post"])
    def approve(self, request: Request, pk: str | None = None) -> Response:
        """So'rovni tasdiqlaydi; qoldiq shu paytda o'zgaradi (bir marta)."""
        return self.decide(request, pk, self.approve_service)

    @action(detail=True, methods=["post"])
    def reject(self, request: Request, pk: str | None = None) -> Response:
        """So'rovni rad etadi; qoldiq o'zgarmaydi."""
        return self.decide(request, pk, self.reject_service)


class StockReturnViewSet(ApprovalRequestViewSet):
    """Qaytarishlar (OQ-003). Filtrlar: ``issue``, ``material``, ``status``, sana."""

    serializer_class = ReturnSerializer
    create_serializer_class = ReturnCreateSerializer
    idempotency_endpoint = "returns:create"
    action_permissions = {
        "create": "inventory.add_return",
        "approve": "inventory.approve_return",
        "reject": "inventory.approve_return",
    }

    def get_queryset(self) -> QuerySet[StockReturn]:
        """Qaytarishlarni asl chiqim, partiyalar va foydalanuvchilar bilan qaytaradi."""
        queryset = StockReturn.objects.select_related(
            "issue__material", "created_by", "decided_by"
        ).prefetch_related("allocations__batch")
        user = self.request.user
        queryset = queryset.filter(issue__material__in=visible_materials(user))
        if is_shop_worker(user):
            queryset = queryset.filter(created_by=user)
        if issue := int_query_param(self.request, "issue"):
            queryset = queryset.filter(issue_id=issue)
        if material := int_query_param(self.request, "material"):
            queryset = queryset.filter(issue__material_id=material)
        return self.filter_common(queryset)

    def request_service(self, **kwargs) -> StockReturn:
        """Qaytarish so'rovini yaratadi."""
        return services.request_return(**kwargs)

    def approve_service(self, pk: int, **kwargs):
        """Qaytarishni tasdiqlaydi."""
        return services.approve_return(return_id=pk, **kwargs)

    def reject_service(self, pk: int, **kwargs):
        """Qaytarishni rad etadi."""
        return services.reject_return(return_id=pk, **kwargs)


class WriteOffViewSet(ApprovalRequestViewSet):
    """Hisobdan chiqarishlar (OQ-007). Filtrlar: ``material``, ``status``, sana."""

    serializer_class = WriteOffSerializer
    create_serializer_class = WriteOffCreateSerializer
    idempotency_endpoint = "write_offs:create"
    action_permissions = {
        "create": "inventory.add_write_off",
        "approve": "inventory.approve_write_off",
        "reject": "inventory.approve_write_off",
    }

    def get_queryset(self) -> QuerySet[WriteOff]:
        """Hisobdan chiqarishlarni partiyalar va foydalanuvchilar bilan qaytaradi."""
        queryset = WriteOff.objects.select_related(
            "material", "created_by", "decided_by"
        ).prefetch_related("allocations__batch")
        queryset = queryset.filter(material__in=visible_materials(self.request.user))
        if is_shop_worker(self.request.user):
            queryset = queryset.filter(created_by=self.request.user)
        if material := int_query_param(self.request, "material"):
            queryset = queryset.filter(material_id=material)
        return self.filter_common(queryset)

    def request_service(self, **kwargs) -> WriteOff:
        """Hisobdan chiqarish so'rovini yaratadi."""
        return services.request_write_off(**kwargs)

    def approve_service(self, pk: int, **kwargs):
        """Hisobdan chiqarishni tasdiqlaydi (admin)."""
        return services.approve_write_off(write_off_id=pk, **kwargs)

    def reject_service(self, pk: int, **kwargs):
        """Hisobdan chiqarishni rad etadi."""
        return services.reject_write_off(write_off_id=pk, **kwargs)
