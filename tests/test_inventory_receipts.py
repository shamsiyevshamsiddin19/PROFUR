"""PCRM-40: kirim, partiya, qoldiq va takror so'rov (shartnoma, 4- va 7-bo'lim)."""

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from accounts.models import Role
from apps.catalog.models import Category, Material, Unit
from apps.inventory import services
from apps.inventory.models import (
    Batch,
    IdempotencyKey,
    MovementType,
    StockBalance,
    StockMovement,
)
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

RECEIPTS = "/api/v1/receipts/"
STOREKEEPER_CODES = (
    "inventory.view_stock",
    "inventory.add_receipt",
    "inventory.view_purchase_price",
)


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
def storekeeper_user():
    return make_user("storekeeper", *STOREKEEPER_CODES)


@pytest.fixture
def storekeeper(storekeeper_user) -> APIClient:
    return client_for(storekeeper_user)


@pytest.fixture
def egger() -> Material:
    return Material.objects.create(
        category=Category.objects.get(name="LDSP"),
        name="LDSP Egger",
        color="oq",
        length_cm=Decimal("280.00"),
        width_cm=Decimal("207.00"),
        thickness_cm=Decimal("1.60"),
        unit=Unit.SHEET,
    )


def payload(material: Material, **overrides) -> dict:
    data = {
        "material_id": material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "20.00",
        "total_amount": "540.00",
        "currency": "USD",
        "supplier": "Egger Tashkent",
        "document_number": "NK-1182",
    }
    data.update(overrides)
    return data


def post(client: APIClient, data: dict, key: str | None = None):
    headers = {"Idempotency-Key": key or str(uuid.uuid4())}
    return client.post(RECEIPTS, data, format="json", headers=headers)


def on_hand(material: Material) -> Decimal:
    return StockBalance.objects.get(material=material).quantity_on_hand


def error_codes(response, field: str) -> list[str]:
    return [error.code for error in response.data[field]]


# --- Asosiy oqim ---------------------------------------------------------------


def test_receipt_creates_batch_movement_and_stock(storekeeper, storekeeper_user, egger):
    response = post(storekeeper, payload(egger))

    assert response.status_code == 201
    body = response.data
    assert body["material"] == {
        "id": egger.pk,
        "display_name": "LDSP Egger · oq · 280×207×1.6",
        "unit": "sheet",
    }
    assert body["quantity"] == body["quantity_remaining"] == "20.00"
    assert body["total_amount"] == "540.00"
    assert body["unit_price"] == "27.000000"
    assert body["currency"] == "USD"
    assert body["quantity_on_hand_after"] == "20.00"
    assert body["created_by"]["id"] == storekeeper_user.pk

    batch = Batch.objects.get(pk=body["id"])
    movement = StockMovement.objects.get(batch=batch)
    assert movement.type == MovementType.RECEIPT
    assert movement.quantity == Decimal("20.00")
    assert movement.quantity_on_hand_after == Decimal("20.00")
    assert (movement.reference_kind, movement.reference_id) == ("receipt", batch.pk)
    assert on_hand(egger) == Decimal("20.00")


def test_two_prices_stay_two_batches(storekeeper, egger):
    """Qabul mezoni: bir material ikki xil narxda — ikki alohida partiya."""
    first = post(storekeeper, payload(egger, quantity="20", total_amount="540"))
    second = post(storekeeper, payload(egger, quantity="15", total_amount="450"))

    assert first.status_code == second.status_code == 201
    prices = sorted(Batch.objects.values_list("unit_price", flat=True))
    assert prices == [Decimal("27.000000"), Decimal("30.000000")]
    assert on_hand(egger) == Decimal("35.00")
    assert second.data["quantity_on_hand_after"] == "35.00"
    assert StockMovement.objects.filter(material=egger).count() == 2


def test_total_amount_is_kept_exactly(storekeeper, egger):
    response = post(storekeeper, payload(egger, quantity="3", total_amount="100"))

    assert response.data["total_amount"] == "100.00"
    assert response.data["unit_price"] == "33.333333"


# --- Takror so'rov (Idempotency-Key) -------------------------------------------


def test_same_key_and_body_returns_first_response(storekeeper, egger):
    key = str(uuid.uuid4())
    first = post(storekeeper, payload(egger), key)
    second = post(storekeeper, payload(egger), key)

    assert (first.status_code, second.status_code) == (201, 200)
    assert second.data == first.data
    assert Batch.objects.count() == 1
    assert on_hand(egger) == Decimal("20.00")


def test_same_key_with_other_body_is_conflict(storekeeper, egger):
    key = str(uuid.uuid4())
    post(storekeeper, payload(egger), key)

    response = post(storekeeper, payload(egger, quantity="21.00"), key)

    assert response.status_code == 409
    assert response.data["detail"].code == "idempotency_conflict"
    assert response.data["code"] == "idempotency_conflict"
    assert Batch.objects.count() == 1


def test_key_is_per_user(storekeeper, egger):
    key = str(uuid.uuid4())
    other = client_for(make_user("other", *STOREKEEPER_CODES))

    assert post(storekeeper, payload(egger), key).status_code == 201
    assert post(other, payload(egger), key).status_code == 201
    assert Batch.objects.count() == 2


def test_expired_key_can_be_reused(storekeeper, egger):
    key = str(uuid.uuid4())
    post(storekeeper, payload(egger), key)
    IdempotencyKey.objects.update(created_at=timezone.now() - timedelta(hours=25))

    assert post(storekeeper, payload(egger), key).status_code == 201
    assert Batch.objects.count() == 2


@pytest.mark.parametrize("key", [None, "", "not-a-uuid"])
def test_missing_or_bad_key_is_rejected(storekeeper, egger, key):
    headers = {} if key is None else {"Idempotency-Key": key}
    response = storekeeper.post(
        RECEIPTS, payload(egger), format="json", headers=headers
    )

    assert response.status_code == 400
    assert error_codes(response, "idempotency_key") == ["idempotency_key_required"]
    assert not Batch.objects.exists()


# --- Tekshiruvlar ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("quantity", "0", "min_value"),
        ("quantity", "1.234", "max_decimal_places"),
        ("total_amount", "-1", "min_value"),
        ("currency", "EUR", "invalid_choice"),
        ("currency", "UZS", "invalid_choice"),
        ("material_id", 999999, "does_not_exist"),
    ],
)
def test_invalid_fields(storekeeper, egger, field, value, code):
    response = post(storekeeper, payload(egger, **{field: value}))

    assert response.status_code == 400
    assert error_codes(response, field) == [code]
    assert not Batch.objects.exists()
    assert not IdempotencyKey.objects.exists()


def test_future_date_is_rejected(storekeeper, egger):
    tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()

    response = post(storekeeper, payload(egger, received_on=tomorrow))

    assert response.status_code == 400
    assert error_codes(response, "received_on") == ["date_in_future"]


def test_inactive_material_is_rejected(storekeeper, egger):
    Material.objects.filter(pk=egger.pk).update(is_active=False)

    response = post(storekeeper, payload(egger))

    assert response.status_code == 400
    assert error_codes(response, "material_id") == ["material_inactive"]


def test_failure_inside_transaction_saves_nothing(storekeeper, egger, monkeypatch):
    """Harakat yozilmasa, partiya ham, qoldiq ham saqlanmaydi."""

    def broken_create(*args, **kwargs):
        raise RuntimeError("harakat yozilmadi")

    monkeypatch.setattr(StockMovement.objects, "create", broken_create)
    storekeeper.raise_request_exception = False

    response = post(storekeeper, payload(egger))

    assert response.status_code == 500
    assert not Batch.objects.exists()
    assert not IdempotencyKey.objects.exists()
    assert not StockBalance.objects.filter(quantity_on_hand__gt=0).exists()


# --- Ruxsatlar ------------------------------------------------------------------


def test_anonymous_is_rejected(egger):
    response = post(APIClient(), payload(egger))

    assert response.status_code == 403
    assert response.data["detail"].code == "not_authenticated"


def test_without_add_receipt_permission(egger):
    viewer = client_for(make_user("viewer", "inventory.view_stock"))

    assert post(viewer, payload(egger)).status_code == 403
    assert viewer.get(RECEIPTS).status_code == 200


def test_prices_hidden_without_price_permission(storekeeper, egger):
    created = post(storekeeper, payload(egger))
    supervisor = client_for(make_user("supervisor", "inventory.view_stock"))

    response = supervisor.get(f"{RECEIPTS}{created.data['id']}/")

    assert response.status_code == 200
    for field in ("total_amount", "unit_price", "currency"):
        assert field not in response.data
    assert response.data["quantity"] == "20.00"


def test_put_patch_delete_are_not_allowed(storekeeper, egger):
    created = post(storekeeper, payload(egger))
    url = f"{RECEIPTS}{created.data['id']}/"

    assert storekeeper.put(url, {}).status_code == 405
    assert storekeeper.patch(url, {}).status_code == 405
    assert storekeeper.delete(url).status_code == 405


# --- Ro'yxat --------------------------------------------------------------------


def test_list_filters_and_newest_first(storekeeper, egger):
    pva = Material.objects.create(
        category=Category.objects.get(name="Furnitura"), name="PVA", unit=Unit.KG
    )
    today = timezone.localdate()
    old = post(storekeeper, payload(egger, received_on=str(today - timedelta(days=5))))
    new = post(storekeeper, payload(egger))
    post(storekeeper, payload(pva, quantity="5", total_amount="10"))

    def ids(**params):
        response = storekeeper.get(RECEIPTS, params)
        assert response.status_code == 200
        return [item["id"] for item in response.data["results"]]

    assert ids(material=egger.pk) == [new.data["id"], old.data["id"]]
    assert ids(material=egger.pk, date_to=str(today - timedelta(days=1))) == [
        old.data["id"]
    ]
    assert len(ids(date_from=str(today))) == 2
    assert "quantity_on_hand_after" not in storekeeper.get(RECEIPTS).data["results"][0]
    assert storekeeper.get(RECEIPTS, {"date_from": "18.11.2026"}).status_code == 400


# --- Xizmat funksiyasi ----------------------------------------------------------


def test_receive_service_directly(storekeeper_user, egger):
    egger.unit = "kg"
    egger.save(update_fields=["unit"])
    batch, balance = services.receive(
        material=egger,
        received_on=timezone.localdate(),
        quantity=Decimal("2.50"),
        total_amount=Decimal("10.00"),
        user=storekeeper_user,
    )

    assert batch.unit_price == Decimal("4.000000")
    assert batch.currency == "USD"
    assert balance.quantity_on_hand == Decimal("2.50")


# --- Katalog bilan bog'liqlik --------------------------------------------------


def test_catalog_shows_quantity_on_hand_after_receipt(storekeeper, egger):
    catalog = client_for(
        make_user("catalog_viewer", "catalog.view_material", "inventory.view_stock")
    )
    url = f"/api/v1/materials/{egger.pk}/"
    assert catalog.get(url).data["quantity_on_hand"] == "0.00"

    post(storekeeper, payload(egger, quantity="20"))
    post(storekeeper, payload(egger, quantity="15", total_amount="450"))

    assert catalog.get(url).data["quantity_on_hand"] == "35.00"


def test_material_with_receipts_keeps_unit_and_dimensions(storekeeper, egger):
    post(storekeeper, payload(egger))
    editor = client_for(
        make_user("editor", "catalog.view_material", "catalog.change_material")
    )
    url = f"/api/v1/materials/{egger.pk}/"

    for change in ({"unit": "piece"}, {"thickness_cm": "1.80"}):
        response = editor.patch(url, change, format="json")
        assert response.status_code == 409
        assert response.data["detail"].code == "material_has_history"
        assert response.data["code"] == "material_has_history"

    assert editor.patch(url, {"name": "LDSP Egger W980"}).status_code == 200
    assert editor.patch(url, {"unit": "sheet"}).status_code == 200  # o'zgarmagan
    egger.refresh_from_db()
    assert (egger.unit, egger.thickness_cm) == ("sheet", Decimal("1.60"))


def test_material_without_receipts_can_change_unit(egger):
    editor = client_for(
        make_user("editor", "catalog.view_material", "catalog.change_material")
    )

    response = editor.patch(f"/api/v1/materials/{egger.pk}/", {"unit": "piece"})

    assert response.status_code == 200
