"""PCRM-44: qaytarish (OQ-003) va hisobdan chiqarish (OQ-007) so'rovlari.

Qabul mezonlari: kutilayotgan yoki rad etilgan so'rov qoldiqni o'zgartirmaydi;
tasdiq qoldiqni faqat bir marta o'zgartiradi; jami qaytarish asl chiqimdan
oshmaydi; ruxsatsiz amal rad etiladi; jarayon o'rtasidagi xato hammasini
ortga qaytaradi; harakatlar tarixida har amal bir marta ko'rinadi.
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
    RequestStatus,
    StockBalance,
    StockIssue,
    StockMovement,
    StockReturn,
    StockReturnAllocation,
    WriteOff,
)
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

ISSUES = "/api/v1/issues/"
RETURNS = "/api/v1/returns/"
WRITE_OFFS = "/api/v1/write-offs/"
MOVEMENTS = "/api/v1/movements/"
KEEPER_CODES = (
    "inventory.view_stock",
    "inventory.view_purchase_price",
    "inventory.add_issue",
    "inventory.add_return",
    "inventory.approve_return",
    "inventory.add_write_off",
)

postgres_only = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="Qatorni qulflash (select_for_update) faqat PostgreSQL'da sinaladi",
)


def make_user(username: str, *codes: str, role_code: str | None = None):
    """Foydalanuvchi yaratadi va unga ruxsat kodlari bilan rol biriktiradi."""
    user = get_user_model().objects.create_user(username=username, password="x")
    role = Role.objects.create(
        code=role_code or f"TEST_{username.upper()}",
        name=username,
        permissions=list(codes),
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
    """Ombor mas'uli: chiqim, qaytarish va uni tasdiqlash, hisobdan chiqarish so'rovi."""
    return make_user("keeper", *KEEPER_CODES)


@pytest.fixture
def keeper(keeper_user) -> APIClient:
    """Ombor mas'uli nomidan mijoz."""
    return client_for(keeper_user)


@pytest.fixture
def admin_user():
    """Administrator (``ADMIN`` roli barcha ruxsatlarga ega)."""
    return make_user("boss", role_code="ADMIN")


@pytest.fixture
def admin(admin_user) -> APIClient:
    """Administrator nomidan mijoz."""
    return client_for(admin_user)


@pytest.fixture
def egger() -> Material:
    """Sinov materiali."""
    return Material.objects.create(
        category=Category.objects.get(name="LDSP"),
        name="LDSP Egger",
        color="oq",
        thickness_cm=Decimal("1.60"),
        unit=Unit.SHEET,
    )


def receive(material, user, quantity: str, total: str, days_ago: int = 0) -> Batch:
    """Servis orqali kirim qiladi va partiyani qaytaradi."""
    batch, _ = services.receive(
        material=material,
        received_on=timezone.localdate() - timedelta(days=days_ago),
        quantity=Decimal(quantity),
        total_amount=Decimal(total),
        user=user,
    )
    return batch


def post(client: APIClient, url: str, body: dict, key: uuid.UUID | None = None):
    """``POST`` so'rovini ``Idempotency-Key`` bilan yuboradi."""
    return client.post(
        url, body, format="json", HTTP_IDEMPOTENCY_KEY=str(key or uuid.uuid4())
    )


def parts(*pairs: tuple[Batch, str]) -> list[dict]:
    """``(partiya, miqdor)`` juftliklaridan ``allocations`` ro'yxatini tuzadi."""
    return [{"batch_id": batch.pk, "quantity": qty} for batch, qty in pairs]


def issue(client: APIClient, material, *pairs: tuple[Batch, str]) -> dict:
    """API orqali chiqim yozadi va javob tanasini qaytaradi."""
    response = post(
        client,
        ISSUES,
        {
            "material_id": material.pk,
            "recipient_name": "Sardor",
            "allocations": parts(*pairs),
        },
    )
    assert response.status_code == 201, response.data
    return response.data


def request_return(client: APIClient, issue_id: int, *pairs, key=None):
    """Qaytarish so'rovini yuboradi."""
    body = {"issue_id": issue_id, "reason": "Ortib qoldi", "allocations": parts(*pairs)}
    return post(client, RETURNS, body, key)


