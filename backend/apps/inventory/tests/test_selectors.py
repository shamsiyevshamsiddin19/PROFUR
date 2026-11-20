from decimal import Decimal
from datetime import date
from django.test import TestCase

from apps.inventory.selectors import (
    warehouse_valuation,
    low_stock_materials,
    weighted_average_price,
)
from apps.inventory.services import receive, set_min_quantity
from .factories import make_admin, make_material


class ValuationTest(TestCase):
    def setUp(self):
        self.user = make_admin()

    def test_empty_warehouse(self):
        self.assertEqual(warehouse_valuation(), Decimal("0"))

    def test_single_batch_valuation(self):
        mat = make_material(name="Val Mat", unit="kg")
        receive(
            material=mat,
            received_on=date.today(),
            quantity=Decimal("10"),
            total_amount=Decimal("100"),
            user=self.user,
            currency="USD",
        )
        # valuation = quantity_remaining * unit_price = 10 * 10.000000 = 100.00
        self.assertEqual(warehouse_valuation(), Decimal("100.00"))

    def test_weighted_average_price(self):
        mat = make_material(name="Avg Mat", unit="kg")
        receive(
            material=mat, received_on=date.today(),
            quantity=Decimal("10"), total_amount=Decimal("100"),
            user=self.user, currency="USD",
        )
        receive(
            material=mat, received_on=date.today(),
            quantity=Decimal("10"), total_amount=Decimal("200"),
            user=self.user, currency="USD",
        )
        # (10 * 10 + 10 * 20) / (10 + 10) = 300 / 20 = 15.000000
        avg = weighted_average_price(mat)
        self.assertEqual(avg, Decimal("15.000000"))


class LowStockTest(TestCase):
    def setUp(self):
        self.user = make_admin()

    def test_below_min_detected(self):
        mat = make_material(name="Low Mat", unit="kg")
        receive(
            material=mat, received_on=date.today(),
            quantity=Decimal("5"), total_amount=Decimal("50"),
            user=self.user, currency="USD",
        )
        set_min_quantity(mat, Decimal("10"))
        low = low_stock_materials()
        self.assertEqual(low.count(), 1)

    def test_above_min_not_flagged(self):
        mat = make_material(name="OK Mat", unit="kg")
        receive(
            material=mat, received_on=date.today(),
            quantity=Decimal("20"), total_amount=Decimal("200"),
            user=self.user, currency="USD",
        )
        set_min_quantity(mat, Decimal("10"))
        low = low_stock_materials()
        self.assertEqual(low.count(), 0)

    def test_no_min_set_not_flagged(self):
        mat = make_material(name="NoMin Mat", unit="kg")
        receive(
            material=mat, received_on=date.today(),
            quantity=Decimal("1"), total_amount=Decimal("10"),
            user=self.user, currency="USD",
        )
        low = low_stock_materials()
        self.assertEqual(low.count(), 0)
