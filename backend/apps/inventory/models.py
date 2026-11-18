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

from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

QUANTITY = {"max_digits": 12, "decimal_places": 2}
AMOUNT = {"max_digits": 14, "decimal_places": 2}
UNIT_PRICE = {"max_digits": 18, "decimal_places": 6}
MONEY_STEP = Decimal("0.01")


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
    # OQ-014: minimal chegarani admin belgilaydi; bo'sh — chegara yo'q.
    min_quantity = models.DecimalField(
        _("minimal qoldiq"), null=True, blank=True, **QUANTITY
    )
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
            models.CheckConstraint(
                condition=Q(min_quantity__isnull=True) | Q(min_quantity__gte=0),
                name="inventory_balance_min_not_negative",
            ),
        ]

    @property
    def is_below_min(self) -> bool:
        return (
            self.min_quantity is not None and self.quantity_on_hand < self.min_quantity
        )

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


class StockIssue(models.Model):
    """Chiqim hujjati (PCRM-44): material ombordan ishchiga amalda berildi.

    OQ-002: qoldiq aynan shu paytda kamayadi. Qaysi partiyadan qancha olingani
    ``StockIssueAllocation`` qatorlarida, qoldiq harakati esa ``StockMovement``
    da (``reference_kind="issue"``) saqlanadi. Hujjat o'zgartirilmaydi.

    ``project_id`` — loyiha raqami; loyihalar moduli kelguncha oddiy son
    (``expenses.Expense.project_id`` bilan bir xil yondashuv).
    """

    material = models.ForeignKey(
        "catalog.Material",
        on_delete=models.PROTECT,
        related_name="issues",
        verbose_name=_("material"),
    )
    quantity = models.DecimalField(_("miqdor"), **QUANTITY)
    issued_on = models.DateField(_("chiqim sanasi"))
    recipient_name = models.CharField(_("kim oldi"), max_length=200)
    project_id = models.PositiveBigIntegerField(
        _("loyiha raqami"), null=True, blank=True
    )
    note = models.CharField(_("izoh"), max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("kiritgan"),
    )
    created_at = models.DateTimeField(_("yaratilgan"), auto_now_add=True)

    class Meta:
        ordering = ["-issued_on", "-id"]
        verbose_name = _("chiqim")
        verbose_name_plural = _("chiqimlar")
        indexes = [models.Index(fields=["project_id"], name="inventory_issue_project")]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0), name="inventory_issue_quantity_positive"
            ),
        ]

    def __str__(self) -> str:
        """Chiqimni qisqa ko'rinishda qaytaradi: raqam, material va miqdor."""
        return f"#{self.pk} · {self.material} · {self.quantity}"

    def total_cost(self) -> Decimal:
        """Chiqim tannarxi USD'da: har qism miqdori × partiya narxi, sentgacha.

        Oraliq ko'paytmalar yaxlitlanmaydi, faqat yakuniy yig'indi 0.01 gacha
        ``ROUND_HALF_UP`` bilan yaxlitlanadi.
        """
        return allocations_cost(self.allocations.all())


class StockIssueAllocation(models.Model):
    """Chiqimning bitta partiyadan olingan qismi.

    Tannarx partiyaning o'zgarmas ``unit_price`` idan olinadi (USD), shuning
    uchun keyingi kirimlar eski chiqim qiymatini o'zgartirmaydi.
    """

    issue = models.ForeignKey(
        StockIssue,
        on_delete=models.PROTECT,
        related_name="allocations",
        verbose_name=_("chiqim"),
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="issue_allocations",
        verbose_name=_("partiya"),
    )
    quantity = models.DecimalField(_("miqdor"), **QUANTITY)

    class Meta:
        ordering = ["id"]
        verbose_name = _("chiqim partiyasi")
        verbose_name_plural = _("chiqim partiyalari")
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="inventory_issue_alloc_quantity_positive",
            ),
            models.UniqueConstraint(
                fields=["issue", "batch"], name="inventory_issue_alloc_unique_batch"
            ),
        ]

    def __str__(self) -> str:
        """Qismni ko'rsatadi: chiqim, partiya va miqdor."""
        return f"#{self.issue_id} ← partiya #{self.batch_id} · {self.quantity}"