def request_write_off(client: APIClient, material, *pairs, reason="Namlikdan buzildi"):
    """Hisobdan chiqarish so'rovini yuboradi."""
    body = {"material_id": material.pk, "reason": reason, "allocations": parts(*pairs)}
    return post(client, WRITE_OFFS, body)


def on_hand(material) -> Decimal:
    """Materialning joriy umumiy qoldig'i."""
    return StockBalance.objects.get(material=material).quantity_on_hand


def remaining(batch: Batch) -> Decimal:
    """Partiyaning joriy qoldig'i."""
    batch.refresh_from_db()
    return batch.quantity_remaining


# --- Qaytarish ------------------------------------------------------------------


def test_return_changes_stock_only_after_approval(keeper, keeper_user, egger):
    """So'rov qoldiqni o'zgartirmaydi; tasdiqdan keyin qoldiq va partiya oshadi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "6"))

    created = request_return(keeper, issued["id"], (batch, "2"))

    assert created.status_code == 201, created.data
    assert created.data["status"] == "pending"
    assert created.data["issue"]["id"] == issued["id"]
    assert created.data["total_cost"] == "20.00"
    assert on_hand(egger) == Decimal("4")
    assert not StockMovement.objects.filter(type=MovementType.RETURN).exists()

    approved = keeper.post(
        f"{RETURNS}{created.data['id']}/approve/", {"note": "Ko'rildi"}
    )

    assert approved.status_code == 200, approved.data
    assert approved.data["status"] == "approved"
    assert approved.data["decided_by"]["id"] == keeper_user.pk
    assert approved.data["decision_note"] == "Ko'rildi"
    assert on_hand(egger) == Decimal("6")
    assert remaining(batch) == Decimal("6")
    movement = StockMovement.objects.get(type=MovementType.RETURN)
    assert movement.quantity == Decimal("2")
    assert movement.batch_id == batch.pk
    assert (movement.reference_kind, movement.reference_id) == (
        "return",
        created.data["id"],
    )
    assert movement.reason == "Ortib qoldi"
    assert movement.created_by == keeper_user


def test_return_goes_back_to_its_own_batches(keeper, keeper_user, egger):
    """Ikki partiyali chiqimdan qaytgan material har biri o'z partiyasiga tushadi."""
    old = receive(egger, keeper_user, "5", "100.00", days_ago=2)
    new = receive(egger, keeper_user, "5", "150.00")
    issued = issue(keeper, egger, (old, "5"), (new, "3"))

    return_id = request_return(keeper, issued["id"], (old, "1"), (new, "2")).data["id"]
    keeper.post(f"{RETURNS}{return_id}/approve/")

    assert remaining(old) == Decimal("1")
    assert remaining(new) == Decimal("4")
    assert on_hand(egger) == Decimal("5")


def test_double_approval_writes_one_movement(keeper, keeper_user, egger):
    """Ikki marta tasdiqlash: ikkala javob 200, qoldiq bir marta oshadi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "5"))
    return_id = request_return(keeper, issued["id"], (batch, "2")).data["id"]

    first = keeper.post(f"{RETURNS}{return_id}/approve/")
    second = keeper.post(f"{RETURNS}{return_id}/approve/")

    assert (first.status_code, second.status_code) == (200, 200)
    assert second.data["status"] == "approved"
    assert StockMovement.objects.filter(type=MovementType.RETURN).count() == 1
    assert on_hand(egger) == Decimal("7")


def test_return_cannot_exceed_original_issue(keeper, keeper_user, egger):
    """Jami qaytarish asl chiqimdan oshmaydi; kutilayotgan so'rov ham hisobga kiradi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "4"))

    too_much = request_return(keeper, issued["id"], (batch, "5"))
    first = request_return(keeper, issued["id"], (batch, "3"))
    second = request_return(keeper, issued["id"], (batch, "2"))

    assert too_much.status_code == 409
    assert too_much.data["code"] == "return_exceeds_issue"
    assert too_much.data["available"] == "4.00"
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.data["available"] == "1.00"

    keeper.post(f"{RETURNS}{first.data['id']}/reject/", {"note": "Xato"})
    after_reject = request_return(keeper, issued["id"], (batch, "4"))

    assert after_reject.status_code == 201, after_reject.data


