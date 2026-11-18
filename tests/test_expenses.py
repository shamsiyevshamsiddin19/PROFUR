"""Qo'shimcha xarajatlar API'si sinovlari (PCRM-46).

Tekshiriladi: faqat USD, musbat summa, ruxsatlar, o'chirish/tahrirlash
taqiqi, filtrlar va uz/ru/en tillaridagi xato xabarlari.
"""

from decimal import Decimal

import pytest
from accounts.models import Role
from apps.expenses.models import Expense, ExpenseType
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.test import APIClient

EXPENSES_URL = "/api/v1/expenses/"
TYPES_URL = "/api/v1/expense-types/"


def make_user(username: str, *permission_codes: str):
    """Berilgan ruxsat kodlari bor rolga ega sinov foydalanuvchisini yaratadi.

    Ruxsatlar real tizimdagidek rol orqali beriladi (``Role.permissions``).
    Kod qisqa yoziladi va ``expenses.`` prefiksi qo'shiladi: ``add_expense``.
    """
    user = get_user_model().objects.create_user(username=username, password="x")
    role = Role.objects.create(
        code=f"TEST_{username.upper()}",
        name=username,
        permissions=[f"expenses.{code}" for code in permission_codes],
    )
    user.roles.add(role)
    return user


def client_for(user) -> APIClient:
    """Shu foydalanuvchi nomidan so'rov yuboradigan API mijozini qaytaradi."""
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def warehouse_user():
    """Xarajat kiritish va ko'rish ruxsati bor ombor xodimi."""
    return make_user("omborchi", "add_expense", "view_expense", "view_expensetype")


@pytest.fixture
def tax_type() -> ExpenseType:
    """Migratsiya qo'shgan "Soliq" turi."""
    return ExpenseType.objects.get(code="tax")


def valid_payload(**overrides) -> dict:
    """To'g'ri xarajat so'rovi tanasini qaytaradi; kerakli maydonni almashtirish mumkin."""
    payload = {
        "expense_type": "tax",
        "amount": "150.25",
        "spent_on": "2026-11-18",
        "project_id": 7,
        "note": "Noyabr soligi",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_initial_expense_types_are_seeded():
    """Migratsiya TZ 6.6 dagi uchta turni uch tilda qo'shadi."""
    codes = set(ExpenseType.objects.values_list("code", flat=True))
    assert {"tax", "products", "machine"} <= codes
    machine = ExpenseType.objects.get(code="machine")
    assert machine.localized_name("ru") == "Станок"
    assert machine.localized_name("en") == "Machine"


@pytest.mark.django_db
def test_create_expense_saves_usd_and_author(warehouse_user, tax_type):
    """To'g'ri so'rov xarajatni USD'da saqlaydi va kiritgan odamni yozadi."""
    response = client_for(warehouse_user).post(
        EXPENSES_URL, valid_payload(), format="json"
    )

    assert response.status_code == 201, response.data
    assert response.data["amount"] == "150.25"
    assert response.data["currency"] == "USD"
    assert response.data["expense_type"] == "tax"
    expense = Expense.objects.get()
    assert expense.amount == Decimal("150.25")
    assert expense.created_by == warehouse_user
    assert expense.expense_type == tax_type


@pytest.mark.django_db
@pytest.mark.parametrize("project", ["missing", None])
def test_project_is_required(warehouse_user, project):
    """OQ-010 (PM tasdiqlagan): xarajat aniq loyihaga biriktiriladi, aks holda 400."""
    payload = valid_payload()
    if project == "missing":
        del payload["project_id"]
    else:
        payload["project_id"] = project

    response = client_for(warehouse_user).post(EXPENSES_URL, payload, format="json")

    assert response.status_code == 400
    assert "project_id" in response.data
    assert not Expense.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("currency", ["UZS", "EUR", "usd"])
def test_non_usd_currency_is_rejected(warehouse_user, currency):
    """USD'dan boshqa valyuta 400 xato bilan rad etiladi va hech narsa saqlanmaydi."""
    response = client_for(warehouse_user).post(
        EXPENSES_URL, valid_payload(currency=currency), format="json"
    )

    assert response.status_code == 400
    assert "currency" in response.data
    assert not Expense.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("amount", ["0", "-5.00", "10.123"])
def test_invalid_amount_is_rejected(warehouse_user, amount):
    """Nol, manfiy yoki 2 xonadan ortiq kasrli summa qabul qilinmaydi."""
    response = client_for(warehouse_user).post(
        EXPENSES_URL, valid_payload(amount=amount), format="json"
    )

    assert response.status_code == 400
    assert "amount" in response.data


@pytest.mark.django_db
def test_inactive_expense_type_is_rejected(warehouse_user, tax_type):
    """Faolsizlantirilgan turga yangi xarajat yozib bo'lmaydi."""
    tax_type.is_active = False
    tax_type.save()

    response = client_for(warehouse_user).post(
        EXPENSES_URL, valid_payload(), format="json"
    )

    assert response.status_code == 400
    assert "expense_type" in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("language", "message"),
    [
        ("uz", "Faqat USD valyutasi qabul qilinadi."),
        ("ru", "Принимается только валюта USD."),
        ("en", "Only USD currency is accepted."),
    ],
)
def test_error_message_follows_request_language(warehouse_user, language, message):
    """Xato xabari ``Accept-Language`` tilida qaytadi (uz/ru/en)."""
    response = client_for(warehouse_user).post(
        EXPENSES_URL,
        valid_payload(currency="EUR"),
        format="json",
        HTTP_ACCEPT_LANGUAGE=language,
    )

    assert response.status_code == 400
    assert str(response.data["currency"][0]) == message


