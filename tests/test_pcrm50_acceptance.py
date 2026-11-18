"""PCRM-50: Brauzerda kirimdan qoldiqqacha qabul sinovi va salbiy holatlar.

Ushbu modul muhandislik rejasi (docs/03-architecture/warehouse-engineering-plan.md)
va 2026-11-18 dagi qarorlar jurnali (yagona USD valyutasi va uz/ru/en tillari)
asosida to'liq tizimli qabul (acceptance) sinovlarini o'z ichiga oladi:

1. End-to-end qabul oqimi: CSRF token -> Login sessiyasi -> Material tanlash ->
   Kirim (Receipt) qilish -> Partiya (Batch) yaratilishi -> Qoldiq (StockBalance)
   va material katalogidagi qoldiqning bir martada to'g'ri yangilanishi.
2. Tarmoq uzilishi va brauzer qayta yuborishi (Idempotency): bir xil Idempotency-Key
   va body bilan takroriy so'rovda qoldiq takror ortmasligi; turli body bilan
   yuborilganda 409 Conflict qaytarilishi.
3. Valyuta qat'iy tekshiruvi: faqat USD qabul qilinadi; UZS, EUR, RUB va boshqalar
   server tomonidan rad etiladi.
4. Ko'p tillilik (i18n): uz, ru, en tillari bo'yicha sessiya xabarlari va xatolar.
5. Xavfsizlik va ruxsatlar (salbiy holatlar): anonim so'rov, CSRF tokensiz so'rov,
   tegishli ruxsati bo'lmagan xodim amali rad etilishi; narx ko'rish ruxsati yo'qlarga
   narxlar yashirilishi.
6. Biznes qoidalari bo'yicha salbiy holatlar: kelajakdagi sana, manfiy yoki nol
   miqdor, faol bo'lmagan material.
"""

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from accounts.models import Role
from apps.catalog.models import Category, Material, Unit
from apps.inventory import services
from apps.inventory.models import (
    Batch,
    MovementType,
    StockBalance,
    StockMovement,
)
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

RECEIPTS_URL = "/api/v1/receipts/"
MATERIALS_URL = "/api/v1/materials/"
LOGIN_URL = "/api/auth/login/"
LOGOUT_URL = "/api/auth/logout/"
CSRF_URL = "/api/auth/csrf/"
ME_URL = "/api/auth/me/"


# --- Yordamchi funksiyalar va fixture'lar -------------------------------------


def create_role(code: str, name: str, permissions: list[str]) -> Role:
    """Sinov uchun maxsus rol yaratish yoki mavjud bo'lsa yangilash."""
    role, created = Role.objects.get_or_create(
        code=code,
        defaults={"name": name, "permissions": permissions},
    )
    if not created:
        role.permissions = list(permissions)
        role.name = name
        role.save()
    return role


def create_storekeeper(username: str = "storekeeper_pcrm50") -> tuple:
    """Ombor xodimi foydalanuvchisi va parolini yaratish."""
    password = "StorekeeperPassword123!"
    user = get_user_model().objects.create_user(
        username=username,
        password=password,
        first_name="Ombor",
        last_name="Mas'uli",
    )
    role = create_role(
        code=f"STOREKEEPER_ROLE_{username.upper()}",
        name=f"Ombor Mas'uli {username}",
        permissions=[
            "catalog.view_material",
            "inventory.view_stock",
            "inventory.add_receipt",
            "inventory.view_purchase_price",
        ],
    )
    user.roles.add(role)
    return user, password


def create_worker(username: str = "worker_pcrm50") -> tuple:
    """Faqat katalog ko'rish huquqiga ega oddiy ishchi yaratish."""
    password = "WorkerPassword123!"
    user = get_user_model().objects.create_user(
        username=username,
        password=password,
        first_name="Oddiy",
        last_name="Ishchi",
    )
    role = create_role(
        code="WORKER_ROLE",
        name="Ishchi",
        permissions=["catalog.view_material"],
    )
    user.roles.add(role)
    return user, password


@pytest.fixture
def sample_material() -> Material:
    """Sinov uchun birlamchi material (MDF)."""
    category = Category.objects.filter(name="MDF").first()
    if not category:
        category = Category.objects.create(name="MDF", is_active=True)
    return Material.objects.create(
        category=category,
        name="MDF Standart",
        thickness_cm=Decimal("1.80"),
        unit=Unit.SHEET,
        is_active=True,
    )


# --- 1. To'liq ijobiy oqim (End-to-End Acceptance Flow) ----------------------