def test_approval_rechecks_limit_under_lock(keeper, keeper_user, egger):
    """Limitdan o'tib ketgan so'rov (masalan, poyga natijasi) tasdiqda 409 oladi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "4"))
    first = request_return(keeper, issued["id"], (batch, "3")).data["id"]
    # Kutilayotgan so'rovni chetlab ikkinchi so'rov yaratamiz (poyga holati).
    sneaky = StockReturn.objects.create(
        issue_id=issued["id"],
        quantity=Decimal("3"),
        returned_on=timezone.localdate(),
        created_by=keeper_user,
    )
    StockReturnAllocation.objects.create(
        stock_return=sneaky, batch=batch, quantity=Decimal("3")
    )

    assert keeper.post(f"{RETURNS}{first}/approve/").status_code == 200
    late = keeper.post(f"{RETURNS}{sneaky.pk}/approve/")

    assert late.status_code == 409
    assert late.data["code"] == "return_exceeds_issue"
    assert on_hand(egger) == Decimal("9")
    sneaky.refresh_from_db()
    assert sneaky.status == RequestStatus.PENDING


def test_return_batch_must_belong_to_issue(keeper, keeper_user, egger):
    """Asl chiqimda bo'lmagan partiyaga qaytarish 400."""
    used = receive(egger, keeper_user, "10", "100.00", days_ago=1)
    other = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (used, "4"))

    response = request_return(keeper, issued["id"], (other, "1"))

    assert response.status_code == 400
    assert response.data["allocations"][0].code == "batch_not_in_issue"


def test_rejected_return_cannot_be_approved(keeper, keeper_user, egger):
    """Rad etilgan so'rov qoldiqni o'zgartirmaydi va keyin tasdiqlanmaydi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "4"))
    return_id = request_return(keeper, issued["id"], (batch, "2")).data["id"]

    rejected = keeper.post(f"{RETURNS}{return_id}/reject/")
    again = keeper.post(f"{RETURNS}{return_id}/reject/")
    approve = keeper.post(f"{RETURNS}{return_id}/approve/")

    assert (rejected.status_code, again.status_code) == (200, 200)
    assert rejected.data["status"] == "rejected"
    assert approve.status_code == 409
    assert approve.data["code"] == "already_decided"
    assert approve.data["status"] == "rejected"
    assert on_hand(egger) == Decimal("6")


def test_return_create_is_idempotent(keeper, keeper_user, egger):
    """Qayta yuborilgan so'rov bitta qaytarish; boshqa tana bilan kalit — 409."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "4"))
    key = uuid.uuid4()

    first = request_return(keeper, issued["id"], (batch, "1"), key=key)
    replay = request_return(keeper, issued["id"], (batch, "1"), key=key)
    other = request_return(keeper, issued["id"], (batch, "2"), key=key)

    assert (first.status_code, replay.status_code, other.status_code) == (201, 200, 409)
    assert replay.data == first.data
    assert StockReturn.objects.count() == 1


def test_return_permissions(keeper, keeper_user, egger):
    """Qaytarish so'rovi va tasdig'i alohida ruxsat bilan; aks holda 403."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "4"))
    clerk = client_for(
        make_user("clerk", "inventory.view_stock", "inventory.add_return")
    )
    viewer = client_for(make_user("viewer", "inventory.view_stock"))

    assert request_return(viewer, issued["id"], (batch, "1")).status_code == 403
    return_id = request_return(clerk, issued["id"], (batch, "1")).data["id"]
    assert clerk.post(f"{RETURNS}{return_id}/approve/").status_code == 403
    assert viewer.post(f"{RETURNS}{return_id}/reject/").status_code == 403
    assert viewer.get(f"{RETURNS}{return_id}/").status_code == 200
    assert APIClient().get(RETURNS).status_code == 403
    assert keeper.delete(f"{RETURNS}{return_id}/").status_code == 405
    assert on_hand(egger) == Decimal("6")


def test_return_list_filters(keeper, keeper_user, egger):
    """Ro'yxat ``status`` va ``issue`` bo'yicha filtrlanadi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "4"))
    first = request_return(keeper, issued["id"], (batch, "1")).data["id"]
    request_return(keeper, issued["id"], (batch, "1"))
    keeper.post(f"{RETURNS}{first}/approve/")

    assert keeper.get(f"{RETURNS}?status=pending").data["count"] == 1
    assert keeper.get(f"{RETURNS}?issue={issued['id']}").data["count"] == 2
    assert keeper.get(f"{RETURNS}?status=nope").status_code == 400


