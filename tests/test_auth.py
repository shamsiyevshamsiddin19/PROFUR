"""Foydalanuvchi autentifikatsiyasi va ruxsatlarini tekshiruvchi testlar."""

import pytest
from accounts.models import UserRole
from accounts.permissions import IsAdminRole, IsWarehouseManager
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from rest_framework import status

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def test_users(db):
    admin_user = User.objects.create_user(
        username="admin_user",
        password="securepassword123",
        role=UserRole.ADMIN,
        first_name="Ali",
        last_name="Valiyev",
    )
    warehouse_user = User.objects.create_user(
        username="warehouse_user",
        password="securepassword123",
        role=UserRole.WAREHOUSE_MANAGER,
        first_name="Hasan",
        last_name="Husanov",
    )
    worker_user = User.objects.create_user(
        username="worker_user",
        password="securepassword123",
        role=UserRole.WORKER,
        first_name="Botir",
        last_name="Sobirov",
    )
    return {
        "admin": admin_user,
        "warehouse": warehouse_user,
        "worker": worker_user,
    }


@pytest.mark.django_db
def test_csrf_token_endpoint(client):
    """CSRF token olish API'si 200 qaytarishi va token berishi kerak."""
    response = client.get("/api/auth/csrf/")
    assert response.status_code == status.HTTP_200_OK
    assert "csrfToken" in response.json()


@pytest.mark.django_db
def test_login_success(client, test_users):
    """To'g'ri login va parol bilan kirilganda 200 va foydalanuvchi ma'lumoti qaytishi kerak."""
    response = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "securepassword123"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Tizimga muvaffaqiyatli kirildi."
    assert data["user"]["username"] == "warehouse_user"
    assert data["user"]["role"] == UserRole.WAREHOUSE_MANAGER
    assert data["user"]["role_display"] == "Ombor mas'uli"


@pytest.mark.django_db
def test_login_invalid_credentials(client, test_users):
    """Noto'g'ri parol kiritilganda 400 qaytishi kerak."""
    response = client.post(
        "/api/auth/login/",
        data={"username": "warehouse_user", "password": "wrongpassword"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.json()


@pytest.mark.django_db
def test_me_authenticated(client, test_users):
    """Tizimga kirgan foydalanuvchi /api/auth/me/ orqali o'z profilini olishi kerak."""
    client.login(username="admin_user", password="securepassword123")
    response = client.get("/api/auth/me/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "admin_user"
    assert data["role"] == UserRole.ADMIN


@pytest.mark.django_db
def test_me_unauthenticated(client):
    """Tizimga kirmagan so'rov /api/auth/me/ ga kirganda 403 yoki 401 olishi kerak."""
    response = client.get("/api/auth/me/")
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.django_db
def test_logout(client, test_users):
    """Tizimdan chiqish (logout) muvaffaqiyatli ishlashi kerak."""
    client.login(username="warehouse_user", password="securepassword123")
    response = client.post("/api/auth/logout/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Tizimdan muvaffaqiyatli chiqildi."

    # Chiqilgandan keyin profilga kirish bloklanishi kerak
    me_response = client.get("/api/auth/me/")
    assert me_response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.django_db
def test_role_permissions(factory, test_users):
    """Ruxsatlar (IsAdminRole, IsWarehouseManager) to'g'ri tekshirilishi kerak."""
    admin_perm = IsAdminRole()
    warehouse_perm = IsWarehouseManager()

    # Admin foydalanuvchi barcha ruxsatlardan o'tishi kerak
    req = factory.get("/")
    req.user = test_users["admin"]
    assert admin_perm.has_permission(req, None) is True
    assert warehouse_perm.has_permission(req, None) is True

    # Ombor mas'uli faqat ombor ruxsatidan o'tadi, admin ruxsatidan emas
    req.user = test_users["warehouse"]
    assert admin_perm.has_permission(req, None) is False
    assert warehouse_perm.has_permission(req, None) is True

    # Oddiy ishchi ombor ruxsatidan ham, admin ruxsatidan ham o'tmaydi
    req.user = test_users["worker"]
    assert admin_perm.has_permission(req, None) is False
    assert warehouse_perm.has_permission(req, None) is False
