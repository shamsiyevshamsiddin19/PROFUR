"""Mobil sinov uchun alohida vaqtinchalik baza va Django serveri."""

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
from django.conf import settings  # noqa: E402

with TemporaryDirectory(prefix="profur-browser-") as temporary:
    # Sinov bazasi foydalanuvchining lokal yoki server bazasidan mustaqil.
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(Path(temporary) / "browser.sqlite3"),
        }
    }
    settings.ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    settings.CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:15173"]
    django.setup()

    from accounts.models import Role
    from apps.catalog.models import Category, Material, Unit
    from django.contrib.auth import get_user_model
    from django.core.management import call_command

    call_command("migrate", verbosity=0)
    user = get_user_model().objects.create_user(
        username="browser_storekeeper", password="browser-test-only-password"
    )
    role = Role.objects.create(
        code="ADMIN",
        name="Browser storekeeper",
        permissions=[
            "catalog.view_material",
            "inventory.view_stock",
            "inventory.add_receipt",
            "inventory.view_purchase_price",
        ],
    )
    user.roles.add(role)
    # These accounts exist only in this temporary test database.
    for code, permissions in {
        "warehouse": [
            "catalog.view_material",
            "inventory.view_stock",
            "inventory.view_purchase_price",
            "inventory.add_receipt",
            "inventory.add_issue",
            "inventory.add_return",
            "inventory.approve_return",
            "inventory.add_write_off",
            "inventory.approve_write_off",
            "inventory.change_min_quantity",
        ],
        "procurement": [
            "catalog.view_material",
            "catalog.add_material",
            "catalog.change_material",
            "catalog.add_category",
            "inventory.view_stock",
            "inventory.add_receipt",
        ],
        "production": [
            "catalog.view_material",
            "inventory.view_stock",
            "inventory.add_issue",
            "inventory.add_return",
        ],
        "accountant": [
            "catalog.view_material",
            "inventory.view_stock",
            "inventory.view_purchase_price",
            "expenses.reverse_expense",
            "expenses.view_expense",
            "expenses.view_expensetype",
            "expenses.add_expense",
        ],
        "worker": [],
    }.items():
        scoped_role = Role.objects.create(
            code="E2E_" + code.upper(), name=code, permissions=permissions
        )
        scoped_user = get_user_model().objects.create_user(
            username="browser_" + code, password="browser-test-only-password"
        )
        scoped_user.roles.add(scoped_role)
    category = Category.objects.get(name="LMDF")
    Material.objects.create(name="Browser MDF", category=category, unit=Unit.SHEET)
    Material.objects.create(
        name="Akril panel yuqori zichlikdagi namlikka chidamli maxsus qoplama 2800x1220x18mm",
        category=category,
        unit=Unit.SHEET,
    )
    Material.objects.bulk_create(
        [
            Material(
                name=f"A paged material {i:02}", category=category, unit=Unit.SHEET
            )
            for i in range(25)
        ]
    )
    call_command("runserver", "127.0.0.1:18110", use_reloader=False)