# --- Hisobdan chiqarish ---------------------------------------------------------


def test_write_off_needs_admin_and_changes_stock_only_on_approval(
    keeper, keeper_user, admin, admin_user, egger
):
    """Ombor mas'uli so'raydi (qoldiq o'zgarmaydi), admin tasdiqlaydi (kamayadi)."""
    batch = receive(egger, keeper_user, "10", "100.00")

    created = request_write_off(keeper, egger, (batch, "3"))

    assert created.status_code == 201, created.data
    assert created.data["status"] == "pending"
    assert on_hand(egger) == Decimal("10")
    assert keeper.post(f"{WRITE_OFFS}{created.data['id']}/approve/").status_code == 403
    assert on_hand(egger) == Decimal("10")

    approved = admin.post(f"{WRITE_OFFS}{created.data['id']}/approve/")

    assert approved.status_code == 200, approved.data
    assert approved.data["status"] == "approved"
    assert approved.data["decided_by"]["id"] == admin_user.pk
    assert on_hand(egger) == Decimal("7")
    assert remaining(batch) == Decimal("7")
    movement = StockMovement.objects.get(type=MovementType.WRITE_OFF)
    assert movement.quantity == Decimal("-3")
    assert movement.reason == "Namlikdan buzildi"
    assert movement.created_by == admin_user
    assert (movement.reference_kind, movement.reference_id) == (
        "write_off",
        created.data["id"],
    )


def test_rejected_write_off_keeps_stock(keeper, keeper_user, admin, egger):
    """Rad etilgan so'rov qoldiqni o'zgartirmaydi va harakat yozmaydi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    write_off_id = request_write_off(keeper, egger, (batch, "3")).data["id"]

    rejected = admin.post(f"{WRITE_OFFS}{write_off_id}/reject/", {"note": "Yaroqli"})

    assert rejected.status_code == 200
    assert rejected.data["status"] == "rejected"
    assert rejected.data["decision_note"] == "Yaroqli"
    assert on_hand(egger) == Decimal("10")
    assert not StockMovement.objects.filter(type=MovementType.WRITE_OFF).exists()
    assert admin.post(f"{WRITE_OFFS}{write_off_id}/approve/").status_code == 409


def test_write_off_double_approval_writes_one_movement(
    keeper, keeper_user, admin, egger
):
    """Admin ikki marta bosadi: qoldiq bir marta kamayadi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    write_off_id = request_write_off(keeper, egger, (batch, "3")).data["id"]

    admin.post(f"{WRITE_OFFS}{write_off_id}/approve/")
    second = admin.post(f"{WRITE_OFFS}{write_off_id}/approve/")

    assert second.status_code == 200
    assert StockMovement.objects.filter(type=MovementType.WRITE_OFF).count() == 1
    assert on_hand(egger) == Decimal("7")


def test_write_off_approval_rechecks_stock(keeper, keeper_user, admin, egger):
    """So'rovdan keyin material chiqib ketsa, tasdiq 409 va so'rov kutilayotgan qoladi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    write_off_id = request_write_off(keeper, egger, (batch, "5")).data["id"]
    issue(keeper, egger, (batch, "8"))

    response = admin.post(f"{WRITE_OFFS}{write_off_id}/approve/")

    assert response.status_code == 409
    assert response.data["code"] == "insufficient_stock"
    assert WriteOff.objects.get(pk=write_off_id).status == RequestStatus.PENDING
    assert on_hand(egger) == Decimal("2")


def test_write_off_validation(keeper, keeper_user, egger):
    """Sabab majburiy; ombordagidan ko'p miqdorga so'rov 409."""
    batch = receive(egger, keeper_user, "10", "100.00")

    no_reason = request_write_off(keeper, egger, (batch, "1"), reason="  ")
    too_much = request_write_off(keeper, egger, (batch, "11"))

    assert no_reason.status_code == 400
    assert "reason" in no_reason.data
    assert too_much.status_code == 409
    assert too_much.data["code"] == "insufficient_stock"
    assert not WriteOff.objects.exists()


def test_viewer_without_price_permission_sees_no_cost(keeper, keeper_user, egger):
    """Narx ruxsatisiz javobda ``total_cost`` va ``unit_price`` yo'q (OQ-041)."""
    batch = receive(egger, keeper_user, "10", "100.00")
    write_off_id = request_write_off(keeper, egger, (batch, "1")).data["id"]
    viewer = client_for(make_user("viewer", "inventory.view_stock"))

    data = viewer.get(f"{WRITE_OFFS}{write_off_id}/").data

    assert "total_cost" not in data
    assert "unit_price" not in data["allocations"][0]


