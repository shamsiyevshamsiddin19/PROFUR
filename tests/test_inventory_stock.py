"""PCRM-42: qoldiq, minimal chegara, partiyalar va harakatlar tarixi (shartnoma, 5-bo'lim)."""

from datetime import timedelta
from decimal import Decimal

import pytest
from accounts.models import Role
from apps.catalog.models import Category, Material, Unit
from apps.inventory import services
from apps.inventory.models import Batch, StockBalance
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

STOCK = "/api/v1/stock/"
MOVEMENTS = "/api/v1/movements/"
VIEW = "inventory.view_stock"
PRICES = "inventory.view_purchase_price"
SET_MIN = "inventory.change_min_quantity"


def make_user(username: str, *codes: str):
    user = get_user_model().objects.create_user(username=username, password="x")
    if codes:
        role = Role.objects.create(
            code=f"TEST_{username.upper()}", name=username, permissions=list(codes)
        )
        user.roles.add(role)
    return user


def client_for(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def keeper_user():
    return make_user("keeper", VIEW, PRICES, SET_MIN)


@pytest.fixture
def keeper(keeper_user) -> APIClient:
    return client_for(keeper_user)


@pytest.fixture
def supervisor() -> APIClient:
    """Ishlab chiqarish nazoratchisi: miqdorni ko'radi, narxni emas (OQ-041)."""
    return client_for(make_user("supervisor", VIEW))


@pytest.fixture
def egger() -> Material:
    return Material.objects.create(
        category=Category.objects.get(name="LDSP"),
        name="LDSP Egger",
        color="oq",
        thickness_cm=Decimal("1.60"),
        unit=Unit.SHEET,
    )


@pytest.fixture
def glue() -> Material:
    return Material.objects.create(
        category=Category.objects.get(name="Furnitura"), name="PVA", unit=Unit.KG
    )


def receive(material, user, quantity: str, total: str, days_ago: int = 0) -> Batch:
    batch, _ = services.receive(
        material=material,
        received_on=timezone.localdate() - timedelta(days=days_ago),
        quantity=Decimal(quantity),
        total_amount=Decimal(total),
        user=user,
    )
    return batch


@pytest.fixture
def stocked(egger, keeper_user) -> Material:
    """Ikki narxdagi kirim: 20 × 27 va 15 × 30 → qoldiq 35, qiymati 990."""
    receive(egger, keeper_user, "20", "540", days_ago=3)
    receive(egger, keeper_user, "15", "450")
    return egger


# --- Qoldiq ro'yxati ------------------------------------------------------------


def test_stock_row_matches_contract(keeper, stocked):
    response = keeper.get(f"{STOCK}{stocked.pk}/")

    assert response.status_code == 200
    assert response.data == {
        "material": {
            "id": stocked.pk,
            "display_name": "LDSP Egger · oq · —×—×1.6",
            "unit": "sheet",
            "category": {"id": stocked.category_id, "name": "LDSP"},
        },
        "quantity_on_hand": "35.00",
        "open_batches": 2,
        "min_quantity": None,
        "is_below_min": False,
        "value_by_currency": [{"currency": "USD", "amount": "990.00"}],
    }


def test_material_without_receipts_has_zero_stock(keeper, glue):
    response = keeper.get(f"{STOCK}{glue.pk}/")

    assert response.data["quantity_on_hand"] == "0.00"
    assert response.data["open_batches"] == 0
    assert response.data["value_by_currency"] == []


def test_value_hidden_without_price_permission(supervisor, stocked):
    response = supervisor.get(f"{STOCK}{stocked.pk}/")

    assert response.status_code == 200
    assert response.data["quantity_on_hand"] == "35.00"
    assert "value_by_currency" not in response.data


def test_spent_batch_is_not_counted(keeper, stocked):
    Batch.objects.filter(material=stocked, quantity="20").update(quantity_remaining=0)

    response = keeper.get(f"{STOCK}{stocked.pk}/")

    assert response.data["open_batches"] == 1
    assert response.data["value_by_currency"] == [
        {"currency": "USD", "amount": "450.00"}
    ]


def test_stock_list_filters(keeper, stocked, glue):
    def ids(**params):
        response = keeper.get(STOCK, params)
        assert response.status_code == 200
        return [row["material"]["id"] for row in response.data["results"]]

    assert set(ids()) >= {stocked.pk, glue.pk}
    assert ids(search="egger") == [stocked.pk]
    assert ids(category=glue.category_id) == [glue.pk]
    assert ids(below_min="true") == []
    assert keeper.get(STOCK, {"below_min": "maybe"}).status_code == 400
    assert keeper.get(STOCK, {"category": "x"}).status_code == 400


# --- Minimal chegara (OQ-014) ---------------------------------------------------


def test_min_quantity_marks_material_below_limit(keeper, stocked, glue):
    url = f"{STOCK}{stocked.pk}/"

    response = keeper.patch(url, {"min_quantity": "50"}, format="json")

    assert response.status_code == 200
    assert response.data["min_quantity"] == "50.00"
    assert response.data["is_below_min"] is True
    below = keeper.get(STOCK, {"below_min": "true"}).data["results"]
    assert [row["material"]["id"] for row in below] == [stocked.pk]

    keeper.patch(url, {"min_quantity": "30"}, format="json")
    assert keeper.get(url).data["is_below_min"] is False

    cleared = keeper.patch(url, {"min_quantity": None}, format="json")
    assert cleared.data["min_quantity"] is None


def test_min_quantity_on_material_without_receipts(keeper, glue):
    response = keeper.patch(f"{STOCK}{glue.pk}/", {"min_quantity": "5"}, format="json")

    assert response.status_code == 200
    assert response.data["is_below_min"] is True
    assert StockBalance.objects.get(material=glue).quantity_on_hand == 0


def test_min_quantity_validation(keeper, stocked):
    url = f"{STOCK}{stocked.pk}/"

    negative = keeper.patch(url, {"min_quantity": "-1"}, format="json")
    assert negative.status_code == 400
    assert negative.data["min_quantity"][0].code == "min_value"
    assert keeper.patch(url, {}, format="json").status_code == 400


def test_setting_min_needs_permission(supervisor, stocked):
    response = supervisor.patch(
        f"{STOCK}{stocked.pk}/", {"min_quantity": "5"}, format="json"
    )

    assert response.status_code == 403


def test_stock_is_read_only_otherwise(keeper, stocked):
    url = f"{STOCK}{stocked.pk}/"

    assert keeper.put(url, {}, format="json").status_code == 405
    assert keeper.delete(url).status_code == 405
    assert keeper.post(STOCK, {}, format="json").status_code == 405


# --- Partiyalar -----------------------------------------------------------------


def test_open_batches_oldest_first(keeper, stocked):
    response = keeper.get(f"{STOCK}{stocked.pk}/batches/")

    assert response.status_code == 200
    rows = response.data["results"]
    assert [row["unit_price"] for row in rows] == ["27.000000", "30.000000"]
    assert set(rows[0]) == {
        "id",
        "received_on",
        "quantity",
        "quantity_remaining",
        "unit_price",
        "currency",
    }


def test_batches_hide_prices(supervisor, stocked):
    rows = supervisor.get(f"{STOCK}{stocked.pk}/batches/").data["results"]

    assert len(rows) == 2
    assert "unit_price" not in rows[0]
    assert "currency" not in rows[0]


# --- Harakatlar tarixi ----------------------------------------------------------


def test_movement_history_matches_contract(keeper, keeper_user, stocked):
    response = keeper.get(MOVEMENTS, {"material": stocked.pk})

    assert response.status_code == 200
    newest = response.data["results"][0]
    batch = Batch.objects.get(material=stocked, quantity="15")
    assert newest == {
        "id": newest["id"],
        "type": "receipt",
        "material": {
            "id": stocked.pk,
            "display_name": "LDSP Egger · oq · —×—×1.6",
            "unit": "sheet",
        },
        "batch_id": batch.pk,
        "quantity": "15.00",
        "quantity_on_hand_after": "35.00",
        "reference": {"kind": "receipt", "id": batch.pk},
        "reason": "",
        "created_by": {"id": keeper_user.pk, "name": "keeper"},
        "created_at": newest["created_at"],
    }
    assert [row["quantity_on_hand_after"] for row in response.data["results"]] == [
        "35.00",
        "20.00",
    ]


def test_movement_filters(keeper, stocked, glue, keeper_user):
    receive(glue, keeper_user, "5", "10")
    today = timezone.localdate().isoformat()

    def count(**params):
        response = keeper.get(MOVEMENTS, params)
        assert response.status_code == 200
        return response.data["count"]

    assert count() == 3
    assert count(material=glue.pk) == 1
    assert count(type="receipt", date_from=today, date_to=today) == 3
    assert count(type="issue") == 0
    assert keeper.get(MOVEMENTS, {"type": "gift"}).status_code == 400
    assert keeper.get(MOVEMENTS, {"date_from": "18.11.2026"}).status_code == 400


def test_movements_are_read_only_and_need_permission(keeper, stocked):
    assert keeper.post(MOVEMENTS, {}, format="json").status_code == 405
    nobody = client_for(make_user("nobody", "catalog.view_material"))
    assert nobody.get(MOVEMENTS).status_code == 403
    assert nobody.get(STOCK).status_code == 403


# --- Umumiy qoldiq tekshiruvi (Akbar chiqimda ishlatadi) -------------------------


def test_ensure_available_blocks_negative_stock(stocked):
    balance = StockBalance.objects.get(material=stocked)

    services.ensure_available(balance, Decimal("35.00"))
    with pytest.raises(services.InsufficientStockError) as error:
        services.ensure_available(balance, Decimal("35.01"))

    assert error.value.available == Decimal("35.00")
    assert error.value.requested == Decimal("35.01")
