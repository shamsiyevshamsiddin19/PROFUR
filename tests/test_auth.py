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


@pytest.mark.django_db
def test_custom_role_can_receive_and_lose_warehouse_permission(factory):
    role = Role.objects.create(
        code="CUSTOM_STORE", name="Yordamchi", permissions=["manage_inventory"]
    )
    user = User.objects.create_user(username="custom_store")
    user.roles.add(role)
    request = factory.get("/")
    request.user = user
    gate = IsWarehouseManager()
    assert gate.has_permission(request, None) is True
    role.permissions = []
    role.save(update_fields=["permissions"])
    assert gate.has_permission(request, None) is False


@pytest.mark.django_db
def test_warehouse_name_without_permission_does_not_grant_access(factory):
    role = Role.objects.create(
        code="WAREHOUSE_MANAGER", name="Omborchi", permissions=[]
    )
    user = User.objects.create_user(username="empty_warehouse")
    user.roles.add(role)
    request = factory.get("/")
    request.user = user
    assert IsWarehouseManager().has_permission(request, None) is False


@pytest.mark.django_db
def test_view_permission_code_is_checked(factory):
    from accounts.permissions import HasPermissionCode

    role = Role.objects.create(
        code="RECEIVING", name="Kirimchi", permissions=["inventory.add_receipt"]
    )
    user = User.objects.create_user(username="receiving")
    user.roles.add(role)
    request = factory.get("/")
    request.user = user

    class ReceiptView:
        required_permission = "inventory.add_receipt"

    class IssueView:
        required_permission = "inventory.add_issue"

    gate = HasPermissionCode()
    assert gate.has_permission(request, ReceiptView()) is True
    assert gate.has_permission(request, IssueView()) is False
    assert gate.has_permission(request, None) is False


# ==============================================================================
# 4. Admin Foydalanuvchi Boshqaruvi Testlari (OQ-040)
# ==============================================================================