# --- Tarix va tranzaksiya --------------------------------------------------------


def test_movements_history_counts_each_operation_once(
    keeper, keeper_user, admin, egger
):
    """Harakatlar API'sida har amal bir marta; kutilayotgan so'rov ko'rinmaydi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "6"))
    return_id = request_return(keeper, issued["id"], (batch, "2")).data["id"]
    keeper.post(f"{RETURNS}{return_id}/approve/")
    keeper.post(f"{RETURNS}{return_id}/approve/")
    write_off_id = request_write_off(keeper, egger, (batch, "1")).data["id"]
    admin.post(f"{WRITE_OFFS}{write_off_id}/approve/")
    request_write_off(keeper, egger, (batch, "1"))  # kutilmoqda — tarixda yo'q

    rows = keeper.get(f"{MOVEMENTS}?material={egger.pk}").data["results"]

    kinds = sorted((row["type"], row["reference"]["kind"]) for row in rows)
    assert kinds == [
        ("issue", "issue"),
        ("receipt", "receipt"),
        ("return", "return"),
        ("write_off", "write_off"),
    ]
    assert (
        sum(Decimal(row["quantity"]) for row in rows) == on_hand(egger) == Decimal("5")
    )


def test_failure_mid_issue_rolls_everything_back(
    keeper, keeper_user, egger, monkeypatch
):
    """Harakat yozishda xato: chiqim, qismlar, partiya, qoldiq va kalit saqlanmaydi."""
    batch = receive(egger, keeper_user, "10", "100.00")

    def broken_create(**kwargs):
        """Harakat yozilishi o'rtasida yuz bergan kutilmagan xato."""
        raise RuntimeError("disk full")

    monkeypatch.setattr(StockMovement.objects, "create", broken_create)
    with pytest.raises(RuntimeError):
        post(
            keeper,
            ISSUES,
            {
                "material_id": egger.pk,
                "recipient_name": "Sardor",
                "allocations": parts((batch, "4")),
            },
        )

    assert not StockIssue.objects.exists()
    assert not IdempotencyKey.objects.exists()
    assert remaining(batch) == Decimal("10")
    assert on_hand(egger) == Decimal("10")


def test_failure_mid_approval_rolls_everything_back(
    keeper, keeper_user, egger, monkeypatch
):
    """Tasdiq yozilishida xato: qoldiq, partiya, harakat va holat o'zgarmaydi."""
    batch = receive(egger, keeper_user, "10", "100.00")
    issued = issue(keeper, egger, (batch, "4"))
    return_id = request_return(keeper, issued["id"], (batch, "2")).data["id"]

    def broken_mark(*args, **kwargs):
        """Qaror yozilishi paytidagi kutilmagan xato."""
        raise RuntimeError("connection lost")

    monkeypatch.setattr(services, "mark_decided", broken_mark)
    with pytest.raises(RuntimeError):
        keeper.post(f"{RETURNS}{return_id}/approve/")

    assert StockReturn.objects.get(pk=return_id).status == RequestStatus.PENDING
    assert not StockMovement.objects.filter(type=MovementType.RETURN).exists()
    assert remaining(batch) == Decimal("6")
    assert on_hand(egger) == Decimal("6")


# --- PostgreSQL: parallel ulanishlar ----------------------------------------------