def allocations_cost(allocations) -> Decimal:
    """Partiya qismlarining USD qiymati: ``Σ miqdor × partiya narxi``, sentgacha.

    Chiqim, qaytarish va hisobdan chiqarish tannarxi shu bitta qoida bilan
    hisoblanadi; faqat yakuniy yig'indi ``ROUND_HALF_UP`` bilan yaxlitlanadi.
    """
    total = sum(
        (part.quantity * part.batch.unit_price for part in allocations), Decimal("0")
    )
    return total.quantize(MONEY_STEP, rounding=ROUND_HALF_UP)


class RequestStatus(models.TextChoices):
    """Tasdiqlanadigan so'rov holati: kutilmoqda, tasdiqlangan yoki rad etilgan."""

    PENDING = "pending", _("kutilmoqda")
    APPROVED = "approved", _("tasdiqlangan")
    REJECTED = "rejected", _("rad etilgan")


def approval_constraints(prefix: str) -> list[models.BaseConstraint]:
    """Tasdiqlanadigan so'rovlar uchun umumiy baza cheklovlari.

    Holat ro'yxatdagi qiymat bo'ladi; kutilayotgan so'rovda qaror egasi va
    vaqti bo'sh, qaror qilinganida esa ikkalasi to'ldirilgan; miqdor musbat.
    """
    return [
        models.CheckConstraint(
            condition=Q(status__in=RequestStatus.values),
            name=f"{prefix}_status_valid",
        ),
        models.CheckConstraint(
            condition=(
                Q(status=RequestStatus.PENDING)
                & Q(decided_by__isnull=True)
                & Q(decided_at__isnull=True)
            )
            | (
                ~Q(status=RequestStatus.PENDING)
                & Q(decided_by__isnull=False)
                & Q(decided_at__isnull=False)
            ),
            name=f"{prefix}_decision_consistent",
        ),
        models.CheckConstraint(
            condition=Q(quantity__gt=0), name=f"{prefix}_quantity_positive"
        ),
    ]


class ApprovalRequest(models.Model):
    """Tasdiqlanadigan ombor so'rovining umumiy maydonlari.

    Qaytarish va hisobdan chiqarish shu asosda quriladi. So'rov kutilayotganda
    qoldiq o'zgarmaydi: tasdiqlanganda harakat yoziladi, rad etilganda — yo'q.
    Qaror bir marta qabul qilinadi, kim va qachon qaror qilgani saqlanadi,
    so'rov o'chirilmaydi.
    """

    quantity = models.DecimalField(_("miqdor"), **QUANTITY)
    status = models.CharField(
        _("holati"),
        max_length=10,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("kiritgan"),
    )
    created_at = models.DateTimeField(_("yaratilgan"), auto_now_add=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name=_("qaror qilgan"),
    )
    decided_at = models.DateTimeField(_("qaror vaqti"), null=True, blank=True)
    decision_note = models.CharField(_("qaror izohi"), max_length=500, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-id"]

    @property
    def is_pending(self) -> bool:
        """So'rov hali qaror kutayotganini bildiradi."""
        return self.status == RequestStatus.PENDING

    def total_cost(self) -> Decimal:
        """So'rovdagi materialning USD qiymati (partiya narxlari bo'yicha)."""
        return allocations_cost(self.allocations.all())


class StockReturn(ApprovalRequest):
    """Qaytarish so'rovi (OQ-003): ishchi ishlatmagan materialni omborga qaytaradi.

    Doim asl chiqimga bog'lanadi. Ombor mas'uli tasdiqlagandan keyin qoldiq
    oshadi va material qaysi partiyadan chiqqan bo'lsa, o'shanga qaytadi.
    Jami tasdiqlangan qaytarish asl chiqimdan oshmaydi.
    """

    issue = models.ForeignKey(
        StockIssue,
        on_delete=models.PROTECT,
        related_name="returns",
        verbose_name=_("asl chiqim"),
    )
    returned_on = models.DateField(_("qaytarilgan sana"))
    reason = models.CharField(_("sabab"), max_length=500, blank=True)

    class Meta(ApprovalRequest.Meta):
        verbose_name = _("qaytarish")
        verbose_name_plural = _("qaytarishlar")
        constraints = approval_constraints("inventory_return")

    def __str__(self) -> str:
        """Qaytarishni qisqa ko'rsatadi: raqam, asl chiqim, miqdor va holat."""
        return f"#{self.pk} ← chiqim #{self.issue_id} · {self.quantity} · {self.status}"


class StockReturnAllocation(models.Model):
    """Qaytarishning bitta partiyaga tushadigan qismi (asl chiqim partiyasi)."""

    stock_return = models.ForeignKey(
        StockReturn,
        on_delete=models.PROTECT,
        related_name="allocations",
        verbose_name=_("qaytarish"),
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="return_allocations",
        verbose_name=_("partiya"),
    )
    quantity = models.DecimalField(_("miqdor"), **QUANTITY)

    class Meta:
        ordering = ["id"]
        verbose_name = _("qaytarish partiyasi")
        verbose_name_plural = _("qaytarish partiyalari")
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="inventory_return_alloc_quantity_positive",
            ),
            models.UniqueConstraint(
                fields=["stock_return", "batch"],
                name="inventory_return_alloc_unique_batch",
            ),
        ]

    def __str__(self) -> str:
        """Qismni ko'rsatadi: qaytarish, partiya va miqdor."""
        return f"#{self.stock_return_id} → partiya #{self.batch_id} · {self.quantity}"


