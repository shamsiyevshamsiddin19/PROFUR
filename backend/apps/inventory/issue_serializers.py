"""Chiqim API'si uchun so'rov va javob shakllari (PCRM-44, 1-qism).

Miqdor va pul satr ko'rinishida keladi va ketadi (``"4.00"``). Pul faqat USD.
Narx maydonlari ``inventory.view_purchase_price`` ruxsati bo'lmasa javobdan
olib tashlanadi (OQ-041), xuddi kirim API'sidagidek.
"""

from decimal import Decimal

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.catalog.models import Material

from .models import QUANTITY, Batch, Currency, StockIssue
from .serializers import can_view_prices
from .services import Allocation

MAX_ALLOCATIONS = 50


class AllocationInputSerializer(serializers.Serializer):
    """Bitta partiyadan olinadigan qism: ``{"batch_id": 12, "quantity": "4.00"}``."""

    batch_id = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(**QUANTITY, min_value=Decimal("0.01"))


class IssueCreateSerializer(serializers.Serializer):
    """``POST /api/v1/issues/`` tanasi.

    Partiya tanlash qoidasi PM qaroriga bog'liq (OQ-001), shuning uchun mijoz
    qaysi partiyadan qancha olinishini o'zi yuboradi. Chiqim miqdori —
    qismlar yig'indisi. Qoldiq yetishi serverda, qulf ostida tekshiriladi.
    """

    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    issued_on = serializers.DateField(required=False)
    recipient_name = serializers.CharField(max_length=200)
    project_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    allocations = serializers.ListField(
        child=AllocationInputSerializer(),
        min_length=1,
        max_length=MAX_ALLOCATIONS,
    )

    def validate_issued_on(self, value):
        """Chiqim sanasi kelajakda bo'lmasligini tekshiradi."""
        if value > timezone.localdate():
            raise serializers.ValidationError(
                _("Chiqim sanasi kelajakda bo'lishi mumkin emas."),
                code="date_in_future",
            )
        return value

    def validate(self, attrs: dict) -> dict:
        """Partiyalar takrorlanmasligi va shu materialga tegishli ekanini tekshiradi.

        Bu yerda qoldiq miqdori tekshirilmaydi: u boshqa so'rov bilan bir vaqtda
        o'zgarishi mumkin, shuning uchun servis uni qulf ostida tekshiradi.
        """
        material = attrs["material_id"]
        batch_ids = [part["batch_id"] for part in attrs["allocations"]]
        if len(set(batch_ids)) != len(batch_ids):
            raise serializers.ValidationError(
                {"allocations": _("Bitta partiya ikki marta ko'rsatilgan.")},
                code="duplicate_batch",
            )
        own_batches = set(
            Batch.objects.filter(material=material, pk__in=batch_ids).values_list(
                "pk", flat=True
            )
        )
        if foreign := sorted(set(batch_ids) - own_batches):
            raise serializers.ValidationError(
                {
                    "allocations": _(
                        "Partiya bu materialga tegishli emas: {ids}."
                    ).format(ids=", ".join(map(str, foreign)))
                },
                code="batch_not_of_material",
            )
        attrs.setdefault("issued_on", timezone.localdate())
        attrs["recipient_name"] = attrs["recipient_name"].strip()
        return attrs

    def service_kwargs(self) -> dict:
        """Tekshirilgan ma'lumotni ``services.issue_stock()`` argumentlariga aylantiradi."""
        data = self.validated_data
        return {
            "material": data["material_id"],
            "allocations": [
                Allocation(part["batch_id"], part["quantity"])
                for part in data["allocations"]
            ],
            "issued_on": data["issued_on"],
            "recipient_name": data["recipient_name"],
            "project_id": data.get("project_id"),
            "note": data["note"],
        }


class IssueSerializer(serializers.ModelSerializer):
    """Chiqim javobi. Narx maydonlari ruxsatsiz foydalanuvchidan olib tashlanadi."""

    material = serializers.SerializerMethodField()
    allocations = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = StockIssue
        fields = [
            "id",
            "material",
            "quantity",
            "issued_on",
            "recipient_name",
            "project_id",
            "note",
            "allocations",
            "total_cost",
            "currency",
            "created_by",
            "created_at",
        ]
        read_only_fields = fields

    def get_material(self, issue: StockIssue) -> dict:
        """Material haqida qisqa ma'lumot: raqami, nomi va o'lchov birligi."""
        material = issue.material
        return {"id": material.pk, "display_name": str(material), "unit": material.unit}

    def get_allocations(self, issue: StockIssue) -> list[dict]:
        """Qaysi partiyadan qancha olinganini qaytaradi (narx — ruxsat bo'lsa)."""
        show_prices = self._show_prices()
        parts = []
        for part in issue.allocations.all():
            row = {
                "batch_id": part.batch_id,
                "received_on": part.batch.received_on.isoformat(),
                "quantity": str(part.quantity),
            }
            if show_prices:
                row["unit_price"] = str(part.batch.unit_price)
            parts.append(row)
        return parts

    def get_total_cost(self, issue: StockIssue) -> str:
        """Chiqim tannarxi USD'da, satr ko'rinishida (``"412.50"``)."""
        return str(issue.total_cost())

    def get_currency(self, issue: StockIssue) -> str:
        """Yagona valyuta — USD (qarorlar jurnali, 2026-11-18)."""
        return Currency.USD

    def get_created_by(self, issue: StockIssue) -> dict:
        """Chiqimni kiritgan foydalanuvchining raqami va ismi."""
        user = issue.created_by
        return {"id": user.pk, "name": user.get_full_name() or user.get_username()}

    def to_representation(self, instance: StockIssue) -> dict:
        """Javobni tuzadi va narx ruxsati bo'lmasa pul maydonlarini olib tashlaydi."""
        data = super().to_representation(instance)
        if not self._show_prices():
            data.pop("total_cost", None)
            data.pop("currency", None)
        return data

    def _show_prices(self) -> bool:
        """So'rov egasi narxlarni ko'ra oladimi (``inventory.view_purchase_price``)."""
        request = self.context.get("request")
        return can_view_prices(getattr(request, "user", None))
