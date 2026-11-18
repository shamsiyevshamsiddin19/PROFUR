"""PCRM-46: xarajatni teskari yozuv bilan bekor qilish va tuzatish (TZ 6.8, BR-12).

Asl yozuv o'chirilmaydi va o'zgarmaydi; teskari yozuv manfiy summa va sabab
bilan qo'shiladi, shuning uchun summalar yig'indisi to'g'ri qoladi.
"""

from decimal import Decimal

import pytest
from accounts.models import Role
from apps.expenses import services
from apps.expenses.models import Expense, ExpenseType
from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

EXPENSES = "/api/v1/expenses/"


def make_user(username: str, *codes: str):
    """``expenses.`` ruxsat kodlari bilan rolga ega foydalanuvchi yaratadi."""
    user = get_user_model().objects.create_user(username=username, password="x")
    role = Role.objects.create(
        code=f"TEST_{username.upper()}",
        name=username,
        permissions=[f"expenses.{code}" for code in codes],
    )
    user.roles.add(role)
    return user


def client_for(user) -> APIClient:
    """Shu foydalanuvchi nomidan so'rov yuboradigan mijoz."""
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def accountant_user():
    """Xarajat kiritadi, ko'radi va bekor qila oladi."""
    return make_user("buxgalter", "add_expense", "view_expense", "reverse_expense")


@pytest.fixture
def accountant(accountant_user) -> APIClient:
    """Buxgalter nomidan mijoz."""
    return client_for(accountant_user)


@pytest.fixture
def expense(accountant_user) -> Expense:
    """Loyihaga bog'langan 150.25 $ soliq xarajati."""
    return Expense.objects.create(
        expense_type=ExpenseType.objects.get(code="tax"),
        amount=Decimal("150.25"),
        spent_on="2026-11-10",
        project_id=7,
        note="Noyabr soligi",
        created_by=accountant_user,
    )


def reverse(client: APIClient, expense_id: int, **body):
    """Xarajatni bekor qilish so'rovini yuboradi."""
    return client.post(f"{EXPENSES}{expense_id}/reverse/", body, format="json")


def test_reversal_keeps_original_and_nets_total(accountant, expense):
    """Teskari yozuv manfiy, asl yozuv o'zgarmaydi, yig'indi 0."""
    response = reverse(accountant, expense.pk, reason="Ikki marta kiritilgan")

    assert response.status_code == 201, response.data
    reversal = response.data["reversal"]
    assert reversal["amount"] == "-150.25"
    assert reversal["reverses"] == expense.pk
    assert reversal["note"] == "Ikki marta kiritilgan"
    assert reversal["project_id"] == 7
    assert reversal["currency"] == "USD"
    assert response.data["replacement"] is None
    expense.refresh_from_db()
    assert expense.amount == Decimal("150.25")
    assert Expense.objects.aggregate(total=Sum("amount"))["total"] == Decimal("0")
    detail = accountant.get(f"{EXPENSES}{expense.pk}/").data
    assert detail["reversal"]["id"] == reversal["id"]
    assert detail["reversal"]["reason"] == "Ikki marta kiritilgan"


def test_correction_adds_reversal_and_new_entry_together(accountant, expense):
    """Tuzatish: teskari yozuv va to'g'ri yangi yozuv bitta so'rovda."""
    response = reverse(
        accountant,
        expense.pk,
        reason="Summa xato",
        replacement={
            "expense_type": "tax",
            "amount": "105.25",
            "spent_on": "2026-11-10",
            "project_id": 7,
        },
    )

    assert response.status_code == 201, response.data
    assert response.data["replacement"]["amount"] == "105.25"
    assert response.data["replacement"]["reverses"] is None
    assert Expense.objects.aggregate(total=Sum("amount"))["total"] == Decimal("105.25")


def test_invalid_replacement_saves_nothing(accountant, expense):
    """Yangi yozuv xato bo'lsa, teskari yozuv ham saqlanmaydi (400)."""
    response = reverse(
        accountant,
        expense.pk,
        reason="Summa xato",
        replacement={"expense_type": "tax", "amount": "-5", "spent_on": "2026-11-10"},
    )

    assert response.status_code == 400
    assert Expense.objects.count() == 1


def test_expense_can_be_reversed_only_once(accountant, expense):
    """Ikkinchi marta bekor qilish va teskari yozuvni bekor qilish — 409."""
    reversal_id = reverse(accountant, expense.pk, reason="Xato").data["reversal"]["id"]

    again = reverse(accountant, expense.pk, reason="Yana")
    of_reversal = reverse(accountant, reversal_id, reason="Bekorni bekor")

    assert again.status_code == 409
    assert again.data["code"] == "already_reversed"
    assert of_reversal.status_code == 409
    assert of_reversal.data["code"] == "reversal_not_reversible"
    assert Expense.objects.count() == 2


def test_service_blocks_double_reversal(accountant_user, expense):
    """Servis darajasida ham ikkinchi teskari yozuv yaratilmaydi."""
    services.reverse_expense(expense=expense, reason="Xato", user=accountant_user)

    with pytest.raises(services.ExpenseNotReversibleError):
        services.reverse_expense(expense=expense, reason="Yana", user=accountant_user)


def test_reason_is_required(accountant, expense):
    """Sababsiz bekor qilish 400."""
    assert reverse(accountant, expense.pk, reason="   ").status_code == 400
    assert reverse(accountant, expense.pk).status_code == 400
    assert Expense.objects.count() == 1


def test_reversal_needs_permission(expense):
    """``expenses.reverse_expense`` ruxsatisiz — 403; tahrir va o'chirish hamon 405."""
    clerk = client_for(make_user("kotib", "add_expense", "view_expense"))

    assert reverse(clerk, expense.pk, reason="Xato").status_code == 403
    assert clerk.delete(f"{EXPENSES}{expense.pk}/").status_code == 405
    assert clerk.patch(f"{EXPENSES}{expense.pk}/", {}, format="json").status_code == 405
    assert Expense.objects.count() == 1


def test_reversal_message_follows_language(accountant, expense):
    """409 xabari so'ralgan tilda."""
    reverse(accountant, expense.pk, reason="Xato")

    response = accountant.post(
        f"{EXPENSES}{expense.pk}/reverse/",
        {"reason": "Yana"},
        format="json",
        HTTP_ACCEPT_LANGUAGE="en",
    )

    assert str(response.data["detail"]) == "This expense has already been cancelled."
