"""Foydalanuvchi autentifikatsiyasi, ko'p tillilik (i18n), CSRF va rollarni (OQ-037) tekshiruvchi testlar."""

import pytest
from accounts.models import Role
from accounts.permissions import IsAdminRole, IsWarehouseManager
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from rest_framework import status

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def csrf_client():
    return Client(enforce_csrf_checks=True)


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def default_roles(db):
    admin_role = Role.objects.create(
        code="ADMIN",
        name="Administrator",
        permissions=["*"],
        is_system=True,
    )
    warehouse_role = Role.objects.create(
        code="WAREHOUSE_MANAGER",
        name="Ombor mas'uli",
        permissions=[
            "view_catalog",
            "manage_catalog",
            "view_inventory",
            "manage_inventory",
        ],
        is_system=True,
    )
    worker_role = Role.objects.create(
        code="WORKER",
        name="Ishchi",
        permissions=["view_tasks", "record_work"],
        is_system=True,
    )
    supervisor_role = Role.objects.create(
        code="PRODUCTION_SUPERVISOR",
        name="Ishlab chiqarish nazoratchisi",
        permissions=["view_production", "manage_production"],
        is_system=True,
    )
    return {
        "admin": admin_role,
        "warehouse": warehouse_role,
        "worker": worker_role,
        "supervisor": supervisor_role,
    }


@pytest.fixture
def test_users(db, default_roles):
    admin_user = User.objects.create_user(
        username="admin_user",
        password="securepassword123",
        first_name="Ali",
        last_name="Valiyev",
    )
    admin_user.roles.add(default_roles["admin"])

    warehouse_user = User.objects.create_user(
        username="warehouse_user",
        password="securepassword123",
        first_name="Hasan",
        last_name="Husanov",
    )
    warehouse_user.roles.add(default_roles["warehouse"])

    worker_user = User.objects.create_user(
        username="worker_user",
        password="securepassword123",
        first_name="Botir",
        last_name="Sobirov",
    )
    worker_user.roles.add(default_roles["worker"])

    # Bir nechta rolga ega bo'lgan foydalanuvchi (Ombor + Ishlab chiqarish nazoratchisi)
    multi_role_user = User.objects.create_user(
        username="multi_user",
        password="securepassword123",
        first_name="Qodir",
        last_name="Karimov",
    )
    multi_role_user.roles.add(default_roles["warehouse"], default_roles["supervisor"])

    return {
        "admin": admin_user,
        "warehouse": warehouse_user,
        "worker": worker_user,
        "multi": multi_role_user,
    }


# ==============================================================================
# 1. CSRF Himoyasi Testlari
# ==============================================================================


@pytest.mark.django_db
def test_csrf_token_endpoint(csrf_client):
    """CSRF token olish API'si 200 qaytarishi va csrftoken cookie'sini o'rnatishi kerak."""
    response = csrf_client.get("/api/auth/csrf/")
    assert response.status_code == status.HTTP_200_OK
    assert "csrfToken" in response.json()
    assert "csrftoken" in csrf_client.cookies


@pytest.mark.django_db
def test_login_without_csrf_is_rejected(csrf_client, test_users):
    """CSRF tekshiruvi yoqilganda tokensiz login so'rovi 403 bilan rad etilishi kerak."""
    response = csrf_client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "securepassword123"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_login_with_csrf_succeeds(csrf_client, test_users):
    """CSRF token bilan yuborilgan login so'rovi 200 qaytarishi kerak."""
    csrf_resp = csrf_client.get("/api/auth/csrf/")
    csrf_token = csrf_resp.json()["csrfToken"]

    response = csrf_client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "securepassword123"},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["username"] == "warehouse_user"


# ==============================================================================
# 2. Ko'p tillilik (i18n / UZ, RU, EN) Testlari
# ==============================================================================


@pytest.mark.django_db
def test_login_messages_in_three_languages(client, test_users):
    """Login muvaffaqiyat xabari Accept-Language header'iga mos tilda qaytishi kerak."""
    # O'zbekcha (standart)
    res_uz = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "securepassword123"},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="uz",
    )
    assert res_uz.json()["message"] == "Tizimga muvaffaqiyatli kirildi."

    # Ruscha
    res_ru = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "securepassword123"},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="ru",
    )
    assert res_ru.json()["message"] == "Успешный вход в систему."

    # Inglizcha
    res_en = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "securepassword123"},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="en",
    )
    assert res_en.json()["message"] == "Successfully logged in."


