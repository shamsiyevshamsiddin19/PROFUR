"""Chiqim API'si (PCRM-44, 1-qism): ``POST/GET /api/v1/issues/``.

Chiqim o'zgartirilmaydi va o'chirilmaydi (TZ 6.8): ``PUT``, ``PATCH`` va
``DELETE`` 405 qaytaradi. ``POST`` uchun ``Idempotency-Key`` majburiy: internet
uzilib brauzer so'rovni qayta yuborsa, ikkinchi chiqim yozilmaydi.
"""

import uuid

from accounts.permissions import HasPermissionCode
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ErrorDetail, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from . import services
from .issue_serializers import IssueCreateSerializer, IssueSerializer
from .models import IdempotencyKey, StockIssue
from .serializers import replay_body_for_user
from .views import (
    IDEMPOTENCY_TTL,
    IdempotencyConflictError,
    idempotency_key,
    query_param_date,
    request_fingerprint,
)

ISSUES_ENDPOINT = "issues:create"


class StockConflictError(APIException):
    """409 javobi: qoldiq yoki partiya yetmaydi (OQ-006). Hech narsa saqlanmagan."""

    status_code = status.HTTP_409_CONFLICT

    def __init__(self, code: str, message, **extra: str):
        """Xato kodi, tarjima qilingan matn va qo'shimcha raqamlar bilan javob tuzadi."""
        super().__init__(
            {"detail": ErrorDetail(str(message), code), "code": code, **extra}
        )


CONFLICT_ERRORS = (
    services.InsufficientStockError,
    services.BatchUnavailableError,
    services.ReturnLimitError,
    services.AlreadyDecidedError,
)


def conflict_from(error: Exception) -> StockConflictError:
    """Servis xatosini frontend tushunadigan 409 javobiga aylantiradi."""
    if isinstance(error, services.AlreadyDecidedError):
        return StockConflictError(
            "already_decided",
            _("So'rov bo'yicha boshqa qaror qabul qilingan."),
            status=error.status,
        )
    if isinstance(error, services.ReturnLimitError):
        return StockConflictError(
            "return_exceeds_issue",
            _("Qaytarish asl chiqimning qaytarilmagan qismidan oshadi."),
            batch_id=str(error.batch_id),
            available=str(error.available),
            requested=str(error.requested),
        )
    if isinstance(error, services.BatchUnavailableError):
        return StockConflictError(
            "batch_insufficient",
            _("Partiyada yetarli miqdor qolmagan."),
            batch_id=str(error.batch_id),
            available=str(error.available),
            requested=str(error.requested),
        )
    return StockConflictError(
        "insufficient_stock",
        _("Omborda yetarli material yo'q."),
        available=str(error.available),
        requested=str(error.requested),
    )


def int_query_param(request: Request, name: str) -> int | None:
    """So'rovdagi butun son filtrini o'qiydi; noto'g'ri bo'lsa 400 beradi."""
    value = request.query_params.get(name)
    if not value:
        return None
    if not value.isdigit():
        raise ValidationError(
            {name: [ErrorDetail(str(_("Butun son bo'lishi kerak.")), code="invalid")]}
        )
    return int(value)


