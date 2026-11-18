"""Qoldiqni o'zgartiradigan yagona joy (shartnoma, 6-bo'lim).

View yoki serializer qoldiqni to'g'ridan-to'g'ri o'zgartirmaydi. Har bir amal
material qoldig'i qatorini ``select_for_update()`` bilan qulflaydi, shuning
uchun bir vaqtdagi so'rovlar navbat bilan bajariladi.

Chiqim (``decrease``) va qaytarish (``increase``) shu modulga PCRM-44 da
Akbar tomonidan qo'shiladi. Qoldiq yetarliligini ular ``ensure_available()``
orqali, qulflangan ``locked_balance()`` ustida tekshiradi (OQ-006).

PCRM-44: ``decrease()``/``issue_stock()`` (chiqim), ``increase()`` va
qaytarish so'rovi (OQ-003), hisobdan chiqarish so'rovi (OQ-007). So'rov
kutilayotganda qoldiq o'zgarmaydi; harakat faqat tasdiqda yoziladi.

Qulf tartibi (deadlock bo'lmasligi uchun hamma joyda bir xil): so'rov qatori →
asl chiqim → material qoldig'i → partiyalar ``id`` bo'yicha.
"""

from collections import defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.catalog.models import Material

from .models import (
    Batch,
    Currency,
    MovementType,
    RequestStatus,
    StockBalance,
    StockIssue,
    StockIssueAllocation,
    StockMovement,
    StockReturn,
    StockReturnAllocation,
    WriteOff,
    WriteOffAllocation,
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
    quantity = total_of(allocations)
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


# --- Qaytarish va hisobdan chiqarish -------------------------------------------


class ReturnLimitError(Exception):
    """Qaytarish asl chiqimning shu partiyadan olingan qolgan qismidan oshadi.

    API'da 409 ``return_exceeds_issue``. ``available`` — hali qaytarilmagan
    (va boshqa kutilayotgan so'rovga kiritilmagan) miqdor.
    """

    def __init__(self, batch_id: int, available: Decimal, requested: Decimal):
        """Partiya raqami, qaytarish mumkin bo'lgan va so'ralgan miqdorni saqlaydi."""
        self.batch_id = batch_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"batch={batch_id} available={available} requested={requested}"
        )


class AlreadyDecidedError(Exception):
    """So'rov boshqa qaror bilan yopilgan (masalan, rad etilganni tasdiqlash).

    API'da 409 ``already_decided``. Xuddi shu qarorni takrorlash xato emas:
    u hech narsani o'zgartirmaydi va joriy holatni qaytaradi.
    """

    def __init__(self, status: str):
        """So'rovning joriy holatini saqlaydi."""
        self.status = status
        super().__init__(f"status={status}")


def total_of(allocations: Sequence[Allocation]) -> Decimal:
    """Qismlar miqdorining yig'indisi."""
    return sum((part.quantity for part in allocations), Decimal("0"))


@transaction.atomic
def increase(
    *,
    material: Material,
    quantity: Decimal,
    movement_type: str,
    user,
    reference: tuple[str, int],
    batch: Batch,
    reason: str = "",
) -> StockMovement:
    """Qoldiqni oshiradi: partiya va umumiy qoldiq, bitta musbat harakat.

    Avval material qoldig'i, keyin partiya qulflanadi (``decrease`` bilan bir
    xil tartib). Partiya qoldig'i dastlabki kirimdan oshmasligi kerak — buni
    chaqiruvchi tekshiradi, baza cheklovi esa oxirgi himoya.
    """
    balance = locked_balance(material)
    locked = locked_batches(material, [batch.pk])[batch.pk]
    if locked.quantity_remaining + quantity > locked.quantity:
        raise ValueError(f"Batch {batch.pk} would exceed its received quantity.")
    locked.quantity_remaining += quantity
    locked.save(update_fields=["quantity_remaining"])
    balance.quantity_on_hand += quantity
    balance.save(update_fields=["quantity_on_hand", "updated_at"])
    reference_kind, reference_id = reference
    return StockMovement.objects.create(
        type=movement_type,
        material=material,
        batch=locked,
        quantity=quantity,
        quantity_on_hand_after=balance.quantity_on_hand,
        reference_kind=reference_kind,
        reference_id=reference_id,
        reason=reason,
        created_by=user,
    )


