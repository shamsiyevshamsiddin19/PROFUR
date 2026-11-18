"""PCRM-44, 1-qism: ombordan chiqim API'si (``/api/v1/issues/``).

Tekshiriladi: qoldiq va partiya kamayishi, tannarx (USD), 409 xatolari,
idempotentlik, ruxsatlar, narxni yashirish, filtrlar, uz/ru/en xabarlari va
PostgreSQL'da parallel chiqim (10 dan 7 + 7).
"""

import threading
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
    StockIssue,
    StockMovement,
)
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

ISSUES = "/api/v1/issues/"
VIEW = "inventory.view_stock"
ADD = "inventory.add_issue"
PRICES = "inventory.view_purchase_price"

postgres_only = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="Qatorni qulflash (select_for_update) faqat PostgreSQL'da sinaladi",
)


def make_user(username: str, *codes: str):
    """Foydalanuvchi yaratadi va unga berilgan ruxsat kodlari bilan rol biriktiradi."""
    user = get_user_model().objects.create_user(username=username, password="x")
    if codes:
        role = Role.objects.create(
            code=f"TEST_{username.upper()}", name=username, permissions=list(codes)
        )
        user.roles.add(role)
    return user


def client_for(user) -> APIClient:
    """Shu foydalanuvchi nomidan so'rov yuboradigan mijoz."""
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def keeper_user():
    """Ombor mas'uli: chiqim qiladi, qoldiq va narxni ko'radi."""
    return make_user("keeper", VIEW, ADD, PRICES)


@pytest.fixture
def keeper(keeper_user) -> APIClient:
    """Ombor mas'uli nomidan so'rov yuboradigan mijoz."""
    return client_for(keeper_user)


@pytest.fixture
def supervisor() -> APIClient:
    """Nazoratchi: chiqimlarni ko'radi, lekin narxni ko'rmaydi va chiqim qilmaydi."""
    return client_for(make_user("supervisor", VIEW))


@pytest.fixture
def egger() -> Material:
    """Sinov materiali (list birligida)."""
    return Material.objects.create(
        category=Category.objects.get(name="LDSP"),
        name="LDSP Egger",
        color="oq",
        thickness_cm=Decimal("1.60"),
        unit=Unit.SHEET,
    )


@pytest.fixture
def glue() -> Material:
    """Ikkinchi material: boshqa materialning partiyasini tekshirish uchun."""
    return Material.objects.create(
        category=Category.objects.get(name="Furnitura"), name="PVA", unit=Unit.KG
    )


def receive(material, user, quantity: str, total: str, days_ago: int = 0) -> Batch:
    """Servis orqali kirim qiladi va yangi partiyani qaytaradi."""
    batch, _ = services.receive(
        material=material,
        received_on=timezone.localdate() - timedelta(days=days_ago),
        quantity=Decimal(quantity),
        total_amount=Decimal(total),
        user=user,
    )
    return batch


def issue_body(material, *parts: tuple[Batch, str], **extra) -> dict:
    """Chiqim so'rovi tanasini tuzadi: ``(partiya, miqdor)`` juftliklaridan."""
    return {
        "material_id": material.pk,
        "recipient_name": "Sardor (sex 2)",
        "allocations": [
            {"batch_id": batch.pk, "quantity": quantity} for batch, quantity in parts
        ],
        **extra,
    }


def post_issue(client: APIClient, body: dict, key: uuid.UUID | None = None, **headers):
    """Chiqimni ``Idempotency-Key`` bilan yuboradi (kalit berilmasa yangisi)."""
    return client.post(
        ISSUES,
        body,
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(key or uuid.uuid4()),
        **headers,
    )


def on_hand(material) -> Decimal:
    """Materialning joriy umumiy qoldig'i."""
    return StockBalance.objects.get(material=material).quantity_on_hand


