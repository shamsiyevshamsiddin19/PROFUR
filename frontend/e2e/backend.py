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
        code="BROWSER_STOREKEEPER",
        name="Browser storekeeper",
        permissions=[
            "catalog.view_material",
            "inventory.view_stock",
            "inventory.add_receipt",
            "inventory.view_purchase_price",
        ],
    )
    user.roles.add(role)
    category = Category.objects.get(name="LMDF")
    Material.objects.create(name="Browser MDF", category=category, unit=Unit.SHEET)
    Material.objects.create(
        name="Akril panel yuqori zichlikdagi namlikka chidamli maxsus qoplama 2800x1220x18mm",
        category=category,
        unit=Unit.SHEET,
    )
    call_command("runserver", "127.0.0.1:18110", use_reloader=False)