def test_pcrm50_e2e_login_catalog_receipt_and_stock_flow(sample_material):
    """Qabul mezoni: Omborchi tizimga kiradi, materialni ko'radi, kirim qiladi

    va qoldiq bir marta yangilanib, katalogda ham aks etadi (barchasi USD'da).
    """
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)

    # 1. CSRF token olish
    csrf_res = client.get(CSRF_URL)
    assert csrf_res.status_code == 200
    token = csrf_res.data["csrfToken"]
    assert token

    # 2. Login qilish
    login_res = client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert login_res.status_code == 200
    assert login_res.data["user"]["username"] == user.username

    # 3. Profil va rollarni tekshirish
    me_res = client.get(ME_URL)
    assert me_res.status_code == 200
    assert "inventory.add_receipt" in me_res.data["roles"][0]["permissions"]

    # 4. Katalogdagi dastlabki qoldiqni tekshirish (0 bo'lishi kerak)
    mat_detail_url = f"{MATERIALS_URL}{sample_material.pk}/"
    mat_res = client.get(mat_detail_url)
    assert mat_res.status_code == 200
    assert mat_res.data["quantity_on_hand"] == "0.00"

    # 5. Idempotency-Key bilan kirim (Receipt) yuborish
    key = str(uuid.uuid4())
    receipt_data = {
        "material_id": sample_material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "50.00",
        "total_amount": "1250.00",
        "currency": "USD",
        "supplier": "Premium MDF Ta'minot",
        "document_number": "DOC-2026-PCRM50",
    }
    # Har bir yozish amali uchun yangi CSRF tokenini ta'minlash
    fresh_csrf = client.get(CSRF_URL).data["csrfToken"]
    receipt_res = client.post(
        RECEIPTS_URL,
        receipt_data,
        format="json",
        HTTP_X_CSRFTOKEN=fresh_csrf,
        headers={"Idempotency-Key": key},
    )

    # 6. Kirim javobini tekshirish
    assert receipt_res.status_code == 201
    res_body = receipt_res.data
    assert res_body["quantity"] == "50.00"
    assert res_body["quantity_remaining"] == "50.00"
    assert res_body["total_amount"] == "1250.00"
    assert res_body["currency"] == "USD"
    # Birlik narxi: 1250 / 50 = 25.000000
    assert Decimal(res_body["unit_price"]) == Decimal("25.000000")
    assert res_body["quantity_on_hand_after"] == "50.00"

    # 7. Ma'lumotlar bazasini qat'iy tekshirish
    batch = Batch.objects.get(pk=res_body["id"])
    assert batch.material == sample_material
    assert batch.quantity == Decimal("50.00")
    assert batch.quantity_remaining == Decimal("50.00")
    assert batch.currency == "USD"

    movement = StockMovement.objects.get(batch=batch)
    assert movement.type == MovementType.RECEIPT
    assert movement.quantity == Decimal("50.00")
    assert movement.created_by == user

    stock = StockBalance.objects.get(material=sample_material)
    assert stock.quantity_on_hand == Decimal("50.00")

    # 8. Katalogda qoldiq yangilanganini tasdiqlash
    updated_mat_res = client.get(mat_detail_url)
    assert updated_mat_res.status_code == 200
    assert updated_mat_res.data["quantity_on_hand"] == "50.00"


# --- 2. Tarmoq uzilishi va Idempotency testlari -------------------------------


def test_pcrm50_browser_retry_exact_key_and_body_does_not_duplicate_stock(
    sample_material,
):
    """Tarmoq uzilishi: ayni Idempotency-Key va body bilan so'rov qayta yuborilganda

    qoldiq ikki marta oshmaydi, ikkinchi partiya yaratilmaydi.
    """
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)

    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    key = str(uuid.uuid4())
    payload = {
        "material_id": sample_material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "20.00",
        "total_amount": "500.00",
        "currency": "USD",
        "supplier": "Test Supplier",
    }

    # 1-marta yuborish
    first_res = client.post(
        RECEIPTS_URL,
        payload,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": key},
    )
    assert first_res.status_code == 201

    # 2-marta tarmoq qayta ulanib bir xil kalit va tana yuborilganda
    retry_res = client.post(
        RECEIPTS_URL,
        payload,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": key},
    )
    # Server birinchi natijani qaytaradi (201 yoki 200)
    assert retry_res.status_code in (200, 201)
    assert retry_res.data["id"] == first_res.data["id"]

    # Qoldiq 40 emas, aynan 20.00 bo'lib qolishi shart
    balance = StockBalance.objects.get(material=sample_material)
    assert balance.quantity_on_hand == Decimal("20.00")
    assert Batch.objects.filter(material=sample_material).count() == 1
    assert StockMovement.objects.filter(material=sample_material).count() == 1