def test_issue_decreases_balance_batch_and_writes_movement(keeper, keeper_user, egger):
    """Chiqim qoldiqni va partiyani kamaytiradi, manfiy ``issue`` harakati yozadi."""
    batch = receive(egger, keeper_user, "10", "250.00")

    response = post_issue(keeper, issue_body(egger, (batch, "4"), project_id=7))

    assert response.status_code == 201, response.data
    data = response.data
    assert data["quantity"] == "4.00"
    assert data["quantity_on_hand_after"] == "6.00"
    assert data["project_id"] == 7
    assert data["recipient_name"] == "Sardor (sex 2)"
    assert data["total_cost"] == "100.00"
    assert data["currency"] == "USD"
    assert data["allocations"] == [
        {
            "batch_id": batch.pk,
            "received_on": batch.received_on.isoformat(),
            "quantity": "4.00",
            "unit_price": "25.000000",
        }
    ]
    assert on_hand(egger) == Decimal("6")
    batch.refresh_from_db()
    assert batch.quantity_remaining == Decimal("6")
    movement = StockMovement.objects.get(type=MovementType.ISSUE)
    assert movement.quantity == Decimal("-4")
    assert movement.quantity_on_hand_after == Decimal("6")
    assert (movement.reference_kind, movement.reference_id) == ("issue", data["id"])


def test_issue_split_across_batches_costs_each_batch_price(keeper, keeper_user, egger):
    """Ikki partiyadan olingan chiqim har partiyaning o'z narxida hisoblanadi."""
    old = receive(egger, keeper_user, "5", "100.00", days_ago=3)  # 20.00 $
    new = receive(egger, keeper_user, "5", "150.00")  # 30.00 $

    response = post_issue(keeper, issue_body(egger, (old, "5"), (new, "2")))

    assert response.status_code == 201, response.data
    assert response.data["quantity"] == "7.00"
    assert response.data["total_cost"] == "160.00"  # 5 × 20 + 2 × 30
    assert response.data["quantity_on_hand_after"] == "3.00"
    after = list(
        StockMovement.objects.filter(type=MovementType.ISSUE)
        .order_by("id")
        .values_list("quantity", "quantity_on_hand_after")
    )
    assert after == [(Decimal("-5"), Decimal("5")), (Decimal("-2"), Decimal("3"))]


def test_total_cost_rounds_half_up_to_cents(keeper, keeper_user, egger):
    """Tannarx faqat oxirida sentgacha ``ROUND_HALF_UP`` bilan yaxlitlanadi."""
    batch = receive(egger, keeper_user, "3", "100.00")  # 33.333333 $

    response = post_issue(keeper, issue_body(egger, (batch, "1.5")))

    assert response.data["total_cost"] == "50.00"  # 1.5 × 33.333333 = 49.9999995


def test_insufficient_stock_returns_409_and_saves_nothing(keeper, keeper_user, egger):
    """Qoldiqdan ko'p chiqim 409 ``insufficient_stock``; hech narsa saqlanmaydi."""
    batch = receive(egger, keeper_user, "3", "30.00")

    response = post_issue(keeper, issue_body(egger, (batch, "5")))

    assert response.status_code == 409
    assert response.data["code"] == "insufficient_stock"
    assert response.data["available"] == "3.00"
    assert response.data["requested"] == "5.00"
    assert not StockIssue.objects.exists()
    assert not IdempotencyKey.objects.exists()
    assert on_hand(egger) == Decimal("3")


def test_batch_short_returns_409_batch_insufficient(keeper, keeper_user, egger):
    """Umumiy qoldiq yetsa ham tanlangan partiyada yetmasa 409 ``batch_insufficient``."""
    small = receive(egger, keeper_user, "2", "20.00", days_ago=1)
    receive(egger, keeper_user, "8", "80.00")

    response = post_issue(keeper, issue_body(egger, (small, "3")))

    assert response.status_code == 409
    assert response.data["code"] == "batch_insufficient"
    assert response.data["batch_id"] == str(small.pk)
    assert response.data["available"] == "2.00"
    assert not StockIssue.objects.exists()
    assert on_hand(egger) == Decimal("10")


