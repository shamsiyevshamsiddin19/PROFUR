"""Qoldiq materiallar bo'yicha xizmatlar: qayd etish va ishlatish."""

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventory.models import OFFCUT_UNITS, LeftoverOffcut


class OffcutDimensionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class OffcutUnitError(Exception):
    def __init__(self, unit):
        self.message = (
            f"Material unit '{unit}' does not support offcuts. Allowed: {OFFCUT_UNITS}"
        )
        super().__init__(self.message)


def _validate_offcut_dimensions(material, length_mm, width_mm):
    """Validate offcut dimensions against parent sheet size."""
    mat_length = material.length_cm * 10 if material.length_cm else None
    mat_width = material.width_cm * 10 if material.width_cm else None

    if mat_length and mat_width:
        # Check both orientations (normal and rotated)
        fits_normal = length_mm <= mat_length and (
            width_mm is None or width_mm <= mat_width
        )
        fits_rotated = length_mm <= mat_width and (
            width_mm is None or width_mm <= mat_length
        )
        if not fits_normal and not fits_rotated:
            raise OffcutDimensionError(
                f"Offcut {length_mm}×{width_mm}mm exceeds parent sheet "
                f"{mat_length}×{mat_width}mm in both orientations."
            )
    elif mat_length:
        if length_mm > mat_length:
            raise OffcutDimensionError(
                f"Offcut length {length_mm}mm exceeds material length {mat_length}mm."
            )


@transaction.atomic
def register_offcut(material, length_mm, width_mm, quantity, user, note=""):
    """Register a reusable leftover piece from cutting."""
    if material.unit not in OFFCUT_UNITS:
        raise OffcutUnitError(material.unit)

    _validate_offcut_dimensions(material, length_mm, width_mm)

    offcut = LeftoverOffcut.objects.create(
        material=material,
        length_mm=length_mm,
        width_mm=width_mm,
        quantity=quantity,
        note=note,
        registered_by=user,
    )
    return offcut


@transaction.atomic
def withdraw_offcut(offcut_id, quantity, user, reason=""):
    """Withdraw (use) an offcut. Decrements quantity or deletes if fully used."""
    offcut = LeftoverOffcut.objects.select_for_update().get(pk=offcut_id)

    if quantity > offcut.quantity:
        raise ValidationError(
            f"Requested {quantity} but only {offcut.quantity} available."
        )

    if quantity == offcut.quantity:
        offcut.delete()
    else:
        offcut.quantity -= quantity
        offcut.save(update_fields=["quantity"])

    return offcut