def test_pcrm50_browser_retry_same_key_different_body_is_rejected_with_409(
    sample_material,
):
    """Bir xil Idempotency-Key bilan BOSHQA parametr yuborilsa, 409 Conflict qaytadi."""
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)

    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    key = str(uuid.uuid4())
    payload1 = {
        "material_id": sample_material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "10.00",
        "total_amount": "200.00",
        "currency": "USD",
    }
    client.post(
        RECEIPTS_URL,
        payload1,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": key},
    )

    # Turli miqdor bilan ayni kalitdan qayta foydalanishga urinish
    payload2 = {
        "material_id": sample_material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "30.00",  # boshqa miqdor
        "total_amount": "600.00",
        "currency": "USD",
    }
    conflict_res = client.post(
        RECEIPTS_URL,
        payload2,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": key},
    )
    assert conflict_res.status_code == 409


# --- 3. Yagona USD valyutasi talabi --------------------------------------------


@pytest.mark.parametrize("invalid_currency", ["UZS", "EUR", "RUB", "usd"])
def test_pcrm50_currency_strict_usd_only(sample_material, invalid_currency):
    """2026-11-18 qarori: barcha pul hisoblari faqat USD.

    Boshqa valyutalar server tomonidan rad etiladi.
    """
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)

    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    bad_payload = {
        "material_id": sample_material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "10.00",
        "total_amount": "250.00",
        "currency": invalid_currency,
    }
    res = client.post(
        RECEIPTS_URL,
        bad_payload,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert res.status_code == 400
    assert "currency" in res.data


# --- 4. Ko'p tillilik (UZ / RU / EN) -------------------------------------------


@pytest.mark.parametrize(
    "lang,expected_login_msg,expected_logout_msg",
    [
        ("uz", "Tizimga muvaffaqiyatli kirildi", "Tizimdan muvaffaqiyatli chiqildi"),
        ("ru", "Успешный вход в систему", "Успешный выход из системы"),
        ("en", "Successfully logged in", "Successfully logged out"),
    ],
)
def test_pcrm50_multilingual_flow_uz_ru_en(
    lang, expected_login_msg, expected_logout_msg
):
    """Sessiya xabarlari Accept-Language ga qarab uz, ru, en da qaytadi."""
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)

    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    login_res = client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
        HTTP_ACCEPT_LANGUAGE=lang,
    )
    assert login_res.status_code == 200
    assert expected_login_msg in login_res.data["message"]

    logout_token = client.get(CSRF_URL).data["csrfToken"]
    logout_res = client.post(
        LOGOUT_URL,
        {},
        format="json",
        HTTP_X_CSRFTOKEN=logout_token,
        HTTP_ACCEPT_LANGUAGE=lang,
    )
    assert logout_res.status_code == 200
    assert expected_logout_msg in logout_res.data["message"]


# --- 5. Ruxsatlar va xavfsizlik (Salbiy holatlar) -----------------------------