def test_rejects_duplicate_and_foreign_batches(keeper, keeper_user, egger, glue):
    """Takroriy partiya va boshqa materialning partiyasi 400 qaytaradi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    other = receive(glue, keeper_user, "10", "50.00")

    duplicate = post_issue(keeper, issue_body(egger, (batch, "1"), (batch, "1")))
    foreign = post_issue(keeper, issue_body(egger, (other, "1")))

    assert duplicate.status_code == 400
    assert duplicate.data["allocations"][0].code == "duplicate_batch"
    assert foreign.status_code == 400
    assert foreign.data["allocations"][0].code == "batch_not_of_material"
    assert str(other.pk) in str(foreign.data["allocations"][0])


@pytest.mark.parametrize(
    ("extra", "field"),
    [
        ({"issued_on": "2999-01-01"}, "issued_on"),
        ({"project_id": 0}, "project_id"),
        ({"recipient_name": ""}, "recipient_name"),
        ({"allocations": []}, "allocations"),
    ],
)
def test_validation_errors(keeper, keeper_user, egger, extra, field):
    """Kelajak sana, noto'g'ri loyiha, bo'sh oluvchi va bo'sh qismlar — 400."""
    batch = receive(egger, keeper_user, "10", "100.00")

    response = post_issue(keeper, issue_body(egger, (batch, "1"), **extra))

    assert response.status_code == 400
    assert field in response.data


def test_zero_quantity_part_is_rejected(keeper, keeper_user, egger):
    """Qism miqdori 0 bo'lishi mumkin emas."""
    batch = receive(egger, keeper_user, "10", "100.00")

    response = post_issue(keeper, issue_body(egger, (batch, "0")))

    assert response.status_code == 400
    assert "allocations" in response.data


def test_idempotency_key_is_required(keeper, keeper_user, egger):
    """``Idempotency-Key`` sarlavhasisiz chiqim 400 bilan rad etiladi."""
    batch = receive(egger, keeper_user, "10", "100.00")

    response = keeper.post(ISSUES, issue_body(egger, (batch, "1")), format="json")

    assert response.status_code == 400
    assert response.data["idempotency_key"][0].code == "idempotency_key_required"


def test_replayed_request_writes_one_issue(keeper, keeper_user, egger):
    """Bir xil kalit va tana: bitta chiqim, ikkinchi javob 200 va aynan o'sha tana."""
    batch = receive(egger, keeper_user, "10", "100.00")
    key = uuid.uuid4()
    body = issue_body(egger, (batch, "4"))

    first = post_issue(keeper, body, key)
    second = post_issue(keeper, body, key)

    assert (first.status_code, second.status_code) == (201, 200)
    assert second.data == first.data
    assert StockIssue.objects.count() == 1
    assert StockMovement.objects.filter(type=MovementType.ISSUE).count() == 1
    assert on_hand(egger) == Decimal("6")


def test_same_key_with_other_body_is_409(keeper, keeper_user, egger):
    """Bir xil kalit, boshqa tana — 409 ``idempotency_conflict``."""
    batch = receive(egger, keeper_user, "10", "100.00")
    key = uuid.uuid4()

    post_issue(keeper, issue_body(egger, (batch, "4")), key)
    response = post_issue(keeper, issue_body(egger, (batch, "5")), key)

    assert response.status_code == 409
    assert response.data["detail"].code == "idempotency_conflict"
    assert on_hand(egger) == Decimal("6")


def test_failed_issue_does_not_burn_the_key(keeper, keeper_user, egger):
    """409 dan keyin xuddi shu kalit bilan to'g'rilangan so'rov o'tadi."""
    batch = receive(egger, keeper_user, "3", "30.00")
    key = uuid.uuid4()

    failed = post_issue(keeper, issue_body(egger, (batch, "5")), key)
    fixed = post_issue(keeper, issue_body(egger, (batch, "3")), key)

    assert (failed.status_code, fixed.status_code) == (409, 201)


def test_permissions(keeper_user, supervisor, egger):
    """Chiqim uchun ``inventory.add_issue``, ko'rish uchun ``inventory.view_stock``."""
    batch = receive(egger, keeper_user, "10", "100.00")
    stranger = client_for(make_user("stranger"))

    assert post_issue(supervisor, issue_body(egger, (batch, "1"))).status_code == 403
    assert stranger.get(ISSUES).status_code == 403
    assert APIClient().get(ISSUES).status_code == 403
    assert supervisor.get(ISSUES).status_code == 200


