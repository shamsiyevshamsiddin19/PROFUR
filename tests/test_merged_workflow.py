"""Birlashtirilgan login, katalog va xarajat API'sining sessiya/CSRF sinovi."""

import pytest
from accounts.models import Role
from apps.expenses.admin import ExpenseAdmin, ExpenseTypeAdmin
from apps.expenses.models import Expense, ExpenseType
from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_session_login_and_both_api_routes_enforce_csrf_and_permissions():
    """Haqiqiy login sessiyasi ikkala include va aniq ruxsat kodlari bilan ishlaydi."""
    user = get_user_model().objects.create_user(
        username="integration", password="secret"
    )
    role = Role.objects.create(
        code="CUSTOM", name="Sinov", permissions=["catalog.view_material"]
    )
    user.roles.add(role)
    client = APIClient(enforce_csrf_checks=True)
    token = client.get("/api/auth/csrf/").data["csrfToken"]
    assert (
        client.post(
            "/api/auth/login/",
            {"username": "integration", "password": "secret"},
            format="json",
            HTTP_X_CSRFTOKEN=token,
        ).status_code
        == 200
    )
    assert client.get("/api/v1/materials/").status_code == 200
    assert client.get("/api/v1/expenses/").status_code == 403
    role.permissions += ["expenses.view_expense", "expenses.add_expense"]
    role.save()
    assert client.get("/api/v1/expenses/").status_code == 200
    payload = {"expense_type": "tax", "amount": "12.50", "spent_on": "2026-11-18"}
    assert client.post("/api/v1/expenses/", payload, format="json").status_code == 403
    fresh = client.get("/api/auth/csrf/").data["csrfToken"]
    response = client.post(
        "/api/v1/expenses/",
        payload,
        format="json",
        HTTP_X_CSRFTOKEN=fresh,
    )
    assert response.status_code == 201
    assert response.data["created_by"] == user.pk
    assert response.data["currency"] == "USD"
    assert response.data["amount"] == "12.50"
    role.permissions.remove("expenses.add_expense")
    role.save()
    assert (
        client.post(
            "/api/v1/expenses/",
            payload,
            format="json",
            HTTP_X_CSRFTOKEN=fresh,
        ).status_code
        == 403
    )
    assert Expense.objects.count() == 1


def test_expense_admin_preserves_api_only_creation_and_immutable_type_code():
    """Admin orqali muallifni chetlab o'tish va tur kodini almashtirish yopilgan."""
    expense_admin = ExpenseAdmin(Expense, admin.site)
    assert not expense_admin.has_add_permission(None)
    assert not expense_admin.has_change_permission(None)
    assert not expense_admin.has_delete_permission(None)
    type_admin = ExpenseTypeAdmin(ExpenseType, admin.site)
    assert "code" in type_admin.get_readonly_fields(None, ExpenseType(code="tax"))
    assert "code" not in type_admin.get_readonly_fields(None)
