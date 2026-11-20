"""Material visibility shared by catalogue, inventory and reports."""

from django.db import connection
from django.db.models import Q

from .models import Material


def is_shop_worker(user):
    """Identify worker accounts, including newly configured job roles."""
    if user.is_admin_role:
        return False
    return any(
        role.code == "WORKER" or "inventory.worker" in role.permissions
        for role in user.roles.all()
    )


def visible_materials(user):
    materials = Material.objects.all()
    if user.is_admin_role:
        return materials
    roles = set(user.role_codes)
    visible = Q(allowed_roles=[])
    if connection.features.supports_json_field_contains:
        for code in roles:
            visible |= Q(allowed_roles__contains=[code])
    elif roles:
        restricted = materials.exclude(allowed_roles=[]).values_list(
            "pk", "allowed_roles"
        )
        visible |= Q(
            pk__in=[
                pk
                for pk, allowed in restricted.iterator()
                if roles.intersection(allowed)
            ]
        )
    return materials.filter(visible)