def test_supervisor_does_not_see_prices(keeper, keeper_user, supervisor, egger):
    """Narx ruxsatisiz javobda ``total_cost``, ``currency`` va ``unit_price`` yo'q."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issue_id = post_issue(keeper, issue_body(egger, (batch, "2"))).data["id"]

    data = supervisor.get(f"{ISSUES}{issue_id}/").data

    assert "total_cost" not in data
    assert "currency" not in data
    assert "unit_price" not in data["allocations"][0]
    assert data["allocations"][0]["quantity"] == "2.00"


def test_issues_cannot_be_changed_or_deleted(keeper, keeper_user, egger):
    """Chiqim o'zgarmas: ``PUT``, ``PATCH``, ``DELETE`` — 405 (TZ 6.8)."""
    batch = receive(egger, keeper_user, "10", "100.00")
    url = f"{ISSUES}{post_issue(keeper, issue_body(egger, (batch, '1'))).data['id']}/"

    assert keeper.put(url, {}, format="json").status_code == 405
    assert keeper.patch(url, {}, format="json").status_code == 405
    assert keeper.delete(url).status_code == 405


def test_list_filters(keeper, keeper_user, egger, glue):
    """Ro'yxat ``material``, ``project_id`` va sana oralig'i bo'yicha filtrlanadi."""
    board = receive(egger, keeper_user, "10", "100.00")
    pva = receive(glue, keeper_user, "10", "50.00")
    week_ago = (timezone.localdate() - timedelta(days=7)).isoformat()
    post_issue(keeper, issue_body(egger, (board, "1"), project_id=5))
    post_issue(keeper, issue_body(egger, (board, "1"), issued_on=week_ago))
    post_issue(keeper, issue_body(glue, (pva, "1"), project_id=5))

    def count(query: str) -> int:
        """Filtr bilan qaytgan chiqimlar soni."""
        return keeper.get(f"{ISSUES}?{query}").data["count"]

    assert count("") == 3
    assert count(f"material={egger.pk}") == 2
    assert count("project_id=5") == 2
    assert count(f"date_to={week_ago}") == 1
    assert count(f"date_from={timezone.localdate().isoformat()}") == 2
    assert keeper.get(f"{ISSUES}?project_id=abc").status_code == 400


@pytest.mark.parametrize(
    ("language", "message"),
    [
        ("uz", "Omborda yetarli material yo'q."),
        ("ru", "На складе недостаточно материала."),
        ("en", "Not enough material in stock."),
    ],
)
def test_conflict_message_follows_language(
    keeper, keeper_user, egger, language, message
):
    """409 xabari so'ralgan tilda (uz/ru/en), summa esa doim USD."""
    batch = receive(egger, keeper_user, "1", "10.00")

    response = post_issue(
        keeper, issue_body(egger, (batch, "2")), HTTP_ACCEPT_LANGUAGE=language
    )

    assert response.status_code == 409
    assert str(response.data["detail"]) == message


@postgres_only
@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_parallel_issues_never_make_stock_negative():
    """Qoldiq 10: ikki ulanishdan bir vaqtda 7 tadan chiqim — bittasi o'tadi.

    Qabul mezoni (rol fayli, PCRM-44): ikkinchi so'rov qulfni kutadi, keyin
    qoldiq 3 ekanini ko'radi va 409 oladi. Qoldiq manfiy bo'lmaydi.
    """
    user = make_user("keeper_parallel", VIEW, ADD)
    category = Category.objects.create(name="Parallel sinov")
    material = Material.objects.create(category=category, name="MDF", unit=Unit.SHEET)
    batch = receive(material, user, "10", "100.00")
    start = threading.Barrier(2)
    statuses: list[int] = []

    def worker() -> None:
        """Alohida ulanishdan 7 ta chiqim yuboradi va javob holatini yozadi."""
        try:
            client = client_for(user)
            start.wait(timeout=10)
            statuses.append(
                post_issue(client, issue_body(material, (batch, "7"))).status_code
            )
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert sorted(statuses) == [201, 409]
    assert on_hand(material) == Decimal("3")
    batch.refresh_from_db()
    assert batch.quantity_remaining == Decimal("3")
    assert StockIssue.objects.count() == 1
