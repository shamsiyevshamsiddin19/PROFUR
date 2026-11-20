"""Qaytarish (OQ-003) va hisobdan chiqarish (OQ-007) so'rovlari shakllari.

Ikkala so'rov ham partiya qismlari bilan keladi va qaror (tasdiq yoki rad)
kutadi. Narx maydonlari OQ-041 bo'yicha ruxsatsiz foydalanuvchidan yashiriladi.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.catalog.access import is_shop_worker, visible_materials
from apps.catalog.models import Material

from .issue_serializers import (
    CostedAllocationsMixin,
    allocations_field,
    ensure_batches_of_material,
    not_in_future,
    reject_duplicate_batches,
    to_allocations,
)
from .models import StockIssue, StockReturn, WriteOff
from .serializers import user_brief

DECISION_FIELDS = ["status", "decided_by", "decided_at", "decision_note"]


class DecisionSerializer(serializers.Serializer):
    """``approve``/``reject`` tanasi: ixtiyoriy izoh."""

    note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )


class ReturnCreateSerializer(serializers.Serializer):
    """``POST /api/v1/returns/`` tanasi.

    Qism faqat asl chiqim olingan partiyaga qaytadi. Asl chiqimdan ortiq
    qaytarish limitini servis qulf ostida tekshiradi (409).
    """

    issue_id = serializers.PrimaryKeyRelatedField(
        queryset=StockIssue.objects.prefetch_related("allocations")
    )
    returned_on = serializers.DateField(required=False)
    reason = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    allocations = allocations_field()

    def validate_returned_on(self, value):
        """Qaytarish sanasi kelajakda bo'lmasligini tekshiradi."""
        return not_in_future(
            value, _("Qaytarish sanasi kelajakda bo'lishi mumkin emas.")
        )

    def validate(self, attrs: dict) -> dict:
        """Partiyalar asl chiqimda borligini va sana chiqimdan oldin emasligini tekshiradi."""
        issue = attrs["issue_id"]
        if request := self.context.get("request"):
            user = request.user
            if not visible_materials(user).filter(pk=issue.material_id).exists() or (
                is_shop_worker(user) and issue.created_by_id != user.pk
            ):
                raise serializers.ValidationError(
                    {"issue_id": _("Chiqim mavjud emas.")}
                )
        batch_ids = reject_duplicate_batches(attrs["allocations"])
        issued = {part.batch_id for part in issue.allocations.all()}
        if foreign := sorted(set(batch_ids) - issued):
            raise serializers.ValidationError(
                {
                    "allocations": _("Partiya asl chiqimda yo'q: {ids}.").format(
                        ids=", ".join(map(str, foreign))
                    )
                },
                code="batch_not_in_issue",
            )
        returned_on = attrs.setdefault("returned_on", timezone.localdate())
        if returned_on < issue.issued_on:
            raise serializers.ValidationError(
                {
                    "returned_on": _(
                        "Qaytarish sanasi chiqim sanasidan oldin bo'lmasin."
                    )
                },
                code="before_issue",
            )
        attrs["reason"] = attrs["reason"].strip()
        return attrs

    def service_kwargs(self) -> dict:
        """Tekshirilgan ma'lumotni ``services.request_return()`` argumentlariga aylantiradi."""
        data = self.validated_data
        return {
            "issue": data["issue_id"],
            "allocations": to_allocations(data["allocations"]),
            "returned_on": data["returned_on"],
            "reason": data["reason"],
        }


class WriteOffCreateSerializer(serializers.Serializer):
    """``POST /api/v1/write-offs/`` tanasi. Sabab majburiy (OQ-007)."""

    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    reason = serializers.CharField(max_length=500)
    allocations = allocations_field()

    def validate(self, attrs: dict) -> dict:
        """Partiyalar shu materialniki ekanini tekshiradi va sababni tozalaydi."""
        if request := self.context.get("request"):
            if (
                not visible_materials(request.user)
                .filter(pk=attrs["material_id"].pk)
                .exists()
            ):
                raise serializers.ValidationError(
                    {"material_id": _("Material mavjud emas.")}
                )
        ensure_batches_of_material(attrs["material_id"], attrs["allocations"])
        attrs["reason"] = attrs["reason"].strip()
        return attrs

    def service_kwargs(self) -> dict:
        """Tekshirilgan ma'lumotni ``services.request_write_off()`` argumentlariga aylantiradi."""
        data = self.validated_data
        return {
            "material": data["material_id"],
            "allocations": to_allocations(data["allocations"]),
            "reason": data["reason"],
        }


class DecisionFieldsMixin(serializers.Serializer):
    """Qaror maydonlari: kim qaror qilgani (bo'lmasa ``null``)."""

    decided_by = serializers.SerializerMethodField()

    def get_decided_by(self, obj) -> dict | None:
        """Qaror qilgan foydalanuvchi yoki kutilayotgan so'rovda ``None``."""
        return user_brief(obj.decided_by) if obj.decided_by_id else None


class ReturnSerializer(
    DecisionFieldsMixin, CostedAllocationsMixin, serializers.ModelSerializer
):
    """Qaytarish javobi: asl chiqim, partiyalar, holat va qaror."""

    issue = serializers.SerializerMethodField()

    class Meta:
        model = StockReturn
        fields = [
            "id",
            "issue",
            "material",
            "quantity",
            "returned_on",
            "reason",
            "allocations",
            "total_cost",
            "currency",
            *DECISION_FIELDS,
            "created_by",
            "created_at",
        ]
        read_only_fields = fields

    def get_issue(self, stock_return: StockReturn) -> dict:
        """Asl chiqim haqida qisqa ma'lumot."""
        issue = stock_return.issue
        return {
            "id": issue.pk,
            "issued_on": issue.issued_on.isoformat(),
            "recipient_name": issue.recipient_name,
            "project_id": issue.project_id,
            "quantity": str(issue.quantity),
        }

    def get_material(self, stock_return: StockReturn) -> dict:
        """Material asl chiqimdan olinadi."""
        return super().get_material(stock_return.issue)


class WriteOffSerializer(
    DecisionFieldsMixin, CostedAllocationsMixin, serializers.ModelSerializer
):
    """Hisobdan chiqarish javobi: material, partiyalar, sabab, holat va qaror."""

    class Meta:
        model = WriteOff
        fields = [
            "id",
            "material",
            "quantity",
            "reason",
            "allocations",
            "total_cost",
            "currency",
            *DECISION_FIELDS,
            "created_by",
            "created_at",
        ]
        read_only_fields = fields
