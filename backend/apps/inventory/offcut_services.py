"""Qoldiq materiallar bo'yicha xizmatlar: qayd etish va ishlatish."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import OFFCUT_UNITS, LeftoverOffcut, StockIssue, WarehouseReview


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
def register_offcut(
    material, length_mm, width_mm, quantity, user, note="", source_issue=None
):
    """Register a reusable leftover piece from cutting."""
    if material.unit not in OFFCUT_UNITS:
        raise OffcutUnitError(material.unit)

    if material.unit == "sheet" and width_mm is None:
        raise OffcutDimensionError(_("List bo‘lagi uchun eni majburiy."))
    if material.unit == "meter" and width_mm is not None:
        raise OffcutDimensionError(
            _("Metr bilan o‘lchanadigan bo‘lak uchun uzunlikni kiriting.")
        )
    _validate_offcut_dimensions(material, length_mm, width_mm)
    if source_issue is not None:
        source_issue = StockIssue.objects.select_for_update().get(pk=source_issue.pk)
        check_source(source_issue, material, length_mm, width_mm, quantity)

    offcut = LeftoverOffcut.objects.create(
        material=material,
        length_mm=length_mm,
        width_mm=width_mm,
        quantity=quantity,
        note=note,
        registered_by=user,
        source_issue=source_issue,
    )
    record_offcut(offcut, WarehouseReview.Kind.OFFCUT_ADD, quantity, user, note)
    return offcut


@transaction.atomic
def withdraw_offcut(offcut_id, quantity, user, reason=""):
    """Withdraw (use) an offcut. Keeps exhausted pieces linked to the history."""
    offcut = LeftoverOffcut.objects.select_for_update().get(pk=offcut_id)

    if quantity <= 0 or quantity > offcut.quantity:
        raise ValidationError(_("Qoldiq bo‘laklar yetarli emas."))

    offcut.quantity -= quantity
    offcut.save(update_fields=["quantity"])
    record_offcut(offcut, WarehouseReview.Kind.OFFCUT_USE, quantity, user, reason)
    return offcut


def record_offcut(offcut, kind, quantity, actor, note, **extra):
    return WarehouseReview.objects.create(
        kind=kind,
        material=offcut.material,
        issue=offcut.source_issue,
        offcut=offcut,
        quantity=quantity,
        actor=actor,
        note=note,
        **extra,
    )


def source_measure(material):
    if material.unit == "meter":
        return 1000
    return (
        material.length_cm * material.width_cm * 100
        if (material.length_cm and material.width_cm)
        else None
    )


def registered_measure(issue):
    rows = WarehouseReview.objects.filter(
        issue=issue, kind=WarehouseReview.Kind.OFFCUT_ADD, correction__isnull=True
    ).select_related("offcut")
    return sum(
        row.quantity * row.offcut.length_mm * (row.offcut.width_mm or 1) for row in rows
    )


def check_source(issue, material, length, width, quantity):
    from .services import returnable_by_batch

    if issue.material_id != material.pk:
        raise OffcutDimensionError(_("Bo‘lak asl chiqim materialiga mos kelmadi."))
    measure = source_measure(material)
    if measure is None:
        raise OffcutDimensionError(
            _("Avval listning eni va uzunligi katalogda bo‘lishi kerak.")
        )
    available = sum(returnable_by_batch(issue, include_pending=True).values()) * measure
    if registered_measure(issue) + length * (width or 1) * quantity > available:
        raise OffcutDimensionError(
            _("Kesilgan bo‘laklar asl chiqim o‘lchamidan oshib ketdi.")
        )


@transaction.atomic
def correct_offcut(review_id, actor, reason):
    review = WarehouseReview.objects.select_for_update().get(pk=review_id)
    if review.kind not in (
        WarehouseReview.Kind.OFFCUT_ADD,
        WarehouseReview.Kind.OFFCUT_USE,
    ):
        raise ValidationError(_("Bu yozuv kesilgan qoldiq amali emas."))
    if previous := WarehouseReview.objects.filter(correction_of=review).first():
        return previous
    if review.issue_id:
        StockIssue.objects.select_for_update().get(pk=review.issue_id)
    offcut = LeftoverOffcut.objects.select_for_update().get(pk=review.offcut_id)
    if review.kind == WarehouseReview.Kind.OFFCUT_ADD:
        if offcut.quantity < review.quantity:
            raise ValidationError(
                _("Bo‘lak ishlatilgan. Avval ishlatish yozuvini tuzating.")
            )
        quantity = -review.quantity
    else:
        quantity = review.quantity
    offcut.quantity += quantity
    offcut.save(update_fields=["quantity"])
    return record_offcut(
        offcut,
        WarehouseReview.Kind.OFFCUT_CORRECTION,
        quantity,
        actor,
        reason,
        state=WarehouseReview.State.REVIEWED,
        correction_of=review,
        reviewer=actor,
        reviewed_at=timezone.now(),
    )
