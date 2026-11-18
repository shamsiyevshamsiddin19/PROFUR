"""Haqiqiy PostgreSQL bazasida parallel amallar va qator qulflash (select_for_update) sinovlari.

Ushbu modul SQLite yoki mock bilan ishlamaydi. U haqiqiy PostgreSQL ulanishlaridan
foydalanadi va parallel tranzaksiyalarning atomarligi, qoldiqning manfiyga tushmasligi,
lost update bo'lmasligi hamda Idempotency-Key himoyasini tekshiradi.
"""

import threading
import uuid
from datetime import date
from decimal import Decimal

import pytest
from accounts.models import Role
from apps.catalog.models import Category, Material, Unit
from apps.inventory import services
from apps.inventory.models import (
    Batch,
    Currency,
    MovementType,
    StockBalance,
    StockMovement,
)
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

# SQLite yoki mock qabul qilinmaydi:
pytestmark = [
    pytest.mark.django_db(transaction=True, serialized_rollback=True),
    pytest.mark.skipif(
        connection.vendor != "postgresql",
        reason="Parallel sinovlar faqat haqiqiy PostgreSQL bazasida ishlaydi (SQLite row-level lock qo'llab-quvvatlamaydi)",
    ),
]


def test_postgres_vendor_verification():
    """Haqiqiy PostgreSQL bazasiga ulanganligimizni tekshiradi."""
    assert connection.vendor == "postgresql", (
        "Test faqat PostgreSQL'da bajarilishi shart!"
    )


def test_concurrent_receipts_on_same_material_no_lost_updates():
    """Bir vaqtda 5 ta alohida ulanishdan bitta materialga kirim qilinishi (lost update bo'lmasligi)."""
    user = User.objects.create_user(
        username="pg_concurrency_user", password="password123"
    )
    category = Category.objects.create(name="Postgres Parallel Yog'och")
    material = Material.objects.create(
        category=category, name="Dub doska 50mm", unit=Unit.PIECE
    )

    num_threads = 5
    quantity_per_thread = Decimal("10.00")
    barrier = threading.Barrier(num_threads)
    errors: list[Exception] = []

    def worker(worker_id: int):
        connection.close()
        try:
            barrier.wait(timeout=10)
            services.receive(
                material=material,
                received_on=date(2026, 11, 18),
                quantity=quantity_per_thread,
                total_amount=Decimal("150.00"),
                user=user,
                currency=Currency.USD,
                document_number=f"DOC-CONCURRENT-{worker_id}",
            )
        except Exception as e:
            errors.append(e)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert not errors, f"Xatolar yuz berdi: {errors}"

    balance = StockBalance.objects.get(material=material)
    expected_total = quantity_per_thread * num_threads
    assert balance.quantity_on_hand == expected_total
    assert Batch.objects.filter(material=material).count() == num_threads
    assert (
        StockMovement.objects.filter(
            material=material, type=MovementType.RECEIPT
        ).count()
        == num_threads
    )


