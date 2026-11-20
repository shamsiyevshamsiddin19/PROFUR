"""Chiqim API'si uchun so'rov va javob shakllari (PCRM-44).

Miqdor va pul satr ko'rinishida keladi va ketadi (``"4.00"``). Pul faqat USD.
Narx maydonlari ``inventory.view_purchase_price`` ruxsati bo'lmasa javobdan
olib tashlanadi (OQ-041), xuddi kirim API'sidagidek.

Partiya qismlari (``allocations``), tannarx va narxni yashirish qaytarish va
hisobdan chiqarish shakllarida ham shu moduldan olinadi.
"""

from decimal import Decimal

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.catalog.access import visible_materials
from apps.catalog.models import Material

from .models import QUANTITY, Batch, Currency, StockIssue
from .serializers import can_view_prices, material_brief, user_brief
from .services import Allocation

MAX_ALLOCATIONS = 50
COST_FIELDS = ("total_cost", "currency")


class AllocationInputSerializer(serializers.Serializer):
    """Bitta partiyadan olinadigan qism: ``{"batch_id": 12, "quantity": "4.00"}``."""

    batch_id = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(**QUANTITY, min_value=Decimal("0.01"))


def allocations_field() -> serializers.ListField:
    """Partiya qismlari ro'yxati maydoni: 1 tadan 50 tagacha qism."""
    return serializers.ListField(
        child=AllocationInputSerializer(), min_length=1, max_length=MAX_ALLOCATIONS
    )


def to_allocations(parts: list[dict]) -> list[Allocation]:
    """Tekshirilgan qismlarni servis kutadigan ``Allocation`` larga aylantiradi."""
    return [Allocation(part["batch_id"], part["quantity"]) for part in parts]


def reject_duplicate_batches(parts: list[dict]) -> list[int]:
    """Bir partiya ikki marta ko'rsatilsa 400 beradi; partiya raqamlarini qaytaradi."""
    batch_ids = [part["batch_id"] for part in parts]
    if len(set(batch_ids)) != len(batch_ids):
        raise serializers.ValidationError(
            {"allocations": _("Bitta partiya ikki marta ko'rsatilgan.")},
            code="duplicate_batch",
        )
    return batch_ids


def ensure_batches_of_material(material: Material, parts: list[dict]) -> None:
    """Qismlar takrorlanmasligi va partiyalar shu materialniki ekanini tekshiradi.

    Qoldiq miqdori bu yerda tekshirilmaydi: u boshqa so'rov bilan bir vaqtda
    o'zgarishi mumkin, shuning uchun servis uni qulf ostida tekshiradi.
    """
    batch_ids = reject_duplicate_batches(parts)
    own = set(
        Batch.objects.filter(material=material, pk__in=batch_ids).values_list(
            "pk", flat=True
        )
    )
    if foreign := sorted(set(batch_ids) - own):
        raise serializers.ValidationError(
            {
                "allocations": _("Partiya bu materialga tegishli emas: {ids}.").format(
                    ids=", ".join(map(str, foreign))
                )
            },
            code="batch_not_of_material",
        )


def not_in_future(value, message):
    """Sana kelajakda bo'lsa ``date_in_future`` kodi bilan 400 beradi."""
    if value > timezone.localdate():
        raise serializers.ValidationError(message, code="date_in_future")
    return value


