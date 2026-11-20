"""Qoldiq, partiyalar va harakatlar tarixi API'si (PCRM-42).

Shartnoma: docs/06-api-contract/warehouse-api-v1.md, 5-bo'lim.

- ``GET /api/v1/stock/`` va ``GET /api/v1/stock/{material_id}/`` — qoldiq.
- ``PATCH /api/v1/stock/{material_id}/`` — minimal chegara (OQ-014).
- ``GET /api/v1/stock/{material_id}/batches/`` — qoldig'i bor partiyalar.
- ``GET /api/v1/movements/`` — harakatlar tarixi.

Bu yerda qoldiq faqat o'qiladi; o'zgartirish ``services`` orqali.
"""

from accounts.permissions import HasPermissionCode
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, QuerySet, Sum
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.catalog.access import is_shop_worker, visible_materials
from apps.catalog.models import Material

from . import services
from .models import Batch, MovementType, StockMovement
from .serializers import (
    MinQuantitySerializer,
    MovementSerializer,
    OpenBatchSerializer,
    StockRowSerializer,
)
from .views import query_param_date

VIEW_STOCK = "inventory.view_stock"
OPEN_BATCH = Q(batches__quantity_remaining__gt=0)


def int_param(request: Request, name: str) -> int | None:
    value = request.query_params.get(name)
    if not value:
        return None
    if not value.isdigit():
        raise ValidationError(
            {name: [ErrorDetail(str(_("Butun son.")), code="invalid")]}
        )
    return int(value)


class StockPermissionMixin:
    permission_classes = [HasPermissionCode]
    permission_codes: dict[str, str] = {}

    @property
    def required_permission(self) -> str:
        return self.permission_codes.get(self.request.method, VIEW_STOCK)


class StockViewSet(
    StockPermissionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Material bo'yicha qoldiq. ``{pk}`` — material identifikatori."""

    serializer_class = StockRowSerializer
    http_method_names = ["get", "patch", "head", "options"]
    permission_codes = {"PATCH": "inventory.change_min_quantity"}

    def get_queryset(self) -> QuerySet[Material]:
        params = self.request.query_params
        stock_value = ExpressionWrapper(
            F("batches__quantity_remaining") * F("batches__unit_price"),
            output_field=DecimalField(max_digits=32, decimal_places=8),
        )
        queryset = (
            visible_materials(self.request.user)
            .select_related("category", "stock")
            .annotate(
                open_batches=Count("batches", filter=OPEN_BATCH),
                stock_value=Sum(stock_value, filter=OPEN_BATCH),
            )
            .order_by("category__name", "name", "id")
        )
        if search := params.get("search", "").strip():
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(color__icontains=search)
            )
        if (category := int_param(self.request, "category")) is not None:
            queryset = queryset.filter(category_id=category)
        below_min = params.get("below_min", "").lower()
        if below_min in ("true", "1"):
            queryset = queryset.filter(
                stock__min_quantity__isnull=False,
                stock__quantity_on_hand__lt=F("stock__min_quantity"),
            )
        elif below_min not in ("", "false", "0"):
            raise ValidationError(
                {"below_min": [ErrorDetail(str(_("true yoki false.")), code="invalid")]}
            )
        return queryset

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        material = self.get_object()
        serializer = MinQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.set_min_quantity(material, serializer.validated_data["min_quantity"])
        return Response(
            self.get_serializer(self.get_queryset().get(pk=material.pk)).data
        )

    @action(detail=True, methods=["get"])
    def batches(self, request: Request, pk=None) -> Response:
        material = self.get_object()
        open_batches = Batch.objects.filter(
            material=material, quantity_remaining__gt=0
        ).order_by("received_on", "id")
        page = self.paginate_queryset(open_batches)
        serializer = OpenBatchSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)


class MovementViewSet(
    StockPermissionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MovementSerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self) -> QuerySet[StockMovement]:
        params = self.request.query_params
        user = self.request.user
        queryset = StockMovement.objects.select_related(
            "material", "created_by"
        ).filter(material__in=visible_materials(user))
        if is_shop_worker(user):
            queryset = queryset.filter(created_by=user)
        if (material := int_param(self.request, "material")) is not None:
            queryset = queryset.filter(material_id=material)
        if movement_type := params.get("type"):
            if movement_type not in MovementType.values:
                raise ValidationError(
                    {
                        "type": [
                            ErrorDetail(
                                str(_("Noma'lum harakat turi.")), code="invalid_choice"
                            )
                        ]
                    }
                )
            queryset = queryset.filter(type=movement_type)
        if date_from := query_param_date(self.request, "date_from"):
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to := query_param_date(self.request, "date_to"):
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset
