"""OQ-041: takroriy so'rov ham joriy narx ruxsatiga bo'ysunadi."""

import uuid
from decimal import Decimal

import pytest
from accounts.models import Role
from apps.catalog.models import Category, Material, Unit
from apps.inventory import services
from apps.inventory.models import IdempotencyKey, StockMovement
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db
PRICE_CODE = "inventory.view_purchase_price"


@pytest.mark.parametrize("endpoint", ["receipts", "issues", "returns", "write-offs"])
def test_replay_hides_prices_after_permission_is_revoked(endpoint):
    """Ruxsat bekor bo'lgach narx ochilmaydi, amal va saqlangan javob o'zgarmaydi."""
    user = get_user_model().objects.create_user(username="keeper")
    role = Role.objects.create(
        code="REPLAY_KEEPER",
        name="Ombor mas'uli",
        permissions=[
            "inventory.view_stock",
            "inventory.add_receipt",
            "inventory.add_issue",
            "inventory.add_return",
            "inventory.add_write_off",
            PRICE_CODE,
        ],
    )
    user.roles.add(role)
    client = APIClient()
    client.force_authenticate(user)
    material = Material.objects.create(
        category=Category.objects.get(name="LDSP"),
        name="Replay sinovi",
        color="oq",
        thickness_cm=Decimal("1.60"),
        unit=Unit.SHEET,
    )
    today = timezone.localdate()
    batch, _ = services.receive(
        material=material,
        received_on=today,
        quantity=Decimal("10"),
        total_amount=Decimal("100"),
        user=user,
    )
    allocations = [{"batch_id": batch.pk, "quantity": "1.00"}]
    bodies = {
        "receipts": {
            "material_id": material.pk,
            "received_on": today.isoformat(),
            "quantity": "2.00",
            "total_amount": "20.00",
            "currency": "USD",
        },
        "issues": {
            "material_id": material.pk,
            "recipient_name": "Sardor",
            "allocations": allocations,
        },
        "write-offs": {
            "material_id": material.pk,
            "reason": "Yaroqsiz",
            "allocations": allocations,
        },
    }
    if endpoint == "returns":
        issued, _ = services.issue_stock(
            material=material,
            allocations=[services.Allocation(batch.pk, Decimal("4"))],
            issued_on=today,
            recipient_name="Sardor",
            user=user,
        )
        bodies["returns"] = {"issue_id": issued.pk, "allocations": allocations}
    url = f"/api/v1/{endpoint}/"
    key = str(uuid.uuid4())

    def submit():
        return client.post(
            url, bodies[endpoint], format="json", HTTP_IDEMPOTENCY_KEY=key
        )

    first = submit()
    assert first.status_code == 201, first.data
    price_field = "total_amount" if endpoint == "receipts" else "total_cost"
    assert price_field in first.data
    movement_count = StockMovement.objects.count()
    role.permissions.remove(PRICE_CODE)
    role.save(update_fields=["permissions"])

    replay = submit()

    assert replay.status_code == 200, replay.data
    assert replay.data["id"] == first.data["id"]
    for field in ("total_amount", "unit_price", "total_cost", "currency"):
        assert field not in replay.data
    for part in replay.data.get("allocations", []):
        assert "unit_price" not in part
    assert StockMovement.objects.count() == movement_count
    cached = IdempotencyKey.objects.get(key=key, user=user)
    assert cached.response_body == first.data

    role.permissions.append(PRICE_CODE)
    role.save(update_fields=["permissions"])
    restored = submit()
    assert restored.status_code == 200
    assert restored.data == first.data
    assert StockMovement.objects.count() == movement_count
