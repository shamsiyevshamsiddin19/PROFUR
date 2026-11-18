"""Kirim API'si uchun so'rov va javob shakllari (shartnoma, 4-bo'lim)."""

from decimal import Decimal

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.catalog.models import Material

from .models import AMOUNT, QUANTITY, Batch, Currency

PRICE_FIELDS = ("total_amount", "unit_price", "currency")
VIEW_PRICE_CODE = "inventory.view_purchase_price"


def can_view_prices(user) -> bool:
    """OQ-041: narxni faqat ``inventory.view_purchase_price`` ruxsati bilan ko'rish."""
    return bool(user and user.is_authenticated) and user.has_permission_code(
        VIEW_PRICE_CODE
    )


class ActiveMaterialField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        "material_inactive": _("Faol bo'lmagan materialga kirim qilib bo'lmaydi."),
    }

    def to_internal_value(self, data) -> Material:
        material = super().to_internal_value(data)
        if not material.is_active:
            self.fail("material_inactive")
        return material


class ReceiptCreateSerializer(serializers.Serializer):
    """POST /api/v1/receipts/ tanasi."""

    material_id = ActiveMaterialField(queryset=Material.objects.all())
    received_on = serializers.DateField()
    quantity = serializers.DecimalField(**QUANTITY, min_value=Decimal("0.01"))
    total_amount = serializers.DecimalField(**AMOUNT, min_value=Decimal("0.01"))
    currency = serializers.ChoiceField(choices=Currency.choices)
    supplier = serializers.CharField(
        max_length=200, required=False, allow_blank=True, default=""
    )
    document_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )

    def validate_received_on(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                _("Kirim sanasi kelajakda bo'lishi mumkin emas."),
                code="date_in_future",
            )
        return value


class ReceiptSerializer(serializers.ModelSerializer):
    """Kirim (partiya) javobi. Narx maydonlari ruxsatsiz foydalanuvchidan olib tashlanadi."""

    material = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = [
            "id",
            "material",
            "received_on",
            "quantity",
            "quantity_remaining",
            *PRICE_FIELDS,
            "supplier",
            "document_number",
            "note",
            "created_by",
            "created_at",
        ]
        read_only_fields = fields

    def get_material(self, obj: Batch) -> dict:
        material = obj.material
        return {"id": material.pk, "display_name": str(material), "unit": material.unit}

    def get_created_by(self, obj: Batch) -> dict:
        user = obj.created_by
        return {"id": user.pk, "name": user.get_full_name() or user.get_username()}

    def to_representation(self, instance: Batch) -> dict:
        data = super().to_representation(instance)
        request = self.context.get("request")
        if not can_view_prices(getattr(request, "user", None)):
            for field in PRICE_FIELDS:
                data.pop(field, None)
        return data