class WriteOff(ApprovalRequest):
    """Hisobdan chiqarish so'rovi (OQ-007): yaroqsiz material.

    Ombor mas'uli sabab bilan so'rov yuboradi, admin tasdiqlaydi. Qoldiq faqat
    tasdiqlanganda kamayadi; kutilayotgan yoki rad etilgan so'rov qoldiqqa
    tegmaydi. Qoldiq tasdiq paytida qulf ostida qayta tekshiriladi.
    """

    material = models.ForeignKey(
        "catalog.Material",
        on_delete=models.PROTECT,
        related_name="write_offs",
        verbose_name=_("material"),
    )
    reason = models.CharField(_("sabab"), max_length=500)

    class Meta(ApprovalRequest.Meta):
        verbose_name = _("hisobdan chiqarish")
        verbose_name_plural = _("hisobdan chiqarishlar")
        constraints = [
            *approval_constraints("inventory_writeoff"),
            models.CheckConstraint(
                condition=~Q(reason=""), name="inventory_writeoff_reason_required"
            ),
        ]

    def __str__(self) -> str:
        """So'rovni qisqa ko'rsatadi: raqam, material, miqdor va holat."""
        return f"#{self.pk} · {self.material} · {self.quantity} · {self.status}"


class WriteOffAllocation(models.Model):
    """Hisobdan chiqariladigan materialning bitta partiyadagi qismi."""

    write_off = models.ForeignKey(
        WriteOff,
        on_delete=models.PROTECT,
        related_name="allocations",
        verbose_name=_("hisobdan chiqarish"),
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="write_off_allocations",
        verbose_name=_("partiya"),
    )
    quantity = models.DecimalField(_("miqdor"), **QUANTITY)

    class Meta:
        ordering = ["id"]
        verbose_name = _("hisobdan chiqarish partiyasi")
        verbose_name_plural = _("hisobdan chiqarish partiyalari")
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="inventory_writeoff_alloc_quantity_positive",
            ),
            models.UniqueConstraint(
                fields=["write_off", "batch"],
                name="inventory_writeoff_alloc_unique_batch",
            ),
        ]

    def __str__(self) -> str:
        """Qismni ko'rsatadi: so'rov, partiya va miqdor."""
        return f"#{self.write_off_id} ← partiya #{self.batch_id} · {self.quantity}"
