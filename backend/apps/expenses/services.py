"""Xarajatni bekor qilish va tuzatish (TZ 6.8, BR-11/12).

Xato xarajat o'chirilmaydi va tahrirlanmaydi. Uning o'rniga:

1. teskari yozuv qo'shiladi — o'sha tur, loyiha va summaning manfiy qiymati,
   ``note`` da sabab, ``reverses`` da asl yozuv;
2. kerak bo'lsa, xuddi shu tranzaksiyada to'g'ri yangi yozuv qo'shiladi.

Asl yozuv o'zgarmaydi, shuning uchun summalar yig'indisi doim to'g'ri.
"""

from django.db import transaction
from django.utils import timezone

from .models import Expense


class ExpenseNotReversibleError(Exception):
    """Yozuvni bekor qilib bo'lmaydi. API'da 409 ``code`` bilan.

    ``already_reversed`` — yozuv avval bekor qilingan;
    ``reversal_not_reversible`` — teskari yozuvning o'zini bekor qilib bo'lmaydi.
    """

    def __init__(self, code: str):
        """Xato kodini saqlaydi."""
        self.code = code
        super().__init__(code)


@transaction.atomic
def reverse_expense(
    *, expense: Expense, reason: str, user, replacement: dict | None = None
) -> tuple[Expense, Expense | None]:
    """Xarajatni teskari yozuv bilan bekor qiladi, xohlansa to'g'ri yozuvni qo'shadi.

    Asl yozuv qulflanadi: ikki marta bosilgan yoki parallel so'rovda ikkinchisi
    ``already_reversed`` oladi (``reverses`` ham bazada noyob). Teskari yozuv
    sanasi — bugun. ``replacement`` — tekshirilgan yangi xarajat maydonlari.
    Ikkala yozuv birga saqlanadi yoki birga bekor bo'ladi.
    """
    original = Expense.objects.select_for_update().get(pk=expense.pk)
    if original.is_reversal:
        raise ExpenseNotReversibleError("reversal_not_reversible")
    if Expense.objects.filter(reverses=original).exists():
        raise ExpenseNotReversibleError("already_reversed")
    reversal = Expense.objects.create(
        expense_type=original.expense_type,
        amount=-original.amount,
        currency=original.currency,
        spent_on=timezone.localdate(),
        project_id=original.project_id,
        note=reason,
        reverses=original,
        created_by=user,
    )
    corrected = None
    if replacement is not None:
        corrected = Expense.objects.create(**replacement, created_by=user)
    return reversal, corrected
