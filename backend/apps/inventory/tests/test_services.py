from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.inventory.models import (
    ImmutableLedgerError,
    StockMovement,
)
from apps.inventory.services import (
    Allocation,
    InsufficientStockError,
    issue_stock,
    receive,
)

from .factories import make_admin, make_material, stock_up


class ReceiveTest(TestCase):
    def setUp(self):
        self.user = make_admin()
        self.material = make_material()

    def test_receive_creates_batch_and_balance(self):
        batch, balance = receive(
            material=self.material,
            received_on=date.today(),
            quantity=Decimal("10"),
            total_amount=Decimal("100"),
            user=self.user,
            currency="USD",
        )
        self.assertEqual(batch.quantity, Decimal("10"))
        self.assertEqual(batch.unit_price, Decimal("10.000000"))
        self.assertEqual(balance.quantity_on_hand, Decimal("10"))

    def test_receive_creates_movement(self):
        batch, _ = receive(
            material=self.material,
            received_on=date.today(),
            quantity=Decimal("10"),
            total_amount=Decimal("100"),
            user=self.user,
            currency="USD",
        )
        movement = StockMovement.objects.first()
        self.assertIsNotNone(movement)
        self.assertEqual(movement.type, "receipt")
        self.assertEqual(movement.quantity, Decimal("10"))
        self.assertEqual(movement.batch_id, batch.pk)

    def test_receive_integer_unit_rejects_fraction(self):
        mat = make_material(name="Sheet Mat", unit="sheet")
        with self.assertRaises(ValidationError):
            receive(
                material=mat,
                received_on=date.today(),
                quantity=Decimal("1.5"),
                total_amount=Decimal("100"),
                user=self.user,
                currency="USD",
            )

    def test_receive_kg_allows_fraction(self):
        mat = make_material(name="KG Mat", unit="kg")
        batch, balance = receive(
            material=mat,
            received_on=date.today(),
            quantity=Decimal("1.5"),
            total_amount=Decimal("100"),
            user=self.user,
            currency="USD",
        )
        self.assertEqual(batch.quantity, Decimal("1.5"))

    def test_multiple_receives_accumulate(self):
        receive(
            material=self.material,
            received_on=date.today(),
            quantity=Decimal("10"),
            total_amount=Decimal("100"),
            user=self.user,
            currency="USD",
        )
        _, balance = receive(
            material=self.material,
            received_on=date.today(),
            quantity=Decimal("5"),
            total_amount=Decimal("75"),
            user=self.user,
            currency="USD",
        )
        self.assertEqual(balance.quantity_on_hand, Decimal("15"))

    def test_unit_price_calculated_correctly(self):
        batch, _ = receive(
            material=self.material,
            received_on=date.today(),
            quantity=Decimal("3"),
            total_amount=Decimal("100"),
            user=self.user,
            currency="USD",
        )
        # 100 / 3 = 33.333333 (6 decimal places, ROUND_HALF_UP)
        self.assertEqual(batch.unit_price, Decimal("33.333333"))


class ImmutableLedgerTest(TestCase):
    def setUp(self):
        self.user = make_admin()
        self.material = make_material()
        stock_up(self.material, 10, 100, self.user)

    def test_cannot_update_movement(self):
        movement = StockMovement.objects.first()
        with self.assertRaises(ImmutableLedgerError):
            movement.reason = "tampered"
            movement.save()

    def test_cannot_delete_movement(self):
        movement = StockMovement.objects.first()
        with self.assertRaises(ImmutableLedgerError):
            movement.delete()

    def test_queryset_update_blocked(self):
        with self.assertRaises(ImmutableLedgerError):
            StockMovement.objects.all().update(reason="tampered")

    def test_queryset_delete_blocked(self):
        with self.assertRaises(ImmutableLedgerError):
            StockMovement.objects.all().delete()


class IssueTest(TestCase):
    def setUp(self):
        self.user = make_admin()
        self.material = make_material(name="Issue Mat", unit="kg")
        self.batch, _ = stock_up(self.material, 100, 1000, self.user)

    def test_issue_decrements_stock(self):
        issue, on_hand = issue_stock(
            material=self.material,
            allocations=[Allocation(batch_id=self.batch.id, quantity=Decimal("10"))],
            issued_on=date.today(),
            recipient_name="Worker",
            user=self.user,
        )
        self.assertEqual(on_hand, Decimal("90"))

    def test_issue_creates_movement(self):
        issue, _ = issue_stock(
            material=self.material,
            allocations=[Allocation(batch_id=self.batch.id, quantity=Decimal("10"))],
            issued_on=date.today(),
            recipient_name="Worker",
            user=self.user,
        )
        movements = StockMovement.objects.filter(type="issue")
        self.assertEqual(movements.count(), 1)
        self.assertEqual(movements.first().quantity, Decimal("-10"))

    def test_issue_insufficient_stock(self):
        with self.assertRaises(InsufficientStockError):
            issue_stock(
                material=self.material,
                allocations=[
                    Allocation(batch_id=self.batch.id, quantity=Decimal("200"))
                ],
                issued_on=date.today(),
                recipient_name="Worker",
                user=self.user,
            )

    def test_issue_batch_remaining_decremented(self):
        issue_stock(
            material=self.material,
            allocations=[Allocation(batch_id=self.batch.id, quantity=Decimal("30"))],
            issued_on=date.today(),
            recipient_name="Worker",
            user=self.user,
        )
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.quantity_remaining, Decimal("70"))

    def test_issue_integer_unit_rejects_fraction(self):
        mat = make_material(name="Sheet Issue", unit="sheet")
        batch, _ = stock_up(mat, 10, 100, self.user)
        with self.assertRaises(ValidationError):
            issue_stock(
                material=mat,
                allocations=[Allocation(batch_id=batch.id, quantity=Decimal("1.5"))],
                issued_on=date.today(),
                recipient_name="Worker",
                user=self.user,
            )
