"""Katalog API'si uchun so'rov va javob shakllari (PCRM-39)."""

from decimal import Decimal

from accounts.models import Role
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Category, Material

DIMENSION_FIELDS = ("length_cm", "width_cm", "thickness_cm")

# Bir kategoriyada takrorlanmasligi kerak bo'lgan maydonlar (PR #11 dagi
# catalog_material_unique_nomenclature cheklovi bilan bir xil).
NOMENCLATURE_FIELDS = (
    "category",
    "name",
    "color",
    *DIMENSION_FIELDS,
    "unit",
    "container_size",
)


class CategorySerializer(serializers.ModelSerializer):
    material_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "is_active", "material_count"]

    def get_material_count(self, obj: Category) -> int:
        count = getattr(obj, "material_count", None)
        return obj.materials.count() if count is None else count


class CategoryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class MaterialSerializer(serializers.ModelSerializer):
    category = CategoryBriefSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )
    display_name = serializers.SerializerMethodField()
    quantity_on_hand = serializers.SerializerMethodField()
    allowed_roles = serializers.ListField(
        child=serializers.CharField(max_length=50), max_length=100, required=False
    )

    def validate_allowed_roles(self, values):
        request = self.context.get("request")
        if not request or not request.user.is_admin_role:
            raise serializers.ValidationError(
                _("Material vakolatlarini administrator belgilaydi.")
            )
        known = set(Role.objects.filter(code__in=values).values_list("code", flat=True))
        if set(values) != known:
            raise serializers.ValidationError(_("Tanlangan rol mavjud emas."))
        return list(dict.fromkeys(values))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if not request or not request.user.is_admin_role:
            data.pop("allowed_roles", None)
        return data

    class Meta:
        model = Material
        fields = [
            "id",
            "category",
            "category_id",
            "name",
            "color",
            *DIMENSION_FIELDS,
            "unit",
            "container_size",
            "allowed_roles",
            "display_name",
            "is_active",
            "quantity_on_hand",
        ]
        extra_kwargs = {
            field: {"min_value": Decimal("0.01")}
            for field in (*DIMENSION_FIELDS, "container_size")
        }
        # Noyoblik view'da tekshiriladi: javobda mavjud material identifikatori
        # qaytishi kerak, DRF'ning avtomatik validatori esa bo'sh o'lchamlarni
        # solishtirmaydi.
        validators: list = []

    def get_display_name(self, obj: Material) -> str:
        return str(obj)

    def get_quantity_on_hand(self, obj: Material) -> str:
        """``inventory.StockBalance`` dagi qoldiq; hali kirim bo'lmasa ``"0.00"``."""
        try:
            return str(obj.stock.quantity_on_hand)
        except ObjectDoesNotExist:
            return "0.00"

    def validate_category_id(self, category: Category) -> Category:
        changed = self.instance is None or self.instance.category_id != category.pk
        if changed and not category.is_active:
            raise serializers.ValidationError(
                _("Faol bo'lmagan kategoriyaga material qo'shib bo'lmaydi."),
                code="category_inactive",
            )
        return category

    def nomenclature(self) -> dict:
        """Saqlanadigan yozuvning noyoblik maydonlari (PATCH'da eski qiymatlar bilan)."""
        data = self.validated_data
        result = {}
        for field in NOMENCLATURE_FIELDS:
            if field in data:
                result[field] = data[field]
            elif self.instance is not None:
                result[field] = getattr(self.instance, field)
            elif field == "color":
                result[field] = ""
            else:
                result[field] = None
        return result