def returnable_by_batch(
    issue: StockIssue, *, exclude_return_id: int | None = None, include_pending: bool
) -> dict[int, Decimal]:
    """Chiqimning har partiyasidan yana qancha qaytarish mumkinligi: ``{batch_id: miqdor}``.

    Chiqim miqdoridan tasdiqlangan (``include_pending`` bo'lsa, kutilayotgan
    ham) qaytarishlar ayiriladi. Rad etilgan so'rovlar hisobga olinmaydi.
    """
    statuses = [RequestStatus.APPROVED]
    if include_pending:
        statuses.append(RequestStatus.PENDING)
    returned = StockReturnAllocation.objects.filter(
        stock_return__issue=issue, stock_return__status__in=statuses
    )
    if exclude_return_id is not None:
        returned = returned.exclude(stock_return_id=exclude_return_id)
    used = defaultdict(
        Decimal,
        returned.values("batch_id")
        .annotate(total=Sum("quantity"))
        .values_list("batch_id", "total"),
    )
    return {
        part.batch_id: part.quantity - used[part.batch_id]
        for part in issue.allocations.all()
    }


def ensure_returnable(
    available: dict[int, Decimal], allocations: Sequence[Allocation]
) -> None:
    """Har qism asl chiqimning shu partiyasidagi qaytarilmagan qismiga sig'ishini tekshiradi."""
    for part in allocations:
        limit = available.get(part.batch_id, Decimal("0"))
        if part.quantity > limit:
            raise ReturnLimitError(part.batch_id, limit, part.quantity)


@transaction.atomic
def request_return(
    *,
    issue: StockIssue,
    allocations: Sequence[Allocation],
    returned_on: date,
    user,
    reason: str = "",
) -> StockReturn:
    """Qaytarish so'rovini yozadi (OQ-003). Qoldiq hali o'zgarmaydi.

    Asl chiqim qatori qulflanadi, shuning uchun bir chiqimga parallel
    yuborilgan so'rovlar navbat bilan tekshiriladi. Kutilayotgan so'rovlar
    ham limitga kiradi: bir xil materialni ikki marta so'rab bo'lmaydi.
    Partiya chiqimda bo'lmasa yoki limit oshsa — ``ReturnLimitError``.
    """
    issue = StockIssue.objects.select_for_update().get(pk=issue.pk)
    ensure_returnable(returnable_by_batch(issue, include_pending=True), allocations)
    stock_return = StockReturn.objects.create(
        issue=issue,
        quantity=total_of(allocations),
        returned_on=returned_on,
        reason=reason,
        created_by=user,
    )
    StockReturnAllocation.objects.bulk_create(
        StockReturnAllocation(
            stock_return=stock_return, batch_id=part.batch_id, quantity=part.quantity
        )
        for part in allocations
    )
    return stock_return


def mark_decided(request_row, status: str, user, note: str) -> None:
    """So'rov qarorini yozadi: holat, kim, qachon va izoh."""
    request_row.status = status
    request_row.decided_by = user
    request_row.decided_at = timezone.now()
    request_row.decision_note = note
    request_row.save(
        update_fields=["status", "decided_by", "decided_at", "decision_note"]
    )


def lock_for_decision(model, pk: int, status: str):
    """So'rovni qulflaydi va qaror qabul qilish mumkinligini aniqlaydi.

    ``(qator, o'zgaradimi)`` qaytaradi. So'rov allaqachon xuddi shu holatda
    bo'lsa — ``False`` (takroriy bosish, hech narsa yozilmaydi). Boshqa qaror
    bilan yopilgan bo'lsa — ``AlreadyDecidedError``.
    """
    row = model.objects.select_for_update().get(pk=pk)
    if row.status == status:
        return row, False
    if not row.is_pending:
        raise AlreadyDecidedError(row.status)
    return row, True


@transaction.atomic
def approve_return(*, return_id: int, user, note: str = "") -> tuple[StockReturn, bool]:
    """Qaytarishni tasdiqlaydi: qoldiq va asl partiyalar oshadi (``return`` harakati).

    Ikki marta tasdiqlash ikkinchi harakat yozmaydi: ``(so'rov, False)``.
    Limit qulf ostida, faqat tasdiqlangan qaytarishlar bo'yicha qayta
    tekshiriladi — jami qaytarish asl chiqimdan oshmaydi.
    """
    stock_return, changed = lock_for_decision(
        StockReturn, return_id, RequestStatus.APPROVED
    )
    if not changed:
        return stock_return, False
    issue = StockIssue.objects.select_for_update().get(pk=stock_return.issue_id)
    parts = [
        Allocation(part.batch_id, part.quantity)
        for part in stock_return.allocations.all()
    ]
    ensure_returnable(
        returnable_by_batch(
            issue, exclude_return_id=stock_return.pk, include_pending=False
        ),
        parts,
    )
    batches = {part.batch_id: part.batch for part in stock_return.allocations.all()}
    for part in parts:
        increase(
            material=issue.material,
            quantity=part.quantity,
            movement_type=MovementType.RETURN,
            user=user,
            reference=("return", stock_return.pk),
            batch=batches[part.batch_id],
            reason=stock_return.reason,
        )
    mark_decided(stock_return, RequestStatus.APPROVED, user, note)
    return stock_return, True