@pytest.mark.django_db
def test_login_error_messages_in_three_languages(client, test_users):
    """Login xatosi ham so'ralgan tilga mos holda tarjima qilinishi kerak."""
    # O'zbekcha
    res_uz = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "wrongpassword"},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="uz",
    )
    assert "Login yoki parol noto'g'ri kiritildi." in res_uz.json()["non_field_errors"]

    # Ruscha
    res_ru = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "wrongpassword"},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="ru",
    )
    assert "Неверный логин или пароль." in res_ru.json()["non_field_errors"]

    # Inglizcha
    res_en = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "wrongpassword"},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="en",
    )
    assert "Invalid username or password." in res_en.json()["non_field_errors"]


# ==============================================================================
# 3. OQ-037 Rollar va Ruxsatlar Testlari (Dinamik va bir nechta rollar)
# ==============================================================================


@pytest.mark.django_db
def test_user_with_multiple_roles(test_users):
    """Foydalanuvchi bir vaqtning o'zida bir nechta rolga ega bo'lishi mumkin."""
    multi_user = test_users["multi"]
    assert multi_user.has_role("WAREHOUSE_MANAGER") is True
    assert multi_user.has_role("PRODUCTION_SUPERVISOR") is True
    assert multi_user.has_role("ADMIN") is False
    assert set(multi_user.role_codes) == {"WAREHOUSE_MANAGER", "PRODUCTION_SUPERVISOR"}

    # Ham ombor, ham ishlab chiqarish ruxsatlariga ega
    assert multi_user.is_warehouse_manager is True
    assert multi_user.is_production_supervisor is True


@pytest.mark.django_db
def test_admin_can_create_new_role(client, test_users):
    """OQ-037: Administrator yangi rol yaratishi va ruxsatlarini sozlashi mumkin."""
    client.login(username="admin_user", password="securepassword123")
    response = client.post(
        "/api/auth/roles/",
        data={
            "code": "QUALITY_CONTROLLER",
            "name": "Sifat nazoratchisi",
            "description": "Mahsulot va detallar sifatini tekshiruvchi mutaxassis",
            "permissions": ["view_quality", "approve_batch"],
        },
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Role.objects.filter(code="QUALITY_CONTROLLER").exists()
    created_role = Role.objects.get(code="QUALITY_CONTROLLER")
    assert "approve_batch" in created_role.permissions


@pytest.mark.django_db
def test_non_admin_cannot_create_role(client, test_users):
    """OQ-037: Administrator bo'lmagan foydalanuvchi yangi rol yarata olmaydi."""
    client.login(username="warehouse_user", password="securepassword123")
    response = client.post(
        "/api/auth/roles/",
        data={
            "code": "CUSTOM_ROLE",
            "name": "Yangi Rol",
        },
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_me_endpoint_returns_roles(client, test_users):
    """/api/auth/me/ foydalanuvchining barcha rollari va ruxsat kodlarini qaytarishi kerak."""
    client.login(username="multi_user", password="securepassword123")
    response = client.get("/api/auth/me/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert set(data["role_codes"]) == {"WAREHOUSE_MANAGER", "PRODUCTION_SUPERVISOR"}
    assert len(data["roles"]) == 2


@pytest.mark.django_db
def test_logout(client, test_users):
    """Tizimdan chiqish (logout) muvaffaqiyatli ishlashi kerak."""
    client.login(username="warehouse_user", password="securepassword123")
    response = client.post("/api/auth/logout/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Tizimdan muvaffaqiyatli chiqildi."


@pytest.mark.django_db
def test_role_permissions_classes(factory, test_users):
    """DRF permission klasslari (IsAdminRole, IsWarehouseManager) to'g'ri ishlashi kerak."""
    admin_perm = IsAdminRole()
    warehouse_perm = IsWarehouseManager()

    # Admin barcha ruxsatlardan o'tadi
    req = factory.get("/")
    req.user = test_users["admin"]
    assert admin_perm.has_permission(req, None) is True
    assert warehouse_perm.has_permission(req, None) is True

    # Omborchi ombordan o'tadi, admindan emas
    req.user = test_users["warehouse"]
    assert admin_perm.has_permission(req, None) is False
    assert warehouse_perm.has_permission(req, None) is True

    # Oddiy ishchi ikkalasidan ham o'tmaydi
    req.user = test_users["worker"]
    assert admin_perm.has_permission(req, None) is False
    assert warehouse_perm.has_permission(req, None) is False
