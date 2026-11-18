"""PCRM-42/44 integratsiyasi: katalog → kirim → chiqim → qoldiq bitta hisobda mos.

Faqat HTTP API orqali: ikki narxdagi kirim ikki partiya bo'ladi, chiqim
partiyalardan ayiriladi, va qoldiq qatori, ochiq partiyalar, harakatlar tarixi
hamda katalogdagi qoldiq bir-biriga teng bo'lib qoladi. Narx ko'rish ruxsati
bo'lmagan foydalanuvchiga server hech qaysi ombor javobida narx qaytarmaydi.
"""

import uuid
from decimal import Decimal

import pytest
from accounts.models import Role
from apps.inventory.models import Batch, StockBalance, StockMovement
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

PRICE_KEYS = {
    "total_amount",
    "unit_price",
    "currency",
    "value_by_currency",
    "total_cost",
}
KEEPER_CODES = (
    "catalog.view_material",
    "catalog.add_material",
    "inventory.view_stock",
    "inventory.add_receipt",
    "inventory.add_issue",
    "inventory.view_purchase_price",
)
# OQ-041: ishlab chiqarish nazoratchisi miqdorni ko'radi, narxni emas.
SUPERVISOR_CODES = ("catalog.view_material", "inventory.view_stock")


def client_with(username: str, codes: tuple[str, ...]) -> APIClient:
    user = get_user_model().objects.create_user(username=username, password="x")
    role = Role.objects.create(
        code=f"TEST_{username.upper()}", name=username, permissions=list(codes)
    )
    user.roles.add(role)
    client = APIClient()
    client.force_authenticate(user)
    return client


def post(client: APIClient, url: str, body: dict):
    return client.post(url, body, format="json", HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()))


def price_keys_in(data) -> set[str]:
    """JSON javobning istalgan chuqurligidagi narx kalitlari."""
    found: set[str] = set()
    if isinstance(data, dict):
        found |= PRICE_KEYS & data.keys()
        for value in data.values():
            found |= price_keys_in(value)
    elif isinstance(data, list):
        for item in data:
            found |= price_keys_in(item)
    return found


@pytest.fixture
def keeper() -> APIClient:
    return client_with("keeper", KEEPER_CODES)


@pytest.fixture
def flow(keeper):
    """Material → 20 × $27 va 15 × $30 kirim → 25 chiqim (20 + 5)."""
    material = keeper.post(
        "/api/v1/materials/",
        {
            "category_id": keeper.get("/api/v1/categories/", {"search": "LDSP"}).data[
                "results"
            ][0]["id"],
            "name": "LDSP Egger",
            "color": "oq",
            "unit": "sheet",
        },
        format="json",
    )
    assert material.status_code == 201
    material_id = material.data["id"]
    today = timezone.localdate().isoformat()
    first = post(
        keeper,
        "/api/v1/receipts/",
        {
            "material_id": material_id,
            "received_on": today,
            "quantity": "20",
            "total_amount": "540",
            "currency": "USD",
        },
    )
    second = post(
        keeper,
        "/api/v1/receipts/",
        {
            "material_id": material_id,
            "received_on": today,
            "quantity": "15",
            "total_amount": "450",
            "currency": "USD",
        },
    )
    assert first.status_code == second.status_code == 201
    issue = post(
        keeper,
        "/api/v1/issues/",
        {
            "material_id": material_id,
            "recipient_name": "Sardor (sex 2)",
            "allocations": [
                {"batch_id": first.data["id"], "quantity": "20"},
                {"batch_id": second.data["id"], "quantity": "5"},
            ],
        },
    )
    assert issue.status_code == 201, issue.data
    return {
        "material_id": material_id,
        "batches": (first.data["id"], second.data["id"]),
        "issue": issue.data,
    }


def assert_ledger_consistent(material_id: int, expected: Decimal) -> None:
    """Qoldiq = ochiq partiyalar yig'indisi = harakatlar yig'indisi."""
    balance = StockBalance.objects.get(material_id=material_id).quantity_on_hand
    remaining = Batch.objects.filter(material_id=material_id).aggregate(
        total=Sum("quantity_remaining")
    )["total"]
    moved = StockMovement.objects.filter(material_id=material_id).aggregate(
        total=Sum("quantity")
    )["total"]
    assert balance == remaining == moved == expected


