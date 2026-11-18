"""Qoldiqni o'zgartiradigan yagona joy (shartnoma, 6-bo'lim).

View yoki serializer qoldiqni to'g'ridan-to'g'ri o'zgartirmaydi. Har bir amal
material qoldig'i qatorini ``select_for_update()`` bilan qulflaydi, shuning
uchun bir vaqtdagi so'rovlar navbat bilan bajariladi.

Chiqim (``decrease``) va qaytarish (``increase``) shu modulga PCRM-44 da
Akbar tomonidan qo'shiladi. Qoldiq yetarliligini ular ``ensure_available()``
orqali, qulflangan ``locked_balance()`` ustida tekshiradi (OQ-006).

PCRM-44, 1-qism: ``decrease()`` va ``issue_stock()`` (chiqim). Qaytarish va
hisobdan chiqarish keyingi qismlarda qo'shiladi.
"""

from collections.abc import Sequence
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple

from django.db import transaction

from apps.catalog.models import Material

from .models import (
    Batch,
    Currency,
    MovementType,
    StockBalance,
    StockIssue,
    StockIssueAllocation,
    StockMovement,
)

UNIT_PRICE_STEP = Decimal("0.000001")


class Allocation(NamedTuple):
    """Qaysi partiyadan qancha olinadi: kamaytiruvchi amallar uchun bitta qism."""

    batch_id: int
    quantity: Decimal


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


class BatchUnavailableError(Exception):
    """Tanlangan partiyada so'ralgan miqdor qolmagan. API'da 409 ``batch_insufficient``.

    Odatda boshqa xodim shu partiyadan bir vaqtda chiqim qilganda yuz beradi:
    serializer tekshiruvidan keyin, qulf ostida aniqlanadi.
    """

    def __init__(self, batch_id: int, available: Decimal, requested: Decimal):
        """Partiya raqami, undagi qoldiq va so'ralgan miqdorni saqlaydi."""
        self.batch_id = batch_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"batch={batch_id} available={available} requested={requested}"
        )


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


def locked_batches(material: Material, batch_ids: Sequence[int]) -> dict[int, Batch]:
    """Materialning ko'rsatilgan partiyalarini qulflab ``{id: Batch}`` ko'rinishida qaytaradi.

    Qulf doim ``id`` tartibida olinadi, shuning uchun ikki parallel so'rov
    bir-birini kutib qolib ketmaydi (deadlock). Boshqa materialning partiyasi
    yoki mavjud bo'lmagan raqam ``ValueError`` beradi: buni serializer oldinroq
    tekshirishi kerak.
    """
    batches = {
        batch.pk: batch
        for batch in Batch.objects.select_for_update()
        .filter(material=material, pk__in=batch_ids)
        .order_by("pk")
    }
    missing = set(batch_ids) - batches.keys()
    if missing:
        raise ValueError(f"Batches {sorted(missing)} do not belong to {material.pk}")
    return batches


@transaction.atomic
def decrease(
    *,
    material: Material,
    quantity: Decimal,
    movement_type: str,
    user,
    reference: tuple[str, int],
    allocations: Sequence[Allocation],
    reason: str = "",
) -> list[StockMovement]:
    """Qoldiqni kamaytiradi: har partiya uchun bitta manfiy harakat yozadi.

    Chiqim, keyinchalik hisobdan chiqarish ham shu funksiyadan foydalanadi.
    Avval material qoldig'i, keyin partiyalar qulflanadi (kirim bilan bir xil
    tartib). Qoldiq yetmasa ``InsufficientStockError`` (OQ-006), partiyada
    yetmasa ``BatchUnavailableError``; ikkala holatda hech narsa saqlanmaydi.

    Partiya tanlash qoidasi PM qaroriga bog'liq (OQ-001), shuning uchun
    funksiya partiyani o'zi tanlamaydi: ``allocations`` majburiy va
    yig'indisi ``quantity`` ga teng bo'lishi kerak.
    """
    if not allocations or sum(part.quantity for part in allocations) != quantity:
        raise ValueError("Allocations must be non-empty and sum up to quantity.")

    balance = locked_balance(material)
    ensure_available(balance, quantity)
    batches = locked_batches(material, [part.batch_id for part in allocations])

    reference_kind, reference_id = reference
    movements = []
    for part in allocations:
        batch = batches[part.batch_id]
        if part.quantity > batch.quantity_remaining:
            raise BatchUnavailableError(
                batch.pk, batch.quantity_remaining, part.quantity
            )
        batch.quantity_remaining -= part.quantity
        batch.save(update_fields=["quantity_remaining"])
        balance.quantity_on_hand -= part.quantity
        movements.append(
            StockMovement.objects.create(
                type=movement_type,
                material=material,
                batch=batch,
                quantity=-part.quantity,
                quantity_on_hand_after=balance.quantity_on_hand,
                reference_kind=reference_kind,
                reference_id=reference_id,
                reason=reason,
                created_by=user,
            )
        )
    balance.save(update_fields=["quantity_on_hand", "updated_at"])
    return movements


@transaction.atomic
def issue_stock(
    *,
    material: Material,
    allocations: Sequence[Allocation],
    issued_on: date,
    recipient_name: str,
    user,
    project_id: int | None = None,
    note: str = "",
) -> tuple[StockIssue, Decimal]:
    """Chiqimni yozadi: hujjat, partiya qismlari, harakatlar va kamaygan qoldiq.

    Hammasi bitta tranzaksiyada: qoldiq yoki partiya yetmasa, chiqim hujjati
    ham saqlanmaydi. Chiqim hujjati va keyingi qoldiqni qaytaradi.
    """
    quantity = sum((part.quantity for part in allocations), Decimal("0"))
    issue = StockIssue.objects.create(
        material=material,
        quantity=quantity,
        issued_on=issued_on,
        recipient_name=recipient_name,
        project_id=project_id,
        note=note,
        created_by=user,
    )
    StockIssueAllocation.objects.bulk_create(
        StockIssueAllocation(
            issue=issue, batch_id=part.batch_id, quantity=part.quantity
        )
        for part in allocations
    )
    movements = decrease(
        material=material,
        quantity=quantity,
        movement_type=MovementType.ISSUE,
        user=user,
        reference=("issue", issue.pk),
        allocations=allocations,
        reason=note,
    )
    return issue, movements[-1].quantity_on_hand_after