@pytest.mark.django_db
def test_database_rejects_non_usd_and_non_positive_amount(warehouse_user, tax_type):
    """API'ni chetlab o'tgan yozuvni ham baza cheklovlari to'xtatadi."""
    with pytest.raises(IntegrityError):
        Expense.objects.create(
            expense_type=tax_type,
            amount=Decimal("10"),
            currency="EUR",
            spent_on="2026-11-18",
            created_by=warehouse_user,
        )


@pytest.mark.django_db
def test_user_without_permission_cannot_create_or_view():
    """Ruxsati yo'q foydalanuvchi (masalan, ishchi) xarajatni ko'rmaydi va kiritmaydi."""
    client = client_for(make_user("ishchi"))

    assert client.post(EXPENSES_URL, valid_payload(), format="json").status_code == 403
    assert client.get(EXPENSES_URL).status_code == 403


@pytest.mark.django_db
def test_anonymous_request_is_rejected():
    """Tizimga kirmagan so'rov rad etiladi."""
    response = APIClient().get(EXPENSES_URL)
    assert response.status_code == 403


@pytest.mark.django_db
def test_expense_cannot_be_changed_or_deleted(warehouse_user):
    """Xarajat yozuvi tahrirlanmaydi va o'chirilmaydi (TZ 6.8): 405 qaytadi."""
    client = client_for(warehouse_user)
    expense_id = client.post(EXPENSES_URL, valid_payload(), format="json").data["id"]
    detail_url = f"{EXPENSES_URL}{expense_id}/"

    assert (
        client.patch(detail_url, {"amount": "1.00"}, format="json").status_code == 405
    )
    assert client.put(detail_url, valid_payload(), format="json").status_code == 405
    assert client.delete(detail_url).status_code == 405
    assert Expense.objects.get().amount == Decimal("150.25")


@pytest.mark.django_db
def test_list_filters_by_type_project_and_dates(warehouse_user):
    """Ro'yxat tur, loyiha va sana oralig'i bo'yicha filtrlanadi."""
    client = client_for(warehouse_user)
    for payload in [
        valid_payload(spent_on="2026-11-01"),
        valid_payload(spent_on="2026-11-20", project_id=8),
        valid_payload(expense_type="machine", spent_on="2026-11-10"),
    ]:
        assert client.post(EXPENSES_URL, payload, format="json").status_code == 201

    def count(query: str) -> int:
        """Shu filtr bilan ro'yxatdagi yozuvlar sonini qaytaradi."""
        return client.get(f"{EXPENSES_URL}?{query}").data["count"]

    assert count("") == 3
    assert count("expense_type=machine") == 1
    assert count("project_id=8") == 1
    assert count("date_from=2026-11-05&date_to=2026-11-15") == 1


@pytest.mark.django_db
def test_list_rejects_inverted_date_range(warehouse_user):
    """Boshlanish sanasi tugash sanasidan keyin bo'lsa 400 qaytadi."""
    response = client_for(warehouse_user).get(
        f"{EXPENSES_URL}?date_from=2026-11-20&date_to=2026-11-01"
    )
    assert response.status_code == 400
    assert "date_to" in response.data


@pytest.mark.django_db
def test_admin_can_add_and_deactivate_expense_type():
    """Ruxsati bor foydalanuvchi yangi tur qo'shadi va uni faolsizlantiradi."""
    client = client_for(
        make_user("admin", "add_expensetype", "change_expensetype", "view_expensetype")
    )

    created = client.post(
        TYPES_URL,
        {"code": "rent", "name_uz": "Ijara", "name_ru": "Аренда", "name_en": "Rent"},
        format="json",
    )
    assert created.status_code == 201, created.data

    url = f"{TYPES_URL}{created.data['id']}/"
    assert client.patch(url, {"is_active": False}, format="json").status_code == 200
    assert client.delete(url).status_code == 405
    active_codes = [
        t["code"] for t in client.get(f"{TYPES_URL}?is_active=true").data["results"]
    ]
    assert "rent" not in active_codes


@pytest.mark.django_db
def test_expense_type_code_cannot_change(tax_type):
    """Mavjud turning kodi o'zgarmaydi, chunki frontend va hisobotlar unga tayanadi."""
    client = client_for(make_user("admin", "change_expensetype"))

    response = client.patch(
        f"{TYPES_URL}{tax_type.id}/", {"code": "nalog"}, format="json"
    )

    assert response.status_code == 400
    assert "code" in response.data


def test_localized_name_falls_back_to_uzbek():
    """Ruscha yoki inglizcha nom bo'lmasa, o'zbekcha nom qaytadi."""
    expense_type = ExpenseType(code="x", name_uz="Ijara")
    assert expense_type.localized_name("ru") == "Ijara"
    assert expense_type.localized_name("en") == "Ijara"
