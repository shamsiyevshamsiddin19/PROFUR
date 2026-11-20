"""Acceptance checks for the warehouse workflow from the client conversation."""

import uuid
from decimal import Decimal

import pytest
from accounts.models import Role, User
from apps.catalog.models import Category, Material
from apps.inventory.models import Batch, LeftoverOffcut, StockBalance, WarehouseReview
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def signed_in(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def post(client, path, data, key=None):
    return client.post(
        path, data, format="json", HTTP_IDEMPOTENCY_KEY=str(key or uuid.uuid4())
    )


@pytest.fixture
def warehouse():
    admin = User.objects.create_superuser(username="admin", password="safe-password-42")
    role = Role.objects.create(
        code="SAWYER",
        name="Arrachi",
        permissions=[
            "inventory.worker",
            "inventory.view_stock",
            "inventory.add_issue",
            "catalog.view_material",
            "inventory.view_offcut",
            "inventory.add_offcut",
            "inventory.use_offcut",
            "inventory.add_return",
        ],
    )
    worker = User.objects.create_user(username="worker")
    worker.roles.add(role)
    category = Category.objects.get(name="PVC")
    sheet = Material.objects.create(
        category=category,
        name="Test PVC",
        length_cm=200,
        width_cm=100,
        unit="sheet",
        allowed_roles=[role.code],
    )
    hidden = Material.objects.create(
        category=category,
        name="Hidden PVC",
        unit="sheet",
        allowed_roles=["OTHER"],
    )
    return signed_in(admin), signed_in(worker), role, sheet, hidden


def receive(admin, sheet, quantity, **price):
    response = post(
        admin,
        "/api/v1/receipts/",
        {
            "material_id": sheet.pk,
            "quantity": str(quantity),
            "currency": "USD",
            "received_on": timezone.localdate().isoformat(),
            **price,
        },
    )
    assert response.status_code == 201, response.data
    return response.data


def test_worker_actions_apply_once_and_admin_review_never_changes_whole_stock(
    warehouse,
):
    admin, worker, _, sheet, hidden = warehouse
    old = receive(admin, sheet, 1, total_amount="25.00")
    new = receive(admin, sheet, 2, unit_price="28")
    assert new["total_amount"] == "56.00"
    assert new["unit_price"] == "28.000000"

    assert worker.get(f"/api/v1/materials/{hidden.pk}/").status_code == 404
    assert worker.get(f"/api/v1/stock/{hidden.pk}/").status_code == 404
    assert (
        post(
            worker,
            "/api/v1/issues/",
            {
                "material_id": hidden.pk,
                "quantity": "1",
                "project_id": 12,
            },
        ).status_code
        == 400
    )
    body = {"material_id": sheet.pk, "quantity": "2", "project_id": 12}
    key = uuid.uuid4()
    result = post(worker, "/api/v1/issues/", body, key)
    assert result.status_code == 201, result.data
    assert post(worker, "/api/v1/issues/", body, key).status_code == 200
    assert result.data["recipient_name"] == "worker"
    assert result.data["project_id"] == 12
    assert "total_cost" not in result.data
    assert [row["batch_id"] for row in result.data["allocations"]] == [
        old["id"],
        new["id"],
    ]
    assert StockBalance.objects.get(material=sheet).quantity_on_hand == 1
    assert WarehouseReview.objects.count() == 1
    assert worker.get("/api/v1/warehouse-reviews/").status_code == 403

    issue_id = result.data["id"]
    piece = {"issue_id": issue_id, "length_mm": "600", "width_mm": "400", "quantity": 1}
    key = uuid.uuid4()
    result = post(worker, "/api/v1/offcuts/", piece, key)
    assert result.status_code == 201, result.data
    assert post(worker, "/api/v1/offcuts/", piece, key).status_code == 200
    offcut = result.data["id"]
    queue = admin.get("/api/v1/warehouse-reviews/?pending=true").data
    assert queue["count"] == 2
    add = next(row for row in queue["results"] if row["kind"] == "offcut_add")
    assert add["actor"]["name"] == "worker"
    assert add["issue"] == issue_id
    assert StockBalance.objects.get(material=sheet).quantity_on_hand == 1

    take = post(worker, f"/api/v1/offcuts/{offcut}/withdraw/", {"quantity": 1})
    assert take.status_code == 201, take.data
    assert LeftoverOffcut.objects.get(pk=offcut).quantity == 0
    assert worker.get("/api/v1/offcuts/").data["count"] == 0
    use_row = WarehouseReview.objects.get(kind="offcut_use")
    assert (
        admin.post(
            f"/api/v1/warehouse-reviews/{use_row.id}/decide/",
            {
                "state": "flagged",
                "note": "Xato miqdor",
            },
        ).status_code
        == 200
    )
    assert (
        admin.post(
            f"/api/v1/warehouse-reviews/{use_row.id}/correct/",
            {
                "note": "Bo‘lak qayta sanaldi",
            },
        ).status_code
        == 200
    )
    assert (
        admin.post(
            f"/api/v1/warehouse-reviews/{use_row.id}/correct/",
            {
                "note": "Bu takror so‘rov",
            },
        ).status_code
        == 200
    )
    assert WarehouseReview.objects.filter(correction_of=use_row).count() == 1
    assert LeftoverOffcut.objects.get(pk=offcut).quantity == 1
    assert StockBalance.objects.get(material=sheet).quantity_on_hand == 1

    blocked = post(
        worker,
        "/api/v1/returns/",
        {
            "issue_id": issue_id,
            "allocations": [
                {"batch_id": old["id"], "quantity": "1"},
                {"batch_id": new["id"], "quantity": "1"},
            ],
        },
    )
    assert blocked.status_code == 409
    restored = post(
        worker,
        "/api/v1/returns/",
        {
            "issue_id": issue_id,
            "allocations": [{"batch_id": old["id"], "quantity": "1"}],
        },
    )
    assert restored.status_code == 201
    assert (
        admin.post(f"/api/v1/returns/{restored.data['id']}/approve/", {}).status_code
        == 200
    )

    report = admin.get("/api/v1/dashboard/").data
    assert report["totals"]["received"] == "81.00"
    assert report["totals"]["issued"] == "53.00"
    assert report["totals"]["returned"] == "25.00"
    assert report["totals"]["net_issued"] == "28.00"
    assert report["rows"][0]["material"]["id"] == sheet.pk
    assert worker.get("/api/v1/dashboard/").status_code == 403
    assert StockBalance.objects.get(material=sheet).quantity_on_hand == Decimal("2")


def test_role_request_does_not_assign_role_until_admin_verifies(warehouse):
    admin, _, role, *_ = warehouse
    public = APIClient()
    assert public.get("/api/auth/signup-roles/").data == [
        {"code": role.code, "name": role.name}
    ]
    payload = {
        "username": "new_sawyer",
        "password": "test-worker-pass-42",
        "requested_roles": [role.code],
    }
    assert (
        public.post(
            "/api/auth/register/",
            {**payload, "requested_roles": ["ADMIN"]},
            format="json",
        ).status_code
        == 400
    )
    result = public.post("/api/auth/register/", payload, format="json")
    assert result.status_code == 201, result.data
    new = User.objects.get(username=payload["username"])
    assert not new.is_approved
    assert not new.roles.exists()
    assert admin.get("/api/auth/pending/").data[0]["requested_roles"] == [role.code]
    result = admin.post(
        f"/api/auth/users/{new.pk}/approve/", {"role_ids": [role.pk]}, format="json"
    )
    assert result.status_code == 200, result.data
    new.refresh_from_db()
    assert new.is_approved and new.has_role(role.code)


def test_impossible_unit_price_total_does_not_create_a_batch(warehouse):
    admin, _, _, sheet, _ = warehouse
    response = post(
        admin,
        "/api/v1/receipts/",
        {
            "material_id": sheet.pk,
            "quantity": "1",
            "unit_price": "0.000001",
            "currency": "USD",
            "received_on": timezone.localdate().isoformat(),
        },
    )
    assert response.status_code == 400, response.data
    assert not Batch.objects.exists()


def test_opening_balance_increases_stock_without_inflating_monthly_purchases(warehouse):
    admin, worker, _, sheet, _ = warehouse
    opening = receive(admin, sheet, 20, total_amount="500.00", is_opening=True)
    assert opening["is_opening"] is True
    receive(admin, sheet, 30, unit_price="28.00")
    report = admin.get("/api/v1/dashboard/").data
    assert report["totals"]["received"] == "840.00"
    assert report["totals"]["warehouse_value"] == "1340.00"
    assert report["rows"][0]["received"] == "30.00"
    assert worker.get(f"/api/v1/stock/{sheet.pk}/").data["quantity_on_hand"] == "50.00"
    late = post(
        admin,
        "/api/v1/receipts/",
        {
            "material_id": sheet.pk,
            "quantity": "1",
            "total_amount": "25",
            "currency": "USD",
            "received_on": timezone.localdate().isoformat(),
            "is_opening": True,
        },
    )
    assert late.status_code == 400
    assert Batch.objects.filter(material=sheet).count() == 2


def test_same_paint_can_have_two_independently_named_bucket_sizes(warehouse):
    admin, *_ = warehouse
    category = Category.objects.create(name="Sinov bo‘yoqlari")
    for capacity in ("12", "25"):
        response = admin.post(
            "/api/v1/materials/",
            {
                "name": "White paint",
                "category_id": category.pk,
                "unit": "piece",
                "container_size": capacity,
            },
        )
        assert response.status_code == 201, response.data
        assert response.data["display_name"] == f"White paint · {capacity} L"