def test_concurrent_stock_decreases_never_go_negative():
    """Qoldiq 10 bo'lganda, ikki alohida ulanishdan 7 tadan chiqim so'ralsa faqat bittasi o'tadi."""
    user = User.objects.create_user(username="pg_issue_user", password="password123")
    category = Category.objects.create(name="Postgres Metall")
    material = Material.objects.create(
        category=category, name="Profil truba", unit=Unit.METER
    )

    batch, _ = services.receive(
        material=material,
        received_on=date(2026, 11, 18),
        quantity=Decimal("10.00"),
        total_amount=Decimal("200.00"),
        user=user,
        currency=Currency.USD,
    )
    role = Role.objects.create(
        code="PG_ISSUER", name="Chiqimchi", permissions=["inventory.add_issue"]
    )
    user.roles.add(role)
    barrier = threading.Barrier(2)
    results: list[int] = []
    errors: list[Exception] = []

    def issue_worker():
        connection.close()
        try:
            client = APIClient()
            client.force_authenticate(user=user)
            barrier.wait(timeout=10)
            response = client.post(
                "/api/v1/issues/",
                {
                    "material_id": material.pk,
                    "recipient_name": "Sardor",
                    "allocations": [{"batch_id": batch.pk, "quantity": "7.00"}],
                },
                format="json",
                HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
            )
            results.append(response.status_code)
        except Exception as error:
            errors.append(error)
        finally:
            connection.close()

    threads = [threading.Thread(target=issue_worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert all(not thread.is_alive() for thread in threads)
    assert not errors, errors
    assert sorted(results) == [201, 409]
    assert StockBalance.objects.get(material=material).quantity_on_hand == Decimal(
        "3.00"
    )
    batch.refresh_from_db()
    assert batch.quantity_remaining == Decimal("3.00")
    assert StockMovement.objects.get(
        material=material, type=MovementType.ISSUE
    ).quantity == Decimal("-7.00")


def test_transaction_rollback_leaves_no_traces_in_postgres():
    """Tranzaksiya ichida xato bo'lsa, PostgreSQL'da hech narsa saqlanmaydi (Rollback)."""
    user = User.objects.create_user(username="pg_rollback_user", password="password123")
    category = Category.objects.create(name="Postgres Rollback Category")
    material = Material.objects.create(
        category=category, name="Rollback Test Material", unit=Unit.PIECE
    )

    with pytest.raises(ValueError, match="rollback drill"):
        with transaction.atomic():
            services.receive(
                material=material,
                received_on=date(2026, 11, 18),
                quantity=Decimal("50.00"),
                total_amount=Decimal("500.00"),
                user=user,
            )
            raise ValueError("rollback drill")

    # Tekshiramiz: baza toza qolishi kerak
    balance = StockBalance.objects.filter(material=material).first()
    if balance:
        assert balance.quantity_on_hand == Decimal("0.00")
    assert Batch.objects.filter(material=material).count() == 0
    assert StockMovement.objects.filter(material=material).count() == 0


def test_concurrent_idempotency_key_replay_returns_same_batch():
    """Bir vaqtda bir xil Idempotency-Key bilan kelgan so'rovlar faqat bitta partiya yaratadi."""
    admin_role, _ = Role.objects.get_or_create(
        code="ADMIN", defaults={"name": "Admin", "permissions": ["*"]}
    )
    user = User.objects.create_user(
        username="pg_idempotent_user", password="password123"
    )
    user.roles.add(admin_role)

    category = Category.objects.create(name="Postgres Idempotent Category")
    material = Material.objects.create(
        category=category, name="Idempotent Material", unit=Unit.PIECE
    )

    idempotency_key = str(uuid.uuid4())
    body = {
        "material_id": material.id,
        "quantity": "25.00",
        "total_amount": "250.00",
        "currency": "USD",
        "received_on": "2026-11-18",
    }

    barrier = threading.Barrier(2)
    statuses: list[int] = []
    batch_ids: list[int] = []
    errors: list[Exception] = []

    def client_worker():
        connection.close()
        try:
            client = APIClient()
            client.force_authenticate(user=user)
            barrier.wait(timeout=10)
            res = client.post(
                "/api/v1/receipts/",
                data=body,
                format="json",
                HTTP_IDEMPOTENCY_KEY=idempotency_key,
            )
            statuses.append(res.status_code)
            if res.status_code in (200, 201):
                batch_ids.append(res.json()["id"])
        except Exception as error:
            errors.append(error)
        finally:
            connection.close()

    t1 = threading.Thread(target=client_worker)
    t2 = threading.Thread(target=client_worker)
    t1.start()
    t2.start()
    t1.join(timeout=30)
    t2.join(timeout=30)

    assert not t1.is_alive() and not t2.is_alive()
    assert not errors, errors
    assert sorted(statuses) == [status.HTTP_200_OK, status.HTTP_201_CREATED]
    assert len(batch_ids) == 2
    # Partiyalar faqat 1 ta yaratilgan bo'lishi shart!
    assert len(set(batch_ids)) == 1
    assert Batch.objects.filter(material=material).count() == 1
    assert StockBalance.objects.get(material=material).quantity_on_hand == Decimal(
        "25.00"
    )
