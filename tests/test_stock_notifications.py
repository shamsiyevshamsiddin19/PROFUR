"""PCRM-7/50: tranzaksiya, chegaradan o'tish va shaxsiy xabar ruxsatlari."""

from decimal import Decimal

import pytest
from accounts.models import Role, User
from apps.catalog.models import Category, Material
from apps.inventory import services
from apps.inventory.models import StockBalance, StockNotification
from django.db import transaction
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup():
    role = Role.objects.create(
        code="NOTICE_KEEPER", name="Keeper", permissions=["inventory.view_stock"]
    )
    keeper = User.objects.create_user(username="notified_keeper")
    keeper.roles.add(role)
    admin = User.objects.create_superuser(username="notified_admin", password="test")
    outsider = User.objects.create_user(username="no_stock_access")
    inactive = User.objects.create_user(username="inactive_keeper", is_active=False)
    inactive.roles.add(role)
    material = Material.objects.create(
        name="Notify MDF", category=Category.objects.get(name="LMDF"), unit="sheet"
    )
    return material, keeper, admin, outsider, role


def test_crossing_sends_once_to_active_authorized_recipients(setup):
    material, keeper, admin, outsider, _ = setup
    services.set_min_quantity(material, Decimal("10"))
    assert set(StockNotification.objects.values_list("recipient_id", flat=True)) == {
        keeper.pk,
        admin.pk,
    }
    services.set_min_quantity(material, Decimal("12"))
    assert StockNotification.objects.count() == 2
    services.receive(
        material=material,
        user=admin,
        received_on=timezone.localdate(),
        quantity=Decimal("15"),
        total_amount=Decimal("150"),
    )
    assert StockNotification.objects.count() == 2
    services.set_min_quantity(material, Decimal("20"))
    assert StockNotification.objects.count() == 4
    latest = StockNotification.objects.first()
    assert latest.quantity == Decimal("15") and latest.minimum == Decimal("20")
    services.set_min_quantity(material, None)
    assert StockBalance.objects.get(material=material).low_stock_notified is False


def test_notification_rollback_follows_stock_transaction(setup):
    material, *_ = setup
    with pytest.raises(ValueError), transaction.atomic():
        services.set_min_quantity(material, Decimal("1"))
        raise ValueError("Rollback")
    assert not StockNotification.objects.exists()
    assert not StockBalance.objects.filter(material=material).exists()


def test_inbox_is_private_and_revocation_blocks_both_actions(setup):
    material, keeper, admin, outsider, role = setup
    services.set_min_quantity(material, Decimal("10"))
    client = APIClient()
    client.force_authenticate(keeper)
    own = StockNotification.objects.get(recipient=keeper)
    other = StockNotification.objects.get(recipient=admin)
    response = client.get("/api/v1/notifications/?unread=true")
    assert response.status_code == 200
    assert [row["id"] for row in response.data["results"]] == [own.pk]
    assert response.data["results"][0]["material_name"] == str(material)
    assert client.post(f"/api/v1/notifications/{other.pk}/read/").status_code == 404
    assert client.post(f"/api/v1/notifications/{own.pk}/read/").status_code == 200
    own.refresh_from_db()
    original_read = own.read_at
    assert client.post(f"/api/v1/notifications/{own.pk}/read/").status_code == 200
    own.refresh_from_db()
    assert own.read_at == original_read
    assert client.get("/api/v1/notifications/?unread=true").data["count"] == 0
    role.permissions = []
    role.save()
    assert client.get("/api/v1/notifications/").status_code == 403
    assert client.post(f"/api/v1/notifications/{own.pk}/read/").status_code == 403


def test_actual_issue_below_minimum_and_recovery_rearm_notifications(setup):
    material, keeper, admin, *_ = setup
    batch, _ = services.receive(
        material=material,
        user=admin,
        received_on=timezone.localdate(),
        quantity=Decimal("20"),
        total_amount=Decimal("600"),
    )
    services.set_min_quantity(material, Decimal("15"))
    assert not StockNotification.objects.exists()
    services.issue_stock(
        material=material,
        allocations=[services.Allocation(batch.pk, Decimal("7"))],
        issued_on=timezone.localdate(),
        recipient_name="Worker",
        user=admin,
    )
    assert StockNotification.objects.filter(recipient=keeper).get().quantity == Decimal(
        "13"
    )
    # Still below: no duplicate alert on another issue.
    services.issue_stock(
        material=material,
        allocations=[services.Allocation(batch.pk, Decimal("1"))],
        issued_on=timezone.localdate(),
        recipient_name="Worker",
        user=admin,
    )
    assert StockNotification.objects.count() == 2
    services.receive(
        material=material,
        user=admin,
        received_on=timezone.localdate(),
        quantity=Decimal("10"),
        total_amount=Decimal("300"),
    )
    services.issue_stock(
        material=material,
        allocations=[services.Allocation(batch.pk, Decimal("8"))],
        issued_on=timezone.localdate(),
        recipient_name="Worker",
        user=admin,
    )
    assert StockNotification.objects.count() == 4
