"""Namuna omborini to‘ldirish mavjud hisob va qoldiqlarni buzmasligi kerak."""

from io import StringIO

import pytest
from accounts.models import Role, User
from apps.inventory.models import Batch
from django.core.management import call_command
from django.core.management.base import CommandError

pytestmark = pytest.mark.django_db


def test_clear_is_rejected_before_any_data_is_written():
    with pytest.raises(CommandError, match="--clear"):
        call_command("seed_real_warehouse", clear=True, stdout=StringIO())
    assert not User.objects.exists()
    assert not Batch.objects.exists()


def test_seed_preserves_existing_accounts_and_rejects_stock_duplication():
    role = Role.objects.create(code="EXISTING", name="Existing", permissions=[])
    identities = {}
    for name in ["admin", "omborchi", "usta", "hisobchi", "taminotchi"]:
        user = User.objects.create_user(
            username=name, password="Existing-identity-2026"
        )
        user.roles.add(role)
        identities[name] = user.password
    call_command("seed_real_warehouse", stdout=StringIO())
    for name, password in identities.items():
        user = User.objects.get(username=name)
        assert user.password == password
        assert list(user.roles.values_list("code", flat=True)) == ["EXISTING"]
        assert not user.is_superuser
    count = Batch.objects.count()
    assert count > 0
    with pytest.raises(CommandError, match="yozuvlar mavjud"):
        call_command("seed_real_warehouse", stdout=StringIO())
    assert Batch.objects.count() == count