class IssueCreateSerializer(serializers.Serializer):
    """``POST /api/v1/issues/`` tanasi.

    Partiya tanlash qoidasi PM qaroriga bog'liq (OQ-001), shuning uchun mijoz
    qaysi partiyadan qancha olinishini o'zi yuboradi. Chiqim miqdori —
    qismlar yig'indisi. Qoldiq yetishi serverda, qulf ostida tekshiriladi.
    Faol bo'lmagan materialdan ham chiqim mumkin: qoldig'i baribir beriladi.
    """

    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    issued_on = serializers.DateField(required=False)
    recipient_name = serializers.CharField(max_length=200)
    project_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    allocations = allocations_field()

    def validate_issued_on(self, value):
        """Chiqim sanasi kelajakda bo'lmasligini tekshiradi."""
        return not_in_future(value, _("Chiqim sanasi kelajakda bo'lishi mumkin emas."))

    def validate(self, attrs: dict) -> dict:
        """Partiyalarni tekshiradi, sana va oluvchi ismini tartibga keltiradi."""
        request = self.context.get("request")
        if (
            request
            and not visible_materials(request.user)
            .filter(pk=attrs["material_id"].pk)
            .exists()
        ):
            raise serializers.ValidationError(
                {"material_id": _("Material mavjud emas.")}
            )
        ensure_batches_of_material(attrs["material_id"], attrs["allocations"])
        attrs.setdefault("issued_on", timezone.localdate())
        attrs["recipient_name"] = attrs["recipient_name"].strip()
        return attrs

    def service_kwargs(self) -> dict:
        """Tekshirilgan ma'lumotni ``services.issue_stock()`` argumentlariga aylantiradi."""
        data = self.validated_data
        return {
            "material": data["material_id"],
            "allocations": to_allocations(data["allocations"]),
            "issued_on": data["issued_on"],
            "recipient_name": data["recipient_name"],
            "project_id": data.get("project_id"),
            "note": data["note"],
        }


class WorkerIssueSerializer(serializers.Serializer):
    material_id = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
    quantity = serializers.DecimalField(**QUANTITY, min_value=Decimal("0.01"))
    project_id = serializers.IntegerField(min_value=1)
    note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )

    def validate_material_id(self, material):
        if (
            not visible_materials(self.context["request"].user)
            .filter(pk=material.pk)
            .exists()
        ):
            raise serializers.ValidationError(_("Material mavjud emas."))
        return material


class CostedAllocationsMixin(serializers.Serializer):
    """Partiya qismlari, USD tannarx va kiritgan foydalanuvchi maydonlari.

    Narx ruxsati bo'lmasa (OQ-041) ``total_cost``, ``currency`` va har qismdagi
    ``unit_price`` javobdan olib tashlanadi. Model ``allocations`` (``batch``
    bilan) va ``total_cost()`` ga ega bo'lishi kerak.
    """

    material = serializers.SerializerMethodField()
    allocations = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    def get_material(self, obj) -> dict:
        """Material haqida qisqa ma'lumot: raqami, nomi va o'lchov birligi."""
        return material_brief(obj.material)

    def get_allocations(self, obj) -> list[dict]:
        """Qaysi partiyadan qancha (narx — ruxsat bo'lsa)."""
        show_prices = self.show_prices()
        parts = []
        for part in obj.allocations.all():
            row = {
                "batch_id": part.batch_id,
                "received_on": part.batch.received_on.isoformat(),
                "quantity": str(part.quantity),
            }
            if show_prices:
                row["unit_price"] = str(part.batch.unit_price)
            parts.append(row)
        return parts

    def get_total_cost(self, obj) -> str:
        """Tannarx USD'da, satr ko'rinishida (``"412.50"``)."""
        return str(obj.total_cost())

    def get_currency(self, obj) -> str:
        """Yagona valyuta — USD (qarorlar jurnali, 2026-11-18)."""
        return Currency.USD

    def get_created_by(self, obj) -> dict:
        """Yozuvni kiritgan foydalanuvchining raqami va ismi."""
        return user_brief(obj.created_by)

    def to_representation(self, instance) -> dict:
        """Javobni tuzadi va narx ruxsati bo'lmasa pul maydonlarini olib tashlaydi."""
        data = super().to_representation(instance)
        if not self.show_prices():
            for field in COST_FIELDS:
                data.pop(field, None)
        return data

    def show_prices(self) -> bool:
        """So'rov egasi narxlarni ko'ra oladimi (``inventory.view_purchase_price``)."""
        request = self.context.get("request")
        return can_view_prices(getattr(request, "user", None))


class IssueSerializer(CostedAllocationsMixin, serializers.ModelSerializer):
    """Chiqim javobi. Narx maydonlari ruxsatsiz foydalanuvchidan olib tashlanadi."""

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
