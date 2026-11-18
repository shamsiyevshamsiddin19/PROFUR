"""Katalog API'si: kategoriyalar va materiallar (PCRM-39).

Shartnoma: docs/06-api-contract/warehouse-api-v1.md, 3-bo'lim.
Yozuvlar o'chirilmaydi, ``is_active=false`` bilan faolsizlantiriladi,
shuning uchun ``DELETE`` va ``PUT`` metodlari yo'q (405).
"""

from accounts.permissions import HasPermissionCode
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ErrorDetail, ValidationError

from .models import Category, Material, Unit
from .serializers import CategorySerializer, MaterialSerializer

READ_METHODS = ("GET", "HEAD", "OPTIONS")
VIEW_CATALOG = "catalog.view_material"


class MaterialDuplicateError(ValidationError):
    """Bir xil material allaqachon bor: 400 va mavjud yozuv identifikatori."""

    def __init__(self, existing_id: int):
        super().__init__(
            {
                "non_field_errors": [
                    ErrorDetail(
                        str(_("Bunday material allaqachon mavjud.")),
                        code="material_duplicate",
                    )
                ]
            }
        )
        self.detail["existing_id"] = existing_id


def bool_param(value: str | None, name: str) -> bool | None:
    if value is None or value == "":
        return None
    lowered = value.lower()
    if lowered in ("true", "1"):
        return True
    if lowered in ("false", "0"):
        return False
    raise ValidationError({name: [ErrorDetail(_("true yoki false."), code="invalid")]})


def int_param(value: str | None, name: str) -> int | None:
    if value is None or value == "":
        return None
    if not value.isdigit():
        raise ValidationError({name: [ErrorDetail(_("Butun son."), code="invalid")]})
    return int(value)


class CreatePatchViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Ro'yxat, bitta yozuv, yaratish va qisman o'zgartirish (PATCH).

    Ruxsat ``HasPermissionCode`` orqali rol ruxsatlaridan tekshiriladi (OQ-037).
    Har bir metodga kerakli kod ``permission_codes`` lug'atida beriladi
    (shartnoma, 2-bo'lim).
    """

    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [HasPermissionCode]
    permission_codes: dict[str, str] = {}

    @property
    def required_permission(self) -> str:
        # Ruxsat metod tekshiruvidan oldin ishlaydi. Ro'yxatda yo'q metod
        # (DELETE, PUT) ko'rish ruxsati bilan o'tib, keyin 405 oladi.
        return self.permission_codes.get(self.request.method, VIEW_CATALOG)


class CategoryViewSet(CreatePatchViewSet):
    serializer_class = CategorySerializer
    permission_codes = {
        **dict.fromkeys(READ_METHODS, VIEW_CATALOG),
        "POST": "catalog.add_category",
        "PATCH": "catalog.change_category",
    }

    def get_queryset(self) -> QuerySet[Category]:
        params = self.request.query_params
        # Count bilan Django Meta.ordering'ni tushirib qoldiradi, tartib aniq beriladi.
        queryset = Category.objects.annotate(
            material_count=Count("materials")
        ).order_by("name")
        if search := params.get("search", "").strip():
            queryset = queryset.filter(name__icontains=search)
        is_active = bool_param(params.get("is_active"), "is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset


class MaterialViewSet(CreatePatchViewSet):
    serializer_class = MaterialSerializer
    permission_codes = {
        **dict.fromkeys(READ_METHODS, VIEW_CATALOG),
        "POST": "catalog.add_material",
        "PATCH": "catalog.change_material",
    }

    def get_queryset(self) -> QuerySet[Material]:
        params = self.request.query_params
        queryset = Material.objects.select_related("category")
        if search := params.get("search", "").strip():
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(color__icontains=search)
            )
        category = int_param(params.get("category"), "category")
        if category is not None:
            queryset = queryset.filter(category_id=category)
        if unit := params.get("unit"):
            if unit not in Unit.values:
                raise ValidationError(
                    {
                        "unit": [
                            ErrorDetail(_("Noma'lum birlik."), code="invalid_choice")
                        ]
                    }
                )
            queryset = queryset.filter(unit=unit)
        is_active = bool_param(params.get("is_active"), "is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

    def perform_create(self, serializer: MaterialSerializer) -> None:
        self._save_unique(serializer)

    def perform_update(self, serializer: MaterialSerializer) -> None:
        self._save_unique(serializer)

    def _save_unique(self, serializer: MaterialSerializer) -> None:
        """Takror materialni oldindan tekshirib, keyin saqlaydi.

        Ikki so'rov bir vaqtda kelsa, bazadagi noyoblik cheklovi ikkinchisini
        to'xtatadi va u ham xuddi shu 400 javobga aylantiriladi.
        """
        lookup = serializer.nomenclature()
        self._raise_if_duplicate(lookup, serializer.instance)
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            self._raise_if_duplicate(lookup, serializer.instance)
            raise

    @staticmethod
    def _raise_if_duplicate(lookup: dict, instance: Material | None) -> None:
        filters = {}
        for field, value in lookup.items():
            if value is None:
                filters[f"{field}__isnull"] = True  # bo'sh o'lcham ham teng sanaladi
            else:
                filters[field] = value
        duplicates = Material.objects.filter(**filters)
        if instance is not None:
            duplicates = duplicates.exclude(pk=instance.pk)
        existing_id = duplicates.values_list("pk", flat=True).first()
        if existing_id is not None:
            raise MaterialDuplicateError(existing_id)
