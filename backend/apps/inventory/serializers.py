"""Ombor API'si uchun so'rov va javob shakllari (shartnoma, 4- va 5-bo'lim)."""

from copy import deepcopy
from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apps.catalog.access import visible_materials
from apps.catalog.models import Material

from .models import AMOUNT, QUANTITY, Batch, Currency, StockMovement

PRICE_FIELDS = ("total_amount", "unit_price", "currency")
VIEW_PRICE_CODE = "inventory.view_purchase_price"


def can_view_prices(user) -> bool:
    """OQ-041: narxni faqat ``inventory.view_purchase_price`` ruxsati bilan ko'rish."""
    return bool(user and user.is_authenticated) and user.has_permission_code(
        VIEW_PRICE_CODE
    )


def replay_body_for_user(body: dict, user) -> dict:
    """Saqlangan javob nusxasida narxni joriy ruxsat bo'yicha yashiradi.

    Idempotentlikdagi asl javob va biznes amal o'zgarmaydi. Ruxsat qaytarilsa,
    keyingi takrorda dastlab saqlangan narxlar yana ko'rinishi mumkin.
    """
    material_id = (body.get("material") or {}).get("id")
    if (
        material_id is not None
        and not visible_materials(user).filter(pk=material_id).exists()
    ):
        raise NotFound()
    data = deepcopy(body)
    if not can_view_prices(user):
        for field in (*PRICE_FIELDS, "total_cost"):
            data.pop(field, None)
        for allocation in data.get("allocations", []):
            allocation.pop("unit_price", None)
    return data


def material_brief(material: Material) -> dict:
    return {"id": material.pk, "display_name": str(material), "unit": material.unit}


def user_brief(user) -> dict:
    return {"id": user.pk, "name": user.get_full_name() or user.get_username()}


class HidePricesMixin:
    """Narx ko'rish ruxsati bo'lmasa, ``price_fields`` javobdan olib tashlanadi."""

    price_fields: tuple[str, ...] = PRICE_FIELDS

    def to_representation(self, instance) -> dict:
        data = super().to_representation(instance)
        request = self.context.get("request")
        if not can_view_prices(getattr(request, "user", None)):
            for field in self.price_fields:
                data.pop(field, None)
        return data


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
    is_opening = serializers.BooleanField(required=False, default=False)
    quantity = serializers.DecimalField(**QUANTITY, min_value=Decimal("0.01"))
    total_amount = serializers.DecimalField(
        **AMOUNT, min_value=Decimal("0.01"), required=False, allow_null=True
    )
    unit_price = serializers.DecimalField(
        max_digits=18,
        decimal_places=6,
        min_value=Decimal("0.000001"),
        required=False,
        allow_null=True,
    )
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

    def validate(self, data):
        total = data.get("total_amount")
        unit = data.get("unit_price")
        quantity = data.get("quantity")

        if total and unit:
            raise serializers.ValidationError(
                _(
                    "total_amount yoki unit_price dan faqat bittasini kiriting, ikkalasini emas."
                )
            )
        if not total and not unit:
            raise serializers.ValidationError(
                _("total_amount yoki unit_price dan bittasi majburiy.")
            )
        if unit and not total:
            amount = (unit * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            data["total_amount"] = self.fields["total_amount"].run_validation(
                str(amount)
            )
        return data


class ReceiptSerializer(HidePricesMixin, serializers.ModelSerializer):
    """Kirim (partiya) javobi. Narx maydonlari ruxsatsiz foydalanuvchidan olib tashlanadi."""

    material = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = [
            "id",
            "material",
            "received_on",
            "is_opening",
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
        return material_brief(obj.material)

    def get_created_by(self, obj: Batch) -> dict:
        return user_brief(obj.created_by)


class OpenBatchSerializer(HidePricesMixin, serializers.ModelSerializer):
    """GET /api/v1/stock/{material_id}/batches/ — qoldig'i bor partiyalar."""

    price_fields = ("unit_price", "currency")

    class Meta:
        model = Batch
        fields = [
            "id",
            "received_on",
            "quantity",
            "quantity_remaining",
            "unit_price",
            "currency",
        ]
        read_only_fields = fields


class StockRowSerializer(serializers.Serializer):
    """GET /api/v1/stock/ qatori: bitta material va uning qoldig'i.

    ``open_batches`` va ``stock_value`` view'dagi annotatsiyadan keladi.
    Yagona valyuta USD bo'lgani uchun ``value_by_currency`` bitta element.
    """

    def to_representation(self, material: Material) -> dict:
        try:
            balance = material.stock
        except ObjectDoesNotExist:
            balance = None
        quantity = balance.quantity_on_hand if balance else Decimal("0.00")
        min_quantity = balance.min_quantity if balance else None
        value = getattr(material, "stock_value", None)
        data = {
            "material": {
                **material_brief(material),
                "category": {
                    "id": material.category_id,
                    "name": material.category.name,
                },
            },
            "quantity_on_hand": f"{quantity:.2f}",
            "open_batches": getattr(material, "open_batches", 0),
            "min_quantity": None if min_quantity is None else f"{min_quantity:.2f}",
            "is_below_min": bool(balance and balance.is_below_min),
            "value_by_currency": (
                [{"currency": Currency.USD, "amount": f"{value:.2f}"}] if value else []
            ),
        }
        request = self.context.get("request")
        if not can_view_prices(getattr(request, "user", None)):
            data.pop("value_by_currency")
        return data


class MinQuantitySerializer(serializers.Serializer):
    """PATCH /api/v1/stock/{material_id}/ — OQ-014 minimal chegara."""

    min_quantity = serializers.DecimalField(
        **QUANTITY, min_value=Decimal("0"), allow_null=True
    )


class MovementSerializer(serializers.ModelSerializer):
    """GET /api/v1/movements/ — o'zgarmas harakatlar tarixi."""

    material = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "type",
            "material",
            "batch_id",
            "quantity",
            "quantity_on_hand_after",
            "reference",
            "reason",
            "created_by",
            "created_at",
        ]
        read_only_fields = fields

    def get_material(self, obj: StockMovement) -> dict:
        return material_brief(obj.material)

    def get_reference(self, obj: StockMovement) -> dict:
        return {"kind": obj.reference_kind, "id": obj.reference_id}

    def get_created_by(self, obj: StockMovement) -> dict:
        return user_brief(obj.created_by)
