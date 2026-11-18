"""Kirim API'si (PCRM-40): POST/GET /api/v1/receipts/.

Shartnoma: docs/06-api-contract/warehouse-api-v1.md, 4-bo'lim.
Kirim o'zgartirilmaydi va o'chirilmaydi (PUT/PATCH/DELETE yo'q): xato kirim
keyinchalik tuzatish harakati bilan to'g'rilanadi (PM savoli P5).
"""

import hashlib
import json
import uuid
from datetime import date, timedelta

from accounts.permissions import HasPermissionCode
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import APIException, ErrorDetail, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from . import services
from .models import Batch, IdempotencyKey
from .serializers import (
    ReceiptCreateSerializer,
    ReceiptSerializer,
    replay_body_for_user,
)

RECEIPTS_ENDPOINT = "receipts:create"
IDEMPOTENCY_TTL = timedelta(hours=24)


class IdempotencyConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Bu kalit boshqa so'rov uchun ishlatilgan.")
    default_code = "idempotency_conflict"


def idempotency_key(request: Request) -> uuid.UUID:
    raw = request.headers.get("Idempotency-Key", "")
    try:
        return uuid.UUID(raw)
    except ValueError:
        raise ValidationError(
            {
                "idempotency_key": [
                    ErrorDetail(
                        str(_("Idempotency-Key sarlavhasi UUID bo'lishi kerak.")),
                        code="idempotency_key_required",
                    )
                ]
            }
        ) from None


def request_fingerprint(request: Request) -> str:
    body = json.dumps(request.data, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(body.encode()).hexdigest()


def query_param_date(request: Request, name: str):
    value = request.query_params.get(name)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationError(
            {name: [ErrorDetail(str(_("Sana YYYY-MM-DD.")), code="invalid")]}
        ) from None


class ReceiptViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = ReceiptSerializer
    permission_classes = [HasPermissionCode]
    http_method_names = ["get", "post", "head", "options"]
    permission_codes = {"POST": "inventory.add_receipt"}

    @property
    def required_permission(self) -> str:
        return self.permission_codes.get(self.request.method, "inventory.view_stock")

    def get_queryset(self) -> QuerySet[Batch]:
        params = self.request.query_params
        queryset = Batch.objects.select_related("material", "created_by")
        if material := params.get("material"):
            if not material.isdigit():
                raise ValidationError(
                    {"material": [ErrorDetail(str(_("Butun son.")), code="invalid")]}
                )
            queryset = queryset.filter(material_id=int(material))
        if date_from := query_param_date(self.request, "date_from"):
            queryset = queryset.filter(received_on__gte=date_from)
        if date_to := query_param_date(self.request, "date_to"):
            queryset = queryset.filter(received_on__lte=date_to)
        if currency := params.get("currency"):
            queryset = queryset.filter(currency=currency)
        return queryset

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Kirim yozadi. Bir xil kalit va tana bilan takror so'rov birinchi javobni qaytaradi."""
        key = idempotency_key(request)
        fingerprint = request_fingerprint(request)
        replay = self._replay(request, key, fingerprint)
        if replay is not None:
            return replay

        serializer = ReceiptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        data["material"] = data.pop("material_id")
        try:
            with transaction.atomic():
                batch, balance = services.receive(user=request.user, **data)
                body = {
                    **ReceiptSerializer(batch, context={"request": request}).data,
                    "quantity_on_hand_after": str(balance.quantity_on_hand),
                }
                IdempotencyKey.objects.create(
                    key=key,
                    user=request.user,
                    endpoint=RECEIPTS_ENDPOINT,
                    request_hash=fingerprint,
                    response_status=status.HTTP_201_CREATED,
                    response_body=body,
                )
        except IntegrityError:
            # Xuddi shu kalit bilan parallel so'rov birinchi bo'lib yozildi:
            # bizning kirim to'liq bekor qilindi, uning javobi qaytariladi.
            replay = self._replay(request, key, fingerprint)
            if replay is None:
                raise
            return replay
        return Response(body, status=status.HTTP_201_CREATED)

    @staticmethod
    def _replay(request: Request, key: uuid.UUID, fingerprint: str) -> Response | None:
        record = IdempotencyKey.objects.filter(
            user=request.user, endpoint=RECEIPTS_ENDPOINT, key=key
        ).first()
        if record is None:
            return None
        if timezone.now() - record.created_at > IDEMPOTENCY_TTL:
            record.delete()
            return None
        if record.request_hash != fingerprint:
            raise IdempotencyConflictError()
        return Response(
            replay_body_for_user(record.response_body, request.user),
            status=status.HTTP_200_OK,
        )
