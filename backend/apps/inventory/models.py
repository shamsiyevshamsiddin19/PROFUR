"""Ombor modellari (PCRM-40).

Shartnoma: docs/06-api-contract/warehouse-api-v1.md, 6-bo'lim.

- ``Batch`` — bitta kirim = bitta partiya. Bir material turli narxda kelsa,
  partiyalar birlashtirilmaydi (OQ-001, OQ-008).
- ``StockBalance`` — material bo'yicha umumiy qoldiq. Faqat ``services``
  orqali, qator qulflangan holda o'zgaradi.
- ``StockMovement`` — o'zgarmas tarix: har bir amal yangi yozuv qo'shadi.
- ``IdempotencyKey`` — takror yuborilgan POST so'rovni tanib olish uchun.

Yagona valyuta — USD (qarorlar jurnali, 2026-11-18).
"""

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

QUANTITY = {"max_digits": 12, "decimal_places": 2}
AMOUNT = {"max_digits": 14, "decimal_places": 2}
UNIT_PRICE = {"max_digits": 18, "decimal_places": 6}


class Currency(models.TextChoices):
    USD = "USD", "USD"


class Batch(models.Model):
    """Kirim partiyasi: asl summa saqlanadi, birlik narxi undan hisoblanadi."""

    material = models.ForeignKey(
        "catalog.Material",
        on_delete=models.PROTECT,
        related_name="batches",
        verbose_name=_("material"),
    )
    received_on = models.DateField(_("kirim sanasi"))
    quantity = models.DecimalField(_("miqdor"), **QUANTITY)
    quantity_remaining = models.DecimalField(_("qolgan miqdor"), **QUANTITY)
    total_amount = models.DecimalField(_("umumiy summa"), **AMOUNT)
    unit_price = models.DecimalField(_("birlik narxi"), **UNIT_PRICE)
    currency = models.CharField(
        _("valyuta"), max_length=3, choices=Currency.choices, default=Currency.USD
    )
    supplier = models.CharField(_("yetkazib beruvchi"), max_length=200, blank=True)
    document_number = models.CharField(_("hujjat raqami"), max_length=100, blank=True)
    note = models.CharField(_("izoh"), max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("kiritgan"),
    )
    created_at = models.DateTimeField(_("yaratilgan"), auto_now_add=True)

    class Meta:
        ordering = ["-received_on", "-id"]
        verbose_name = _("partiya")
        verbose_name_plural = _("partiyalar")
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0), name="inventory_batch_quantity_positive"
            ),
            models.CheckConstraint(
                condition=Q(quantity_remaining__gte=0)
                & Q(quantity_remaining__lte=F("quantity")),
                name="inventory_batch_remaining_in_range",
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gt=0),
                name="inventory_batch_total_positive",
            ),
            models.CheckConstraint(
                condition=Q(currency__in=Currency.values),
                name="inventory_batch_currency_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"#{self.pk} · {self.material} · {self.quantity}"


class StockBalance(models.Model):
    """Materialning ombordagi umumiy qoldig'i (bitta material — bitta qator)."""

    material = models.OneToOneField(
        "catalog.Material",
        on_delete=models.PROTECT,
        related_name="stock",
        verbose_name=_("material"),
    )
    quantity_on_hand = models.DecimalField(_("qoldiq"), default=0, **QUANTITY)
    updated_at = models.DateTimeField(_("o'zgartirilgan"), auto_now=True)

    class Meta:
        verbose_name = _("qoldiq")
        verbose_name_plural = _("qoldiqlar")
        constraints = [
            # OQ-006: qoldiq manfiy bo'lishi taqiqlanadi.
            models.CheckConstraint(
                condition=Q(quantity_on_hand__gte=0),
                name="inventory_balance_not_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.material} · {self.quantity_on_hand}"


class MovementType(models.TextChoices):
    RECEIPT = "receipt", _("kirim")
    ISSUE = "issue", _("chiqim")
    RETURN = "return", _("qaytarish")
    WRITE_OFF = "write_off", _("hisobdan chiqarish")
    ADJUSTMENT = "adjustment", _("tuzatish")


class StockMovement(models.Model):
    """Qoldiq harakati. ``quantity`` musbat — qoldiq oshadi, manfiy — kamayadi."""

    type = models.CharField(_("turi"), max_length=20, choices=MovementType.choices)
    material = models.ForeignKey(
        "catalog.Material",
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name=_("material"),
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="movements",
        null=True,
        blank=True,
        verbose_name=_("partiya"),
    )
    quantity = models.DecimalField(_("miqdor"), **QUANTITY)
    quantity_on_hand_after = models.DecimalField(_("keyingi qoldiq"), **QUANTITY)
    reference_kind = models.CharField(_("manba turi"), max_length=30)
    reference_id = models.BigIntegerField(_("manba identifikatori"))
    reason = models.CharField(_("sabab"), max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("kiritgan"),
    )
    created_at = models.DateTimeField(_("yaratilgan"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = _("harakat")
        verbose_name_plural = _("harakatlar")
        indexes = [models.Index(fields=["material", "-created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=~Q(quantity=0), name="inventory_movement_quantity_nonzero"
            ),
            models.CheckConstraint(
                condition=Q(quantity_on_hand_after__gte=0),
                name="inventory_movement_after_not_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.get_type_display()} · {self.material} · {self.quantity}"


class IdempotencyKey(models.Model):
    """Bir foydalanuvchi, manzil va kalit uchun birinchi javob saqlanadi."""

    key = models.UUIDField(_("kalit"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    endpoint = models.CharField(_("manzil"), max_length=100)
    request_hash = models.CharField(_("so'rov xeshi"), max_length=64)
    response_status = models.PositiveSmallIntegerField(_("javob holati"))
    response_body = models.JSONField(_("javob"))
    created_at = models.DateTimeField(_("yaratilgan"), auto_now_add=True)

    class Meta:
        verbose_name = _("idempotentlik kaliti")
        verbose_name_plural = _("idempotentlik kalitlari")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "endpoint", "key"], name="inventory_idempotency_unique"
            ),
        ]
