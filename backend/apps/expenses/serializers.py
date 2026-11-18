"""Xarajatlar API'sidagi ma'lumotni tekshirish va JSON'ga aylantirish.

Pul summasi API'da satr ko'rinishida keladi va ketadi (``"12.50"``), shunda
frontend uni kasr son sifatida buzmaydi. Xato matnlari ``Accept-Language``
bo'yicha uz/ru/en tillarida qaytadi.
"""

from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import USD, Currency, Expense, ExpenseType


class ExpenseTypeSerializer(serializers.ModelSerializer):
    """Xarajat turini ko'rsatadi, yaratadi va tahrirlaydi."""

    name = serializers.SerializerMethodField(help_text=_("Foydalanuvchi tilidagi nom."))

    class Meta:
        model = ExpenseType
        fields = ["id", "code", "name", "name_uz", "name_ru", "name_en", "is_active"]

    def get_name(self, expense_type: ExpenseType) -> str:
        """Tur nomini so'rov tilida qaytaradi (ru/en bo'lmasa — o'zbekcha)."""
        return expense_type.localized_name()

    def validate_code(self, code: str) -> str:
        """Mavjud turning kodini o'zgartirishni taqiqlaydi.

        Kod frontend va hisobotlarda turni aniqlaydi. U o'zgarsa, eski
        bog'lanishlar buziladi.
        """
        if self.instance is not None and code != self.instance.code:
            raise serializers.ValidationError(
                _("Xarajat turining kodini o'zgartirib bo'lmaydi.")
            )
        return code


class ExpenseSerializer(serializers.ModelSerializer):
    """Xarajat yozuvini ko'rsatadi va yangisini yaratishda tekshiradi."""

    expense_type = serializers.SlugRelatedField(
        slug_field="code", queryset=ExpenseType.objects.all()
    )
    expense_type_name = serializers.SerializerMethodField()
    amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=Decimal("0.01"),
        error_messages={
            "min_value": _("Summa 0 dan katta bo'lishi kerak."),
            "max_decimal_places": _(
                "Summada verguldan keyin ko'pi bilan 2 ta raqam bo'lsin."
            ),
        },
    )
    currency = serializers.ChoiceField(
        choices=Currency.choices,
        default=USD,
        error_messages={"invalid_choice": _("Faqat USD valyutasi qabul qilinadi.")},
    )

    class Meta:
        model = Expense
        fields = [
            "id",
            "expense_type",
            "expense_type_name",
            "amount",
            "currency",
            "spent_on",
            "project_id",
            "note",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]
        extra_kwargs = {"project_id": {"min_value": 1}}

    def get_expense_type_name(self, expense: Expense) -> str:
        """Xarajat turi nomini so'rov tilida qaytaradi."""
        return expense.expense_type.localized_name()

    def validate_expense_type(self, expense_type: ExpenseType) -> ExpenseType:
        """Faolsizlantirilgan turga yangi xarajat yozishni rad etadi."""
        if not expense_type.is_active:
            raise serializers.ValidationError(_("Bu xarajat turi faol emas."))
        return expense_type


class ExpenseFilterSerializer(serializers.Serializer):
    """Xarajatlar ro'yxatini filtrlash parametrlarini tekshiradi.

    Hammasi ixtiyoriy: ``expense_type`` (kod), ``project_id``,
    ``date_from`` va ``date_to`` (``YYYY-MM-DD``, ikkalasi ham kiradi).
    """

    expense_type = serializers.SlugField(required=False)
    project_id = serializers.IntegerField(required=False, min_value=1)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, attrs: dict) -> dict:
        """Boshlanish sanasi tugash sanasidan keyin bo'lmasligini tekshiradi."""
        date_from, date_to = attrs.get("date_from"), attrs.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                {"date_to": _("Tugash sanasi boshlanish sanasidan oldin bo'lmasin.")}
            )
        return attrs
