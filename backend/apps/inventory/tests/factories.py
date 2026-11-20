from decimal import Decimal
from django.contrib.auth import get_user_model
from accounts.models import Role
from apps.catalog.models import Category, Material

User = get_user_model()


def make_role(code="WORKER", name=None, permissions=None):
    role, _ = Role.objects.get_or_create(
        code=code,
        defaults={
            "name": name or code.title(),
            "permissions": permissions or ["inventory.view_stock"],
        },
    )
    return role


def make_admin():
    admin_role = make_role("ADMIN", "Administrator", ["*"])
    user = User.objects.create_user(
        username="admin_test",
        password="testpass123",
        is_approved=True,
    )
    user.roles.add(admin_role)
    return user


def make_user(username="worker1", role_code="WORKER", approved=True):
    role = make_role(role_code)
    user = User.objects.create_user(
        username=username,
        password="testpass123",
        is_approved=approved,
    )
    user.roles.add(role)
    return user


def make_category(name="Test Category"):
    cat, _ = Category.objects.get_or_create(name=name)
    return cat


def make_material(name="Test Material", unit="sheet", category=None, **kwargs):
    cat = category or make_category()
    mat, _ = Material.objects.get_or_create(
        name=name,
        category=cat,
        defaults={"unit": unit, **kwargs},
    )
    return mat


def stock_up(material, quantity, price, user):
    """Create a batch (kirim) for a material."""
    from apps.inventory.services import receive
    from datetime import date
    batch, balance = receive(
        material=material,
        received_on=date.today(),
        quantity=Decimal(str(quantity)),
        total_amount=Decimal(str(price)),
        user=user,
        currency="USD",
    )
    return batch, balance