def run_parallel(user, count: int, send) -> list[int]:
    """``send(client)`` ni ``count`` ta oqimda bir vaqtda chaqiradi; javob kodlarini qaytaradi."""
    start = threading.Barrier(count)
    statuses: list[int] = []

    def worker() -> None:
        """Alohida ulanishdan so'rov yuboradi va javob holatini yozadi."""
        try:
            client = client_for(user)
            start.wait(timeout=10)
            statuses.append(send(client).status_code)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    return statuses


def parallel_material(user) -> tuple[Material, Batch]:
    """Tranzaksion sinov uchun alohida kategoriya, material va 10 dona kirim."""
    category = Category.objects.create(name=f"Parallel {uuid.uuid4().hex[:6]}")
    material = Material.objects.create(category=category, name="MDF", unit=Unit.SHEET)
    return material, receive(material, user, "10", "100.00")


@postgres_only
@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_parallel_double_approval_of_return_moves_stock_once():
    """Ikki ulanishdan bir vaqtda tasdiq: qoldiq bir marta oshadi, harakat bitta."""
    user = make_user("keeper_return_race", *KEEPER_CODES)
    material, batch = parallel_material(user)
    stock_issue, _ = services.issue_stock(
        material=material,
        allocations=[services.Allocation(batch.pk, Decimal("6"))],
        issued_on=timezone.localdate(),
        recipient_name="Sardor",
        user=user,
    )
    stock_return = services.request_return(
        issue=stock_issue,
        allocations=[services.Allocation(batch.pk, Decimal("2"))],
        returned_on=timezone.localdate(),
        user=user,
    )

    statuses = run_parallel(
        user, 2, lambda client: client.post(f"{RETURNS}{stock_return.pk}/approve/")
    )

    assert statuses == [200, 200]
    assert StockMovement.objects.filter(type=MovementType.RETURN).count() == 1
    assert on_hand(material) == Decimal("6")


@postgres_only
@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_parallel_double_approval_of_write_off_moves_stock_once():
    """Admin ikki oynadan bir vaqtda tasdiqlaydi: qoldiq bir marta kamayadi."""
    admin_user = make_user("boss_race", role_code="ADMIN")
    material, batch = parallel_material(admin_user)
    write_off = services.request_write_off(
        material=material,
        allocations=[services.Allocation(batch.pk, Decimal("3"))],
        reason="Buzilgan",
        user=admin_user,
    )

    statuses = run_parallel(
        admin_user,
        2,
        lambda client: client.post(f"{WRITE_OFFS}{write_off.pk}/approve/"),
    )

    assert statuses == [200, 200]
    assert StockMovement.objects.filter(type=MovementType.WRITE_OFF).count() == 1
    assert on_hand(material) == Decimal("7")


def test_returnable_preview_counts_pending_and_approved_without_price_leaks(
    keeper, keeper_user, egger
):
    """Ko‘rsatilgan chegara qayta qaytarilgan yoki band qilingan qismni ayiradi."""
    batch = receive(egger, keeper_user, "10", "300")
    issued = issue(keeper, egger, (batch, "7"))
    pending = request_return(keeper, issued["id"], (batch, "2"))
    assert pending.status_code == 201
    url = f"{ISSUES}{issued['id']}/returnable/"
    response = keeper.get(url)
    assert response.status_code == 200
    assert response.data["allocations"][0]["quantity"] == "7.00"
    assert response.data["allocations"][0]["returnable_quantity"] == "5.00"
    assert on_hand(egger) == Decimal("3.00")
    approved = post(keeper, f"{RETURNS}{pending.data['id']}/approve/", {})
    assert approved.status_code == 200
    assert keeper.get(url).data["allocations"][0]["returnable_quantity"] == "5.00"
    pending_again = request_return(keeper, issued["id"], (batch, "1"))
    assert keeper.get(url).data["allocations"][0]["returnable_quantity"] == "4.00"
    assert (
        post(keeper, f"{RETURNS}{pending_again.data['id']}/reject/", {}).status_code
        == 200
    )
    assert keeper.get(url).data["allocations"][0]["returnable_quantity"] == "5.00"
    reader = client_for(make_user("return_reader", "inventory.view_stock"))
    part = reader.get(url).data["allocations"][0]
    assert part["returnable_quantity"] == "5.00"
    assert "unit_price" not in part
    assert client_for(make_user("no_inventory")).get(url).status_code == 403