@transaction.atomic
def reject_return(*, return_id: int, user, note: str = "") -> tuple[StockReturn, bool]:
    """Qaytarishni rad etadi. Qoldiq o'zgarmaydi, harakat yozilmaydi."""
    stock_return, changed = lock_for_decision(
        StockReturn, return_id, RequestStatus.REJECTED
    )
    if changed:
        mark_decided(stock_return, RequestStatus.REJECTED, user, note)
    return stock_return, changed


def ensure_batches_have(material: Material, allocations: Sequence[Allocation]) -> None:
    """Qulfsiz oldindan tekshiruv: qoldiq va partiyalarda yetarli material bormi.

    So'rov yaratishda foydalanuvchiga darhol javob berish uchun. Yakuniy
    tekshiruv tasdiq paytida ``decrease()`` ichida qulf ostida bajariladi.
    """
    balance = StockBalance.objects.filter(material=material).first()
    on_hand = balance.quantity_on_hand if balance else Decimal("0")
    total = total_of(allocations)
    if total > on_hand:
        raise InsufficientStockError(on_hand, total)
    remaining = dict(
        Batch.objects.filter(
            material=material, pk__in=[part.batch_id for part in allocations]
        ).values_list("pk", "quantity_remaining")
    )
    for part in allocations:
        if part.quantity > remaining.get(part.batch_id, Decimal("0")):
            raise BatchUnavailableError(
                part.batch_id, remaining.get(part.batch_id, Decimal("0")), part.quantity
            )


@transaction.atomic
def request_write_off(
    *, material: Material, allocations: Sequence[Allocation], reason: str, user
) -> WriteOff:
    """Hisobdan chiqarish so'rovini yozadi (OQ-007). Qoldiq hali o'zgarmaydi.

    Hozir omborda bo'lmagan miqdorga so'rov yaratilmaydi
    (``InsufficientStockError`` yoki ``BatchUnavailableError``).
    """
    ensure_batches_have(material, allocations)
    write_off = WriteOff.objects.create(
        material=material,
        quantity=total_of(allocations),
        reason=reason,
        created_by=user,
    )
    WriteOffAllocation.objects.bulk_create(
        WriteOffAllocation(
            write_off=write_off, batch_id=part.batch_id, quantity=part.quantity
        )
        for part in allocations
    )
    return write_off


@transaction.atomic
def approve_write_off(
    *, write_off_id: int, user, note: str = ""
) -> tuple[WriteOff, bool]:
    """Admin tasdig'i: qoldiq va partiyalar kamayadi (``write_off`` harakati).

    Qoldiq tasdiq paytida qulf ostida qayta tekshiriladi. Yetmasa
    ``InsufficientStockError``/``BatchUnavailableError`` va so'rov kutilayotgan
    holatda qoladi. Ikki marta tasdiqlash ikkinchi harakat yozmaydi.
    """
    write_off, changed = lock_for_decision(
        WriteOff, write_off_id, RequestStatus.APPROVED
    )
    if not changed:
        return write_off, False
    decrease(
        material=write_off.material,
        quantity=write_off.quantity,
        movement_type=MovementType.WRITE_OFF,
        user=user,
        reference=("write_off", write_off.pk),
        allocations=[
            Allocation(part.batch_id, part.quantity)
            for part in write_off.allocations.all()
        ],
        reason=write_off.reason,
    )
    mark_decided(write_off, RequestStatus.APPROVED, user, note)
    return write_off, True


@transaction.atomic
def reject_write_off(
    *, write_off_id: int, user, note: str = ""
) -> tuple[WriteOff, bool]:
    """Hisobdan chiqarishni rad etadi. Qoldiq o'zgarmaydi, harakat yozilmaydi."""
    write_off, changed = lock_for_decision(
        WriteOff, write_off_id, RequestStatus.REJECTED
    )
    if changed:
        mark_decided(write_off, RequestStatus.REJECTED, user, note)
    return write_off, changed
