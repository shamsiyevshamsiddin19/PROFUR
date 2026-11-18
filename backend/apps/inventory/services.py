"""Qoldiqni o'zgartiradigan yagona joy (shartnoma, 6-bo'lim).

View yoki serializer qoldiqni to'g'ridan-to'g'ri o'zgartirmaydi. Har bir amal
material qoldig'i qatorini ``select_for_update()`` bilan qulflaydi, shuning
uchun bir vaqtdagi so'rovlar navbat bilan bajariladi.

Chiqim (``decrease``) va qaytarish (``increase``) shu modulga PCRM-44 da
Akbar tomonidan qo'shiladi. Qoldiq yetarliligini ular ``ensure_available()``
orqali, qulflangan ``locked_balance()`` ustida tekshiradi (OQ-006).
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction

from apps.catalog.models import Material

from .models import Batch, Currency, MovementType, StockBalance, StockMovement

UNIT_PRICE_STEP = Decimal("0.000001")


def calculate_unit_price(total_amount: Decimal, quantity: Decimal) -> Decimal:
    """Birlik narxi = summa / miqdor, 6 xonagacha ``ROUND_HALF_UP``.

    Hujjatdagi summa aynan saqlanadi; hisobotlar summani ``total_amount`` dan
    oladi va ``unit_price × quantity`` ni qayta hisoblamaydi.
    """
    return (total_amount / quantity).quantize(UNIT_PRICE_STEP, rounding=ROUND_HALF_UP)


class InsufficientStockError(Exception):
    """Qoldiq yetmaydi: chiqim rad etiladi (OQ-006). API'da 409 ``insufficient_stock``."""

    def __init__(self, available: Decimal, requested: Decimal):
        self.available = available
        self.requested = requested
        super().__init__(f"available={available} requested={requested}")


def locked_balance(material: Material) -> StockBalance:
    """Material qoldig'i qatorini qulflab qaytaradi (yo'q bo'lsa yaratadi).

    Faqat ``transaction.atomic()`` ichida chaqiriladi: qulf tranzaksiya
    tugaguncha turadi va boshqa so'rov shu materialni kutib turadi.
    """
    StockBalance.objects.get_or_create(material=material)
    return StockBalance.objects.select_for_update().get(material=material)


def ensure_available(balance: StockBalance, quantity: Decimal) -> None:
    """Qulflangan qoldiqdan ``quantity`` ni ayirish mumkinligini tekshiradi.

    Yetmasa ``InsufficientStockError``. Chiqim, hisobdan chiqarish va boshqa
    kamaytiruvchi amallar shu bitta tekshiruvdan foydalanadi.
    """
    if quantity > balance.quantity_on_hand:
        raise InsufficientStockError(balance.quantity_on_hand, quantity)


@transaction.atomic
def set_min_quantity(material: Material, min_quantity: Decimal | None) -> StockBalance:
    """OQ-014: minimal chegarani o'rnatadi yoki olib tashlaydi (``None``)."""
    balance = locked_balance(material)
    balance.min_quantity = min_quantity
    balance.save(update_fields=["min_quantity", "updated_at"])
    return balance


@transaction.atomic
def receive(
    *,
    material: Material,
    received_on: date,
    quantity: Decimal,
    total_amount: Decimal,
    user,
    currency: str = Currency.USD,
    supplier: str = "",
    document_number: str = "",
    note: str = "",
) -> tuple[Batch, StockBalance]:
    """Kirimni yozadi: yangi partiya, ``receipt`` harakati va oshgan qoldiq.

    Uchala yozuv bitta tranzaksiyada saqlanadi: biror qadam xato bersa,
    hech narsa saqlanmaydi. Qiymatlar oldindan serializer'da tekshirilgan
    bo'lishi kerak; baza cheklovlari oxirgi himoya.
    """
    balance = locked_balance(material)
    batch = Batch.objects.create(
        material=material,
        received_on=received_on,
        quantity=quantity,
        quantity_remaining=quantity,
        total_amount=total_amount,
        unit_price=calculate_unit_price(total_amount, quantity),
        currency=currency,
        supplier=supplier,
        document_number=document_number,
        note=note,
        created_by=user,
    )
    balance.quantity_on_hand += quantity
    balance.save(update_fields=["quantity_on_hand", "updated_at"])
    StockMovement.objects.create(
        type=MovementType.RECEIPT,
        material=material,
        batch=batch,
        quantity=quantity,
        quantity_on_hand_after=balance.quantity_on_hand,
        reference_kind="receipt",
        reference_id=batch.pk,
        created_by=user,
    )
    return batch, balance
