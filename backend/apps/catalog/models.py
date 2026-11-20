"""Material katalogi modellari.

Katalog qanday material borligini saqlaydi. Narx, miqdor va kirim sanasi
bu yerda yozilmaydi: har bir kirim alohida partiya bo'lib, ``Material``ga
havola qiladi (OQ-008). O'lchamlar santimetrda saqlanadi (OQ-005).
"""

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Yaratilgan va oxirgi o'zgargan vaqtni avtomatik saqlaydi."""

    created_at = models.DateTimeField(_("yaratilgan"), auto_now_add=True)
    updated_at = models.DateTimeField(_("o'zgartirilgan"), auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """Material kategoriyasi. Admin qo'shadi, o'chirish o'rniga faolsizlantiradi."""

    name = models.CharField(_("nomi"), max_length=100, unique=True)
    is_active = models.BooleanField(_("faol"), default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("kategoriya")
        verbose_name_plural = _("kategoriyalar")

    def __str__(self) -> str:
        return self.name


class Unit(models.TextChoices):
    """OQ-005 da tasdiqlangan o'lchov birliklari."""

    SHEET = "sheet", _("list")
    PIECE = "piece", _("dona")
    KG = "kg", _("kg")
    LITER = "liter", _("litr")
    METER = "meter", _("metr")
    SQUARE_METER = "m2", _("m²")


def _dimension_field(label: str) -> models.DecimalField:
    """Ixtiyoriy o'lcham maydoni, santimetrda."""
    return models.DecimalField(
        label, max_digits=10, decimal_places=2, null=True, blank=True
    )


class Material(TimeStampedModel):
    """Katalogdagi material turi (nomenklatura).

    Bir kategoriyada nom, rang, o'lchamlar va birlik jamlanmasi takrorlanmaydi.
    Bo'sh o'lchamlar ham teng deb solishtiriladi (PostgreSQL 15+).
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="materials",
        verbose_name=_("kategoriya"),
    )
    name = models.CharField(_("nomi"), max_length=200)
    color = models.CharField(_("rangi"), max_length=50, blank=True, default="")
    length_cm = _dimension_field(_("uzunligi, sm"))
    width_cm = _dimension_field(_("eni, sm"))
    thickness_cm = _dimension_field(_("qalinligi, sm"))
    unit = models.CharField(_("o'lchov birligi"), max_length=10, choices=Unit.choices)
    container_size = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Container capacity (e.g. 12L bucket). Null means no container."
    )
    allowed_roles = models.JSONField(
        default=list, blank=True,
        help_text="Role codes that can see this material. Empty means visible to all."
    )
    is_active = models.BooleanField(_("faol"), default=True)

    class Meta:
        ordering = ["category__name", "name"]
        verbose_name = _("material")
        verbose_name_plural = _("materiallar")
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "category",
                    "name",
                    "color",
                    "length_cm",
                    "width_cm",
                    "thickness_cm",
                    "unit",
                ],
                nulls_distinct=False,
                name="catalog_material_unique_nomenclature",
            ),
            models.CheckConstraint(
                condition=Q(length_cm__isnull=True) | Q(length_cm__gt=0),
                name="catalog_material_length_positive",
            ),
            models.CheckConstraint(
                condition=Q(width_cm__isnull=True) | Q(width_cm__gt=0),
                name="catalog_material_width_positive",
            ),
            models.CheckConstraint(
                condition=Q(thickness_cm__isnull=True) | Q(thickness_cm__gt=0),
                name="catalog_material_thickness_positive",
            ),
            models.CheckConstraint(
                condition=Q(unit__in=Unit.values),
                name="catalog_material_unit_valid",
            ),
        ]

    @property
    def is_integer_unit(self):
        return self.unit in ("sheet", "piece")

    def __str__(self) -> str:
        parts = [self.name, self.color]
        sizes = [self.length_cm, self.width_cm, self.thickness_cm]
        if any(size is not None for size in sizes):
            parts.append(
                "×".join("—" if s is None else f"{s.normalize():f}" for s in sizes)
            )
        return " · ".join(part for part in parts if part)