def test_pcrm50_anonymous_request_cannot_create_receipt(sample_material):
    """Tizimga kirmagan (anonim) so'rov kirim qila olmaydi."""
    client = APIClient()
    payload = {
        "material_id": sample_material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "10.00",
        "total_amount": "200.00",
        "currency": "USD",
    }
    res = client.post(
        RECEIPTS_URL,
        payload,
        format="json",
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert res.status_code in (401, 403)


def test_pcrm50_worker_without_receipt_permission_is_forbidden(sample_material):
    """Kirim ruxsati (inventory.add_receipt) bo'lmagan xodim kirim qila olmaydi (403)."""
    user, password = create_worker()
    client = APIClient(enforce_csrf_checks=True)

    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    payload = {
        "material_id": sample_material.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "10.00",
        "total_amount": "200.00",
        "currency": "USD",
    }
    res = client.post(
        RECEIPTS_URL,
        payload,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert res.status_code == 403


def test_pcrm50_user_without_price_permission_sees_hidden_prices(sample_material):
    """inventory.view_purchase_price ruxsati bo'lmagan foydalanuvchiga narx ko'rinmaydi."""
    # 1. Avval omborda narx va summaga ega haqiqiy kirim yaratamiz
    admin_user = get_user_model().objects.create_user(
        username="admin_stock_creator", password="CreatorPassword123!"
    )
    batch, _ = services.receive(
        material=sample_material,
        received_on=timezone.localdate(),
        quantity=Decimal("10.00"),
        total_amount=Decimal("300.00"),
        user=admin_user,
        currency="USD",
        supplier="Test Supplier",
        document_number="DOC-PRICE-101",
    )

    # 2. Narx ko'rish ruxsati bo'lmagan foydalanuvchi yaratamiz
    limited_user, password = create_storekeeper(username="limited_storekeeper")
    role = limited_user.roles.first()
    role.permissions = ["catalog.view_material", "inventory.view_stock"]
    role.save()

    client = APIClient(enforce_csrf_checks=True)
    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": limited_user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    # 3. Kirimlar ro'yxatini ko'rish: ro'yxat bo'sh emas, aynan yaratilgan kirimda narxlar yashiringan
    res = client.get(RECEIPTS_URL)
    assert res.status_code == 200
    assert len(res.data["results"]) >= 1
    limited_receipt = next(
        item for item in res.data["results"] if item["id"] == batch.pk
    )
    # Narx maydonlari ruxsatsiz foydalanuvchiga umuman ko'rsatilmaydi (dict'dan o'chiriladi)
    assert "unit_price" not in limited_receipt
    assert "total_amount" not in limited_receipt
    assert "currency" not in limited_receipt
    assert limited_receipt["quantity"] == "10.00"

    # Alohida bitta kirim detail endpointida ham narxlar yashiringanini tekshirish
    detail_res = client.get(f"{RECEIPTS_URL}{batch.pk}/")
    assert detail_res.status_code == 200
    assert "unit_price" not in detail_res.data
    assert "total_amount" not in detail_res.data
    assert "currency" not in detail_res.data

    # 4. Solishtirish: narx ko'rish ruxsati BOR foydalanuvchi aynan shu yozuvda narxni ko'radi
    full_user, full_pwd = create_storekeeper(username="full_price_storekeeper")
    full_client = APIClient(enforce_csrf_checks=True)
    full_csrf = full_client.get(CSRF_URL).data["csrfToken"]
    full_client.post(
        LOGIN_URL,
        {"username": full_user.username, "password": full_pwd},
        format="json",
        HTTP_X_CSRFTOKEN=full_csrf,
    )
    full_res = full_client.get(RECEIPTS_URL)
    assert full_res.status_code == 200
    full_receipt = next(
        item for item in full_res.data["results"] if item["id"] == batch.pk
    )
    assert full_receipt["unit_price"] == "30.000000"
    assert full_receipt["total_amount"] == "300.00"
    assert full_receipt["currency"] == "USD"


# --- 6. Biznes qoidalari salbiy holatlari --------------------------------------


def test_pcrm50_future_date_receipt_is_rejected(sample_material):
    """Kelajakdagi sana bilan kirim qilish rad etiladi."""
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)
    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    future_date = (timezone.localdate() + timedelta(days=2)).isoformat()
    payload = {
        "material_id": sample_material.pk,
        "received_on": future_date,
        "quantity": "10.00",
        "total_amount": "200.00",
        "currency": "USD",
    }
    res = client.post(
        RECEIPTS_URL,
        payload,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert res.status_code == 400
    assert "received_on" in res.data


def test_pcrm50_zero_or_negative_quantity_is_rejected(sample_material):
    """Miqdor nol yoki manfiy bo'lsa, rad etiladi."""
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)
    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    for invalid_qty in ["0.00", "-5.00"]:
        payload = {
            "material_id": sample_material.pk,
            "received_on": timezone.localdate().isoformat(),
            "quantity": invalid_qty,
            "total_amount": "100.00",
            "currency": "USD",
        }
        res = client.post(
            RECEIPTS_URL,
            payload,
            format="json",
            HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert res.status_code == 400
        assert "quantity" in res.data


def test_pcrm50_inactive_material_is_rejected():
    """Arxivlangan (faol bo'lmagan) materialga kirim qilish rad etiladi."""
    category = Category.objects.filter(is_active=True).first()
    inactive_mat = Material.objects.create(
        category=category,
        name="Arxiv MDF",
        thickness_cm=Decimal("1.60"),
        unit=Unit.SHEET,
        is_active=False,
    )
    user, password = create_storekeeper()
    client = APIClient(enforce_csrf_checks=True)
    csrf_token = client.get(CSRF_URL).data["csrfToken"]
    client.post(
        LOGIN_URL,
        {"username": user.username, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    payload = {
        "material_id": inactive_mat.pk,
        "received_on": timezone.localdate().isoformat(),
        "quantity": "10.00",
        "total_amount": "200.00",
        "currency": "USD",
    }
    res = client.post(
        RECEIPTS_URL,
        payload,
        format="json",
        HTTP_X_CSRFTOKEN=client.get(CSRF_URL).data["csrfToken"],
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert res.status_code == 400
    assert "material_id" in res.data