@pytest.mark.django_db
def test_admin_can_create_user(client, test_users, default_roles):
    """Admin yangi foydalanuvchi yaratishi va unga rol biriktirishi mumkin (OQ-040)."""
    client.login(username="admin_user", password="securepassword123")
    response = client.post(
        "/api/auth/users/",
        data={
            "username": "omborchi_sardor",
            "password": "Password123!",
            "first_name": "Sardor",
            "last_name": "Rahimov",
            "email": "sardor@profur.uz",
            "phone": "+998901112233",
            "role_ids": [default_roles["warehouse"].id],
            "is_active": True,
        },
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "omborchi_sardor"
    assert "WAREHOUSE_MANAGER" in data["role_codes"]
    assert "password" not in data

    # Yangi yaratilgan foydalanuvchi tizimga kira olishini tekshiramiz
    login_client = Client()
    login_res = login_client.post(
        "/api/auth/login/",
        data={"username": "omborchi_sardor", "password": "Password123!"},
        content_type="application/json",
    )
    assert login_res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_non_admin_cannot_create_user(client, test_users):
    """Admin bo'lmagan foydalanuvchi yangi hisob yarata olmaydi (403)."""
    client.login(username="warehouse_user", password="securepassword123")
    response = client.post(
        "/api/auth/users/",
        data={"username": "hacker", "password": "Password123!"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_list_and_search_users(client, test_users):
    """Admin foydalanuvchilar ro'yxatini ko'rishi va qidirishi mumkin."""
    client.login(username="admin_user", password="securepassword123")
    response = client.get("/api/auth/users/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    items = data["results"] if isinstance(data, dict) and "results" in data else data
    assert len(items) >= 4

    # Qidiruv
    search_res = client.get("/api/auth/users/?search=Hasan")
    assert search_res.status_code == status.HTTP_200_OK
    search_data = search_res.json()
    results = (
        search_data["results"]
        if isinstance(search_data, dict) and "results" in search_data
        else search_data
    )
    assert len(results) == 1
    assert results[0]["username"] == "warehouse_user"


@pytest.mark.django_db
def test_admin_can_update_user_and_change_roles(client, test_users, default_roles):
    """Admin foydalanuvchi ma'lumotlarini va rollarini o'zgartira oladi."""
    client.login(username="admin_user", password="securepassword123")
    worker = test_users["worker"]
    response = client.patch(
        f"/api/auth/users/{worker.id}/",
        data={
            "first_name": "Botirbek",
            "role_ids": [default_roles["supervisor"].id],
        },
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Botirbek"
    assert "PRODUCTION_SUPERVISOR" in data["role_codes"]


@pytest.mark.django_db
def test_user_cannot_be_deleted_only_deactivated(client, test_users):
    """OQ-040: Akkaunt o'chirilmaydi (DELETE 405), faolsizlantiriladi."""
    client.login(username="admin_user", password="securepassword123")
    worker = test_users["worker"]

    # DELETE so'rovi 405 berishi shart
    delete_res = client.delete(f"/api/auth/users/{worker.id}/")
    assert delete_res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # Faolsizlantirish (Deactivate)
    deact_res = client.post(f"/api/auth/users/{worker.id}/deactivate/")
    assert deact_res.status_code == status.HTTP_200_OK
    assert deact_res.json()["user"]["is_active"] is False

    worker.refresh_from_db()
    assert worker.is_active is False

    # Faolsizlangan hisob login qila olmasligi kerak
    worker_client = Client()
    login_res = worker_client.post(
        "/api/auth/login/",
        data={"username": "worker_user", "password": "securepassword123"},
        content_type="application/json",
    )
    assert login_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ushbu hisob faolsizlantirilgan." in login_res.json()["non_field_errors"]


@pytest.mark.django_db
def test_admin_can_reset_user_password(client, test_users):
    """Admin foydalanuvchi parolini tiklashi mumkin (OQ-040)."""
    client.login(username="admin_user", password="securepassword123")
    worker = test_users["worker"]

    response = client.post(
        f"/api/auth/users/{worker.id}/reset-password/",
        data={"new_password": "BrandNewSecretPassword999!"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Parol muvaffaqiyatli yangilandi."

    # Yangi parol bilan kirish muvaffaqiyatli
    worker_client = Client()
    login_res = worker_client.post(
        "/api/auth/login/",
        data={"username": "worker_user", "password": "BrandNewSecretPassword999!"},
        content_type="application/json",
    )
    assert login_res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_empty_admin_role_name_does_not_grant_authority(factory):
    """Rol nomining o'zi ('ADMIN') ruxsat bermasligi kerak (Rol nomining o'zi vakolat bermasin)."""
    empty_admin_role = Role.objects.create(
        code="ADMIN_EMPTY", name="Empty Admin", permissions=[]
    )
    user = User.objects.create_user(username="fake_admin")
    user.roles.add(empty_admin_role)

    req = factory.get("/")
    req.user = user
    assert IsAdminRole().has_permission(req, None) is False
    assert user.has_permission_code("catalog.view_material") is False


@pytest.mark.django_db
def test_unrecognized_prefix_mask_does_not_grant_permissions(factory):
    """Shartnomada yo‘q prefiks maskasi aniq ruxsat kodlarini o‘zidan bermaydi."""
    catalog_admin_role = Role.objects.create(
        code="CATALOG_ADMIN", name="Katalogchi", permissions=["catalog.*"]
    )
    user = User.objects.create_user(username="catalog_admin")
    user.roles.add(catalog_admin_role)

    assert user.has_permission_code("catalog.view_material") is False
    assert user.has_permission_code("catalog.add_category") is False
    assert user.has_permission_code("catalog.change_material") is False
    assert user.has_permission_code("inventory.add_receipt") is False


@pytest.mark.django_db
def test_me_exposes_superuser_for_frontend_without_allowing_escalation(client):
    """Superuser rol ro'yxatisiz ham UI'ga kiradi; bayroq so'rovdan yozilmaydi."""
    from accounts.serializers import UserSerializer

    user = User.objects.create_superuser(username="root_ui", password=None)
    client.force_login(user)
    response = client.get("/api/auth/me/")
    assert response.status_code == 200
    assert response.json()["is_superuser"] is True
    assert response.json()["roles"] == []
    ordinary = User.objects.create_user(username="ordinary_ui")
    serializer = UserSerializer(ordinary, data={"is_superuser": True}, partial=True)
    assert serializer.is_valid(), serializer.errors
    serializer.save()
    ordinary.refresh_from_db()
    assert ordinary.is_superuser is False


@pytest.mark.django_db
@pytest.mark.parametrize("password", ["abcdef", "1234567890", "password"])
def test_admin_user_writes_enforce_configured_password_validators(
    client, test_users, password
):
    """Yaratish va tiklash sozlamadagi kuchli parol siyosatini chetlab o‘tmaydi."""
    client.force_login(test_users["admin"])
    count = User.objects.count()
    created = client.post(
        "/api/auth/users/",
        {"username": "policy_user", "password": password},
        content_type="application/json",
    )
    assert created.status_code == 400
    assert "password" in created.json()
    assert User.objects.count() == count
    target = test_users["worker"]
    old_hash = target.password
    reset = client.post(
        f"/api/auth/users/{target.pk}/reset-password/",
        {"new_password": password},
        content_type="application/json",
    )
    assert reset.status_code == 400
    target.refresh_from_db()
    assert target.password == old_hash


@pytest.mark.django_db
def test_user_create_rolls_back_if_role_assignment_fails(
    client, test_users, default_roles, monkeypatch
):
    """Rol yozishda xato bo‘lsa yarimta akkaunt bazada qolmaydi."""
    client.force_login(test_users["admin"])

    def failed_assignment(*args, **kwargs):
        raise RuntimeError("role assignment failed")

    monkeypatch.setattr(User.roles.related_manager_cls, "set", failed_assignment)
    with pytest.raises(RuntimeError, match="role assignment failed"):
        client.post(
            "/api/auth/users/",
            {
                "username": "rollback_user",
                "password": "StrongRollbackPass984!",
                "role_ids": [default_roles["worker"].pk],
            },
            content_type="application/json",
        )
    assert not User.objects.filter(username="rollback_user").exists()


@pytest.mark.django_db
def test_admin_cannot_lock_self_out_or_remove_system_role(client, test_users):
    client.login(username="admin_user", password="securepassword123")
    admin = User.objects.get(username="admin_user")
    admin_role = admin.roles.get(code="ADMIN")
    for method, path, data in [
        ("patch", f"/api/auth/users/{admin.pk}/", {"is_active": False}),
        ("patch", f"/api/auth/users/{admin.pk}/", {"role_ids": []}),
        ("post", f"/api/auth/users/{admin.pk}/deactivate/", {}),
        ("patch", f"/api/auth/roles/{admin_role.pk}/", {"code": "RENAMED"}),
        ("delete", f"/api/auth/roles/{admin_role.pk}/", {}),
    ]:
        result = getattr(client, method)(
            path, data=data, content_type="application/json"
        )
        assert result.status_code == 400, result.content
    admin.refresh_from_db()
    assert admin.is_active and admin.has_role("ADMIN")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid", [{"x": "inventory.view_stock"}, [""], "inventory.view_stock"]
)
def test_role_permissions_must_be_string_list(client, test_users, invalid):
    client.login(username="admin_user", password="securepassword123")
    response = client.post(
        "/api/auth/roles/",
        data={"code": "BAD_PERMS", "name": "Bad", "permissions": invalid},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert not Role.objects.filter(code="BAD_PERMS").exists()