class IdempotentCreateMixin:
    """``POST`` so'rovini ``Idempotency-Key`` bo'yicha bir marta bajaradi.

    Kirim API'sidagi qoida bilan bir xil (shartnoma, 4.1): bir xil kalit va
    tana — birinchi javob 200 bilan qaytadi; bir xil kalit, boshqa tana — 409;
    kalit 24 soat saqlanadi. View ``idempotency_endpoint`` ni belgilaydi.
    """

    idempotency_endpoint = ""

    def idempotent_create(self, request: Request, perform) -> Response:
        """``perform()`` ni bir marta bajaradi va javobni kalit bilan saqlaydi.

        ``perform`` tranzaksiya ichida chaqiriladi va javob tanasini qaytaradi.
        Kalitni saqlash ham shu tranzaksiyada, shuning uchun amal va kalit
        birga saqlanadi yoki birga bekor bo'ladi.
        """
        key = idempotency_key(request)
        fingerprint = request_fingerprint(request)
        replay = self._replay(request, key, fingerprint)
        if replay is not None:
            return replay
        try:
            with transaction.atomic():
                body = perform()
                IdempotencyKey.objects.create(
                    key=key,
                    user=request.user,
                    endpoint=self.idempotency_endpoint,
                    request_hash=fingerprint,
                    response_status=status.HTTP_201_CREATED,
                    response_body=body,
                )
        except IntegrityError:
            # Shu kalit bilan parallel so'rov birinchi yozildi: bizning amal
            # to'liq bekor bo'ldi, birinchisining javobi qaytariladi.
            replay = self._replay(request, key, fingerprint)
            if replay is None:
                raise
            return replay
        return Response(body, status=status.HTTP_201_CREATED)

    def _replay(
        self, request: Request, key: uuid.UUID, fingerprint: str
    ) -> Response | None:
        """Shu kalit bilan saqlangan javobni qaytaradi; yo'q yoki eskirgan bo'lsa ``None``."""
        record = IdempotencyKey.objects.filter(
            user=request.user, endpoint=self.idempotency_endpoint, key=key
        ).first()
        if record is None:
            return None
        if timezone.now() - record.created_at > IDEMPOTENCY_TTL:
            record.delete()
            return None
        if record.request_hash != fingerprint:
            raise IdempotencyConflictError()
        return Response(
            self.replay_body(record.response_body, request.user),
            status=status.HTTP_200_OK,
        )

    def replay_body(self, body: dict, user) -> dict:
        """Saqlangan javobni joriy foydalanuvchiga moslaydi (ombor: narxni yashirish).

        Narx maydonlari bo'lmagan view (masalan, xarajatlar) buni o'zgartiradi.
        """
        return replay_body_for_user(body, user)


class StockIssueViewSet(
    IdempotentCreateMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Chiqimlar: ro'yxat (filtr bilan), bitta chiqim va yangi chiqim.

    Ruxsatlar: ``POST`` — ``inventory.add_issue``, ko'rish —
    ``inventory.view_stock`` (kirim va qoldiq bilan bir xil).
    """

    serializer_class = IssueSerializer
    permission_classes = [HasPermissionCode]
    http_method_names = ["get", "post", "head", "options"]
    idempotency_endpoint = ISSUES_ENDPOINT
    permission_codes = {"POST": "inventory.add_issue"}

    @property
    def required_permission(self) -> str:
        """So'rov metodiga mos ruxsat kodini qaytaradi."""
        return self.permission_codes.get(self.request.method, "inventory.view_stock")

    def get_queryset(self) -> QuerySet[StockIssue]:
        """Chiqimlarni qaytaradi; ``material``, ``project_id`` va sana filtrlari bilan."""
        queryset = StockIssue.objects.select_related(
            "material", "created_by"
        ).prefetch_related("allocations__batch")
        if material := int_query_param(self.request, "material"):
            queryset = queryset.filter(material_id=material)
        if project := int_query_param(self.request, "project_id"):
            queryset = queryset.filter(project_id=project)
        if date_from := query_param_date(self.request, "date_from"):
            queryset = queryset.filter(issued_on__gte=date_from)
        if date_to := query_param_date(self.request, "date_to"):
            queryset = queryset.filter(issued_on__lte=date_to)
        return queryset

    @action(detail=True, methods=["get"])
    def returnable(self, request: Request, *args, **kwargs) -> Response:
        """Asl chiqimdan tasdiqlangan va kutilayotgan qaytarishlarni ayiradi."""
        issue = self.get_object()
        available = services.returnable_by_batch(issue, include_pending=True)
        data = self.get_serializer(issue).data
        for part in data["allocations"]:
            part["returnable_quantity"] = str(available[part["batch_id"]])
        return Response({"allocations": data["allocations"]})

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Chiqim yozadi. Qoldiq yoki partiya yetmasa 409, hech narsa saqlanmaydi."""
        serializer = IssueCreateSerializer(data=request.data)

        def perform() -> dict:
            """Ma'lumotni tekshiradi, chiqimni saqlaydi va javob tanasini qaytaradi."""
            serializer.is_valid(raise_exception=True)
            try:
                issue, on_hand = services.issue_stock(
                    user=request.user, **serializer.service_kwargs()
                )
            except CONFLICT_ERRORS as error:
                raise conflict_from(error) from error
            return {
                **IssueSerializer(issue, context={"request": request}).data,
                "quantity_on_hand_after": str(on_hand),
            }

        return self.idempotent_create(request, perform)
