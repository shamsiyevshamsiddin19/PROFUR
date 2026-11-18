"""PCRM-39: katalog API'si shartnomaga mosligi (warehouse-api-v1.md, 3-bo'lim)."""

from decimal import Decimal

import pytest
from accounts.models import Role
from apps.catalog.models import Category, Material, Unit
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

CATEGORIES = "/api/v1/categories/"
MATERIALS = "/api/v1/materials/"


def make_user(username: str, *codes: str):
    """Shartnomadagi ruxsat kodlari berilgan alohida rolli foydalanuvchi (OQ-037)."""
    user = get_user_model().objects.create_user(username=username, password="x")
    if codes:
        role = Role.objects.create(
            code=f"TEST_{username.upper()}", name=username, permissions=list(codes)
        )
        user.roles.add(role)
    return user


def client_for(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def viewer() -> APIClient:
    """Ishlab chiqarish nazoratchisi: faqat ko'radi."""
    return client_for(make_user("viewer", "catalog.view_material"))


@pytest.fixture
def storekeeper() -> APIClient:
    """Ombor mas'uli: material qo'shadi va tahrirlaydi."""
    return client_for(
        make_user(
            "storekeeper",
            "catalog.view_material",
            "catalog.add_material",
            "catalog.change_material",
        )
    )


@pytest.fixture
def admin() -> APIClient:
    """Admin rolidagi ``*`` ruxsati hamma kodni qamraydi."""
    return client_for(make_user("admin", "*"))


@pytest.fixture
def ldsp() -> Category:
    """0002_initial_categories migratsiyasi yaratgan kategoriya."""
    return Category.objects.get(name="LDSP")


@pytest.fixture
def egger(ldsp) -> Material:
    return Material.objects.create(
        category=ldsp,
        name="LDSP Egger",
        color="oq",
        length_cm=Decimal("280.00"),
        width_cm=Decimal("207.00"),
        thickness_cm=Decimal("1.60"),
        unit=Unit.SHEET,
    )


def sheet_payload(category: Category, **overrides) -> dict:
    data = {
        "category_id": category.pk,
        "name": "LDSP Egger",
        "color": "oq",
        "length_cm": "280.00",
        "width_cm": "207.00",
        "thickness_cm": "1.60",
        "unit": "sheet",
    }
    data.update(overrides)
    return data


def error_codes(response, field: str) -> list[str]:
    return [error.code for error in response.data[field]]


# --- Kirish va ruxsatlar -------------------------------------------------------


def test_anonymous_request_is_rejected():
    response = APIClient().get(MATERIALS)

    # SessionAuthentication bilan 403 (shartnoma, 1-bo'lim xato jadvali).
    assert response.status_code == 403
    assert response.data["detail"].code == "not_authenticated"


def test_user_without_view_permission_is_rejected():
    client = client_for(make_user("nobody"))

    assert client.get(MATERIALS).status_code == 403
    assert client.get(CATEGORIES).status_code == 403


def test_viewer_can_read_but_not_write(viewer, ldsp):
    assert viewer.get(MATERIALS).status_code == 200
    assert viewer.post(MATERIALS, sheet_payload(ldsp)).status_code == 403
    assert viewer.post(CATEGORIES, {"name": "MDF"}).status_code == 403


def test_warehouse_role_name_alone_grants_nothing():
    """Rol nomi emas, uning ruxsat kodlari hisoblanadi."""
    role = Role.objects.create(
        code="WAREHOUSE_MANAGER", name="Ombor mas'uli", permissions=[]
    )
    user = make_user("named_only")
    user.roles.add(role)

    assert client_for(user).get(MATERIALS).status_code == 403


def test_permission_change_applies_to_next_request(ldsp):
    user = make_user("changing", "catalog.view_material")
    client = client_for(user)
    assert client.post(MATERIALS, sheet_payload(ldsp)).status_code == 403

    role = user.roles.get()
    role.permissions = [*role.permissions, "catalog.add_material"]
    role.save()

    assert client.post(MATERIALS, sheet_payload(ldsp)).status_code == 201


def test_storekeeper_cannot_manage_categories(storekeeper, ldsp):
    assert storekeeper.post(CATEGORIES, {"name": "MDF"}).status_code == 403
    response = storekeeper.patch(f"{CATEGORIES}{ldsp.pk}/", {"is_active": False})
    assert response.status_code == 403


# --- Kategoriyalar -------------------------------------------------------------


def test_category_list_has_material_count_and_filters(viewer, egger):
    Category.objects.create(name="MDF", is_active=False)

    response = viewer.get(CATEGORIES, {"is_active": "true", "search": "ld"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0] == {
        "id": egger.category_id,
        "name": "LDSP",
        "is_active": True,
        "material_count": 1,
    }


def test_admin_creates_and_deactivates_category(admin):
    created = admin.post(CATEGORIES, {"name": "MDF"})
    assert created.status_code == 201
    assert created.data["material_count"] == 0

    updated = admin.patch(f"{CATEGORIES}{created.data['id']}/", {"is_active": False})
    assert updated.status_code == 200
    assert updated.data["is_active"] is False


def test_duplicate_category_name_is_rejected(admin, ldsp):
    response = admin.post(CATEGORIES, {"name": "LDSP"})

    assert response.status_code == 400
    assert error_codes(response, "name") == ["unique"]


# --- Materiallar: o'qish -------------------------------------------------------


def test_material_detail_matches_contract(viewer, egger):
    response = viewer.get(f"{MATERIALS}{egger.pk}/")

    assert response.status_code == 200
    assert response.data == {
        "id": egger.pk,
        "category": {"id": egger.category_id, "name": "LDSP"},
        "name": "LDSP Egger",
        "color": "oq",
        "length_cm": "280.00",
        "width_cm": "207.00",
        "thickness_cm": "1.60",
        "unit": "sheet",
        "display_name": "LDSP Egger · oq · 280×207×1.6",
        "is_active": True,
        "quantity_on_hand": "0.00",
    }


def test_material_search_and_filters(viewer, egger, ldsp):
    glue_category = Category.objects.create(name="Kley")
    Material.objects.create(category=glue_category, name="PVA", unit=Unit.KG)
    Material.objects.create(
        category=ldsp, name="LDSP Kronospan", color="qora", unit=Unit.SHEET
    )

    def ids(**params):
        response = viewer.get(MATERIALS, params)
        assert response.status_code == 200
        return [item["id"] for item in response.data["results"]]

    assert ids(search="EGGER") == [egger.pk]
    assert ids(search="qora") != []  # rang bo'yicha ham qidiradi
    assert len(ids(category=ldsp.pk)) == 2
    assert len(ids(unit="kg")) == 1
    assert ids(is_active="false") == []


def test_bad_filter_values_return_400(viewer):
    assert viewer.get(MATERIALS, {"unit": "box"}).status_code == 400
    assert viewer.get(MATERIALS, {"category": "abc"}).status_code == 400
    assert viewer.get(MATERIALS, {"is_active": "maybe"}).status_code == 400


# --- Materiallar: yozish -------------------------------------------------------


def test_storekeeper_creates_material(storekeeper, ldsp):
    response = storekeeper.post(MATERIALS, sheet_payload(ldsp))

    assert response.status_code == 201
    assert response.data["category"] == {"id": ldsp.pk, "name": "LDSP"}
    assert Material.objects.filter(pk=response.data["id"]).exists()


def test_duplicate_material_returns_existing_id(storekeeper, egger):
    response = storekeeper.post(MATERIALS, sheet_payload(egger.category))

    assert response.status_code == 400
    assert error_codes(response, "non_field_errors") == ["material_duplicate"]
    assert response.data["existing_id"] == egger.pk
    assert Material.objects.count() == 1


def test_duplicate_without_dimensions_is_detected(storekeeper):
    glue = Category.objects.create(name="Kley")
    payload = {"category_id": glue.pk, "name": "PVA", "unit": "kg"}

    assert storekeeper.post(MATERIALS, payload).status_code == 201
    second = storekeeper.post(MATERIALS, payload)

    assert second.status_code == 400
    assert error_codes(second, "non_field_errors") == ["material_duplicate"]


def test_other_thickness_is_a_new_material(storekeeper, egger):
    payload = sheet_payload(egger.category, thickness_cm="1.80")

    assert storekeeper.post(MATERIALS, payload).status_code == 201


def test_inactive_category_is_rejected(storekeeper):
    archived = Category.objects.create(name="Eski", is_active=False)

    response = storekeeper.post(MATERIALS, sheet_payload(archived))

    assert response.status_code == 400
    assert error_codes(response, "category_id") == ["category_inactive"]


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("thickness_cm", "0", "min_value"),
        ("length_cm", "-5", "min_value"),
        ("width_cm", "1.555", "max_decimal_places"),
        ("unit", "box", "invalid_choice"),
        ("name", "", "blank"),
    ],
)
def test_invalid_material_fields(storekeeper, ldsp, field, value, code):
    response = storekeeper.post(MATERIALS, sheet_payload(ldsp, **{field: value}))

    assert response.status_code == 400
    assert error_codes(response, field) == [code]