def test_two_prices_issue_and_stock_stay_consistent(keeper, flow):
    material_id = flow["material_id"]
    first, second = flow["batches"]

    # Chiqim tannarxi har partiyaning o'z narxi bilan: 20 × 27 + 5 × 30.
    assert flow["issue"]["total_cost"] == "690.00"
    assert flow["issue"]["quantity_on_hand_after"] == "10.00"

    stock = keeper.get(f"/api/v1/stock/{material_id}/").data
    assert stock["quantity_on_hand"] == "10.00"
    assert stock["open_batches"] == 1
    assert stock["value_by_currency"] == [{"currency": "USD", "amount": "300.00"}]

    batches = keeper.get(f"/api/v1/stock/{material_id}/batches/").data["results"]
    assert [(b["id"], b["quantity_remaining"]) for b in batches] == [(second, "10.00")]

    movements = keeper.get("/api/v1/movements/", {"material": material_id}).data
    rows = list(reversed(movements["results"]))
    assert [(r["type"], r["quantity"], r["quantity_on_hand_after"]) for r in rows] == [
        ("receipt", "20.00", "20.00"),
        ("receipt", "15.00", "35.00"),
        ("issue", "-20.00", "15.00"),
        ("issue", "-5.00", "10.00"),
    ]
    assert [r["batch_id"] for r in rows] == [first, second, first, second]

    catalog = keeper.get(f"/api/v1/materials/{material_id}/").data
    assert catalog["quantity_on_hand"] == "10.00"
    assert_ledger_consistent(material_id, Decimal("10.00"))


def test_rejected_issue_changes_nothing(keeper, flow):
    material_id = flow["material_id"]
    _, second = flow["batches"]
    movements_before = StockMovement.objects.count()

    response = post(
        keeper,
        "/api/v1/issues/",
        {
            "material_id": material_id,
            "recipient_name": "Sardor (sex 2)",
            "allocations": [{"batch_id": second, "quantity": "11"}],
        },
    )

    assert response.status_code == 409
    assert response.data["code"] == "insufficient_stock"
    assert StockMovement.objects.count() == movements_before
    assert_ledger_consistent(material_id, Decimal("10.00"))


def test_server_hides_prices_on_every_warehouse_endpoint(flow):
    supervisor = client_with("supervisor", SUPERVISOR_CODES)
    material_id = flow["material_id"]
    receipt_id = flow["batches"][1]
    urls = [
        "/api/v1/receipts/",
        f"/api/v1/receipts/{receipt_id}/",
        "/api/v1/stock/",
        f"/api/v1/stock/{material_id}/",
        f"/api/v1/stock/{material_id}/batches/",
        "/api/v1/issues/",
        f"/api/v1/issues/{flow['issue']['id']}/",
        "/api/v1/movements/",
        f"/api/v1/materials/{material_id}/",
    ]

    for url in urls:
        response = supervisor.get(url)
        assert response.status_code == 200, url
        assert price_keys_in(response.data) == set(), url

    # Miqdorlar esa ko'rinadi.
    assert (
        supervisor.get(f"/api/v1/stock/{material_id}/").data["quantity_on_hand"]
        == "10.00"
    )


def test_return_and_write_off_keep_one_ledger(flow):
    """Qaytarish va hisobdan chiqarish (Akbar, PR #35) ham shu qoldiqni yuritadi."""
    material_id = flow["material_id"]
    _, second = flow["batches"]
    storekeeper = client_with(
        "returns_keeper",
        (
            "inventory.view_stock",
            "inventory.add_return",
            "inventory.approve_return",
            "inventory.add_write_off",
        ),
    )
    admin = client_with("warehouse_admin", ("*",))

    returned = post(
        storekeeper,
        "/api/v1/returns/",
        {
            "issue_id": flow["issue"]["id"],
            "reason": "Ortib qoldi",
            "allocations": [{"batch_id": second, "quantity": "2"}],
        },
    )
    assert returned.status_code == 201, returned.data
    # Tasdiqgacha qoldiq o'zgarmaydi (OQ-003).
    assert_ledger_consistent(material_id, Decimal("10.00"))
    approve = storekeeper.post(f"/api/v1/returns/{returned.data['id']}/approve/")
    assert approve.status_code == 200, approve.data
    assert_ledger_consistent(material_id, Decimal("12.00"))

    write_off = post(
        storekeeper,
        "/api/v1/write-offs/",
        {
            "material_id": material_id,
            "reason": "Namlikdan buzildi",
            "allocations": [{"batch_id": second, "quantity": "3"}],
        },
    )
    assert write_off.status_code == 201, write_off.data
    assert_ledger_consistent(material_id, Decimal("12.00"))
    decided = admin.post(f"/api/v1/write-offs/{write_off.data['id']}/approve/")
    assert decided.status_code == 200, decided.data
    assert_ledger_consistent(material_id, Decimal("9.00"))

    types = list(
        StockMovement.objects.filter(material_id=material_id)
        .order_by("id")
        .values_list("type", flat=True)
    )
    assert types == ["receipt", "receipt", "issue", "issue", "return", "write_off"]

    supervisor = client_with("supervisor", SUPERVISOR_CODES)
    for url in ("/api/v1/returns/", "/api/v1/write-offs/"):
        response = supervisor.get(url)
        assert response.status_code == 200, url
        assert response.data["count"] == 1, url
        assert price_keys_in(response.data) == set(), url
