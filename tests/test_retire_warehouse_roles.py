"""Check that role cleanup affects only the intended, unused roles."""

import pytest
from accounts.models import Role, User
from django.core.management import call_command
from django.core.management.base import CommandError

pytestmark = pytest.mark.django_db


def test_cleanup_removes_only_unused_retired_roles():
    retired = ("PRODUCTION_SUPERVISOR", "ACCOUNTANT", "PROCUREMENT")
    for code in (*retired, "ADMIN", "WAREHOUSE_MANAGER", "WORKER"):
        Role.objects.create(code=code, name=code, is_system=True)

    call_command("retire_warehouse_roles")
    assert Role.objects.filter(code__in=retired).count() == 3

    call_command("retire_warehouse_roles", apply=True)
    call_command("retire_warehouse_roles", apply=True)
    assert set(Role.objects.values_list("code", flat=True)) == {
        "ADMIN",
        "WAREHOUSE_MANAGER",
        "WORKER",
    }


def test_assigned_role_blocks_all_deletions():
    assigned = Role.objects.create(code="ACCOUNTANT", name="Accountant")
    unused = Role.objects.create(code="PROCUREMENT", name="Procurement")
    User.objects.create_user(username="operator").roles.add(assigned)

    with pytest.raises(CommandError, match="ACCOUNTANT"):
        call_command("retire_warehouse_roles", apply=True)

    assert Role.objects.filter(pk__in=[assigned.pk, unused.pk]).count() == 2