def test_patch_renames_and_deactivates_material(storekeeper, egger):
    response = storekeeper.patch(
        f"{MATERIALS}{egger.pk}/", {"name": "LDSP Egger W980", "is_active": False}
    )

    assert response.status_code == 200
    egger.refresh_from_db()
    assert (egger.name, egger.is_active) == ("LDSP Egger W980", False)


def test_patch_into_duplicate_is_rejected(storekeeper, egger):
    other = Material.objects.create(
        category=egger.category,
        name="LDSP Egger",
        color="oq",
        length_cm=Decimal("280.00"),
        width_cm=Decimal("207.00"),
        thickness_cm=Decimal("1.80"),
        unit=Unit.SHEET,
    )

    response = storekeeper.patch(f"{MATERIALS}{other.pk}/", {"thickness_cm": "1.60"})

    assert response.status_code == 400
    assert response.data["existing_id"] == egger.pk


def test_patch_keeps_material_in_now_inactive_category(storekeeper, egger):
    Category.objects.filter(pk=egger.category_id).update(is_active=False)

    response = storekeeper.patch(f"{MATERIALS}{egger.pk}/", {"color": "kulrang"})

    assert response.status_code == 200


def test_delete_and_put_are_not_allowed(admin, egger):
    assert admin.delete(f"{MATERIALS}{egger.pk}/").status_code == 405
    assert admin.put(f"{MATERIALS}{egger.pk}/", {}).status_code == 405
    assert admin.delete(f"{CATEGORIES}{egger.category_id}/").status_code == 405
    assert Material.objects.filter(pk=egger.pk).exists()
