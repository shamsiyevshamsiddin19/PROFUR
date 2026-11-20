"""Monthly warehouse totals by business date and operation kind."""

from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import DecimalField, F, Sum
from django.utils import timezone

from apps.catalog.access import visible_materials
from apps.expenses.models import Expense

from .models import (
    MONEY_STEP,
    Batch,
    RequestStatus,
    StockIssueAllocation,
    StockReturnAllocation,
    WriteOffAllocation,
)


def cash(value):
    return str((value or Decimal(0)).quantize(MONEY_STEP, rounding=ROUND_HALF_UP))


def month_report(user, start):
    end = date(start.year + (start.month == 12), start.month % 12 + 1, 1)
    materials = visible_materials(user).order_by()
    prices = user.has_permission_code("inventory.view_purchase_price")

    received = Batch.objects.filter(
        material__in=materials,
        received_on__gte=start,
        received_on__lt=end,
        is_opening=False,
    )
    issues = StockIssueAllocation.objects.filter(
        issue__material__in=materials,
        issue__issued_on__gte=start,
        issue__issued_on__lt=end,
    )
    returns = StockReturnAllocation.objects.filter(
        stock_return__issue__material__in=materials,
        stock_return__status=RequestStatus.APPROVED,
        stock_return__returned_on__gte=start,
        stock_return__returned_on__lt=end,
    )
    write_offs = WriteOffAllocation.objects.filter(
        write_off__material__in=materials,
        write_off__status=RequestStatus.APPROVED,
        write_off__decided_at__date__gte=start,
        write_off__decided_at__date__lt=end,
    )
    scopes = (
        ("received", received, "material_id", F("total_amount")),
        (
            "issued",
            issues,
            "issue__material_id",
            F("quantity") * F("batch__unit_price"),
        ),
        (
            "returned",
            returns,
            "stock_return__issue__material_id",
            F("quantity") * F("batch__unit_price"),
        ),
        (
            "written_off",
            write_offs,
            "write_off__material_id",
            F("quantity") * F("batch__unit_price"),
        ),
    )
    amounts = defaultdict(Decimal)
    per_material = defaultdict(dict)
    for key, queryset, field, cost in scopes:
        sums = {"units": Sum("quantity")}
        if prices:
            sums["amount"] = Sum(
                cost, output_field=DecimalField(max_digits=30, decimal_places=8)
            )
        for row in queryset.order_by().values(field).annotate(**sums):
            per_material[row[field]][key] = str(row["units"])
            if prices:
                amounts[key] += row["amount"] or Decimal(0)
                per_material[row[field]][key + "_usd"] = cash(row["amount"])

    result = {
        "month": start.isoformat()[:7],
        "rows": [
            {
                "material": {"id": m.pk, "name": str(m), "unit": m.unit},
                **per_material[m.pk],
            }
            for m in materials.filter(pk__in=per_material).order_by("name", "pk")
        ],
    }
    if prices:
        value = Batch.objects.filter(
            material__in=materials, quantity_remaining__gt=0
        ).aggregate(total=Sum(F("quantity_remaining") * F("unit_price")))["total"]
        result["totals"] = {
            **{key: cash(amounts[key]) for key, *_ in scopes},
            "net_issued": cash(amounts["issued"] - amounts["returned"]),
            "warehouse_value": cash(value),
        }
    if user.has_permission_code("expenses.view_expense"):
        result["expenses"] = cash(
            Expense.objects.filter(spent_on__gte=start, spent_on__lt=end).aggregate(
                total=Sum("amount")
            )["total"]
        )
    return result


def current_month():
    return timezone.localdate().replace(day=1)
