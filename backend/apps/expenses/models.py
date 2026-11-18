"""Qo'shimcha xarajatlar modellari (PCRM-46).

Soliq, mahsulot, stanok va boshqa qo'shimcha xarajatlar shu yerda yoziladi
(TZ 6.6, OQ-010). Barcha summalar faqat AQSH dollarida (USD) saqlanadi —
2026-11-18 qarori, docs/09-decisions/decision-log.md.

Xarajat yozuvlari o'chirilmaydi va tahrirlanmaydi (TZ 6.8): tarix buzilmasligi
uchun ular faqat qo'shiladi.
"""

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import get_language, gettext_lazy as _

# Tizimdagi yagona valyuta. Boshqa qiymatni server ham, baza ham rad etadi.
USD = "USD"


class Currency(models.TextChoices):
    """Ruxsat etilgan valyutalar ro'yxati. Hozircha faqat USD."""

    USD = USD, _("AQSH dollari")


class ExpenseType(models.Model):
    """Xarajat turi: soliq, mahsulot, stanok va admin qo'shgan boshqalar.

    Turni admin yaratadi, shuning uchun uning nomi uch tilda bazada saqlanadi.
    ``code`` o'zgarmas va frontend uchun barqaror identifikator bo'lib xizmat
    qiladi. Tur o'chirilmaydi, faqat ``is_active=False`` bilan yashiriladi.
    """

    code = models.SlugField(_("kod"), max_length=50, unique=True)
    name_uz = models.CharField(_("nomi (o'zbekcha)"), max_length=100)
    name_ru = models.CharField(
        _("nomi (ruscha)"), max_length=100, blank=True, default=""
    )
    name_en = models.CharField(
        _("nomi (inglizcha)"), max_length=100, blank=True, default=""
    )
    is_active = models.BooleanField(_("faol"), default=True)

    class Meta:
        ordering = ["name_uz"]
        verbose_name = _("xarajat turi")
        verbose_name_plural = _("xarajat turlari")

    def __str__(self) -> str:
        """Admin panel va ro'yxatlarda turni joriy tildagi nomi bilan ko'rsatadi."""
        return self.localized_name()

    def localized_name(self, language: str | None = None) -> str:
        """Tur nomini so'ralgan yoki joriy tilda qaytaradi.

        Ruscha yoki inglizcha nom kiritilmagan bo'lsa, o'zbekcha nom qaytadi,
        shunda foydalanuvchi hech qachon bo'sh nom ko'rmaydi.
        """
        language = (language or get_language() or "uz")[:2]
        translated = getattr(self, f"name_{language}", "")
        return translated or self.name_uz


class Expense(models.Model):
    """Bitta qo'shimcha xarajat yozuvi.

    ``project_id`` — loyiha raqami. Loyihalar moduli 1-qismdan keyin keladi
    (OQ-010), shuning uchun hozir bu oddiy son. Modul qo'shilganda u
    ``projects.Project`` ga tashqi kalit (ForeignKey) bo'lib o'zgaradi.
    Bo'sh qiymat — loyihaga bog'lanmagan umumiy xarajat (TZ 6.6).
    """

    expense_type = models.ForeignKey(
        ExpenseType,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name=_("xarajat turi"),
    )
    amount = models.DecimalField(_("summa"), max_digits=14, decimal_places=2)
    currency = models.CharField(
        _("valyuta"), max_length=3, choices=Currency.choices, default=USD
    )
    spent_on = models.DateField(_("xarajat sanasi"))
    project_id = models.PositiveBigIntegerField(
        _("loyiha raqami"), null=True, blank=True
    )
    note = models.TextField(_("izoh"), blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("kim kiritdi"),
    )
    created_at = models.DateTimeField(_("kiritilgan vaqt"), auto_now_add=True)
    # TZ 6.8, BR-11/12: xato xarajat o'chirilmaydi. Uni teskari yozuv bekor
    # qiladi: summasi manfiy, ``reverses`` — asl yozuv, ``note`` — sabab.
    # Asl yozuv o'zgarmaydi; bitta yozuvni faqat bir marta bekor qilish mumkin.
    reverses = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reversal",
        verbose_name=_("bekor qilingan yozuv"),
    )

    class Meta:
        ordering = ["-spent_on", "-id"]
        verbose_name = _("qo'shimcha xarajat")
        verbose_name_plural = _("qo'shimcha xarajatlar")
        constraints = [
            # Oddiy yozuv musbat, teskari yozuv manfiy: yig'indi o'zi to'g'ri chiqadi.
            models.CheckConstraint(
                condition=(Q(reverses__isnull=True) & Q(amount__gt=0))
                | (Q(reverses__isnull=False) & Q(amount__lt=0) & ~Q(note="")),
                name="expenses_expense_amount_sign",
            ),
            models.CheckConstraint(
                condition=Q(currency=USD),
                name="expenses_expense_currency_usd_only",
            ),
        ]
        indexes = [
            models.Index(fields=["project_id"], name="expenses_project_idx"),
        ]

    def __str__(self) -> str:
        """Xarajatni qisqa ko'rinishda qaytaradi: tur, summa va sana."""
        return f"{self.expense_type} · ${self.amount} · {self.spent_on}"

    @property
    def is_reversal(self) -> bool:
        """Bu yozuv boshqa xarajatni bekor qiluvchi teskari yozuvmi."""
        return self.reverses_id is not None
