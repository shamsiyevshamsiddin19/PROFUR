from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.inventory.models import LeftoverOffcut
from apps.inventory.offcut_services import (
    OffcutDimensionError,
    OffcutUnitError,
    register_offcut,
    withdraw_offcut,
)

from .factories import make_admin, make_material


class OffcutRegistrationTest(TestCase):
    def setUp(self):
        self.user = make_admin()

    def test_register_sheet_offcut(self):
        mat = make_material(
            name="Sheet",
            unit="sheet",
            length_cm=Decimal("100"),
            width_cm=Decimal("200"),
        )
        offcut = register_offcut(
            material=mat,
            length_mm=Decimal("500"),
            width_mm=Decimal("300"),
            quantity=Decimal("2"),
            user=self.user,
        )
        self.assertEqual(offcut.quantity, Decimal("2"))
        self.assertEqual(offcut.length_mm, Decimal("500"))
        self.assertEqual(offcut.width_mm, Decimal("300"))

    def test_register_meter_offcut(self):
        mat = make_material(
            name="Meter Mat",
            unit="meter",
            length_cm=Decimal("500"),
        )
        offcut = register_offcut(
            material=mat,
            length_mm=Decimal("2000"),
            width_mm=None,
            quantity=Decimal("1"),
            user=self.user,
        )
        self.assertEqual(offcut.quantity, Decimal("1"))

    def test_reject_non_sheet_unit(self):
        mat = make_material(name="KG Offcut", unit="kg")
        with self.assertRaises(OffcutUnitError):
            register_offcut(
                material=mat,
                length_mm=Decimal("100"),
                width_mm=None,
                quantity=Decimal("1"),
                user=self.user,
            )

    def test_reject_oversized_offcut(self):
        mat = make_material(
            name="Small Sheet",
            unit="sheet",
            length_cm=Decimal("50"),
            width_cm=Decimal("50"),
        )
        with self.assertRaises(OffcutDimensionError):
            register_offcut(
                material=mat,
                length_mm=Decimal("600"),
                width_mm=Decimal("600"),
                quantity=Decimal("1"),
                user=self.user,
            )


class OffcutWithdrawalTest(TestCase):
    def setUp(self):
        self.user = make_admin()
        self.mat = make_material(
            name="W Sheet",
            unit="sheet",
            length_cm=Decimal("100"),
            width_cm=Decimal("200"),
        )
        self.offcut = register_offcut(
            material=self.mat,
            length_mm=Decimal("500"),
            width_mm=Decimal("300"),
            quantity=Decimal("5"),
            user=self.user,
        )

    def test_partial_withdrawal(self):
        withdraw_offcut(self.offcut.id, Decimal("2"), self.user)
        self.offcut.refresh_from_db()
        self.assertEqual(self.offcut.quantity, Decimal("3"))

    def test_full_withdrawal_preserves_history(self):
        withdraw_offcut(self.offcut.id, Decimal("5"), self.user)
        self.assertEqual(
            LeftoverOffcut.objects.get(pk=self.offcut.id).quantity, Decimal("0")
        )

    def test_over_withdrawal_fails(self):
        with self.assertRaises(ValidationError):
            withdraw_offcut(self.offcut.id, Decimal("10"), self.user)
