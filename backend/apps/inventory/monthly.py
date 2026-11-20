"""Monthly warehouse totals by business date and operation kind."""

from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Count, DecimalField, F, Sum
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
    materials = visible_materials(user).select_related("category", "stock").order_by()
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

    stock_vals = {}
    if prices:
        stock_val_qs = (
            Batch.objects.filter(material__in=materials, quantity_remaining__gt=0)
            .values("material_id")
            .annotate(val=Sum(F("quantity_remaining") * F("unit_price")))
        )
        stock_vals = {row["material_id"]: cash(row["val"]) for row in stock_val_qs}

    rows = []
    materials_with_movements = materials.filter(pk__in=per_material).order_by("name", "pk")
    for m in materials_with_movements:
        data = per_material[m.pk]
        i_u = Decimal(data.get("issued", "0"))
        ret_u = Decimal(data.get("returned", "0"))
        net_u = str(i_u - ret_u)

        row_item = {
            "material": {
                "id": m.pk,
                "name": str(m),
                "unit": m.unit,
                "category": {
                    "id": m.category_id,
                    "name": m.category.name if m.category else "",
                }
                if m.category_id
                else None,
            },
            "current_stock": str(
                getattr(getattr(m, "stock", None), "quantity_on_hand", "0")
            ),
            "net_issued": net_u,
            **data,
        }
        if prices:
            row_item["stock_value_usd"] = stock_vals.get(m.pk, "0.00")
            i_usd = Decimal(data.get("issued_usd", "0"))
            ret_usd = Decimal(data.get("returned_usd", "0"))
            row_item["net_issued_usd"] = cash(i_usd - ret_usd)
        rows.append(row_item)

    result = {
        "month": start.isoformat()[:7],
        "rows": rows,
    }

    # Categories breakdown
    cat_summary = {}
    for m in materials_with_movements:
        cat_id = m.category_id or 0
        cat_name = m.category.name if m.category else "Boshqa"
        if cat_id not in cat_summary:
            cat_summary[cat_id] = {
                "id": cat_id,
                "name": cat_name,
                "received_units": Decimal(0),
                "issued_units": Decimal(0),
                "returned_units": Decimal(0),
                "written_off_units": Decimal(0),
                "net_issued_units": Decimal(0),
                "received_usd": Decimal(0),
                "issued_usd": Decimal(0),
                "returned_usd": Decimal(0),
                "written_off_usd": Decimal(0),
                "net_issued_usd": Decimal(0),
                "materials_count": 0,
            }
        c = cat_summary[cat_id]
        c["materials_count"] += 1
        r_u = Decimal(per_material[m.pk].get("received", "0"))
        i_u = Decimal(per_material[m.pk].get("issued", "0"))
        ret_u = Decimal(per_material[m.pk].get("returned", "0"))
        w_u = Decimal(per_material[m.pk].get("written_off", "0"))
        c["received_units"] += r_u
        c["issued_units"] += i_u
        c["returned_units"] += ret_u
        c["written_off_units"] += w_u
        c["net_issued_units"] += (i_u - ret_u)
        if prices:
            r_usd = Decimal(per_material[m.pk].get("received_usd", "0"))
            i_usd = Decimal(per_material[m.pk].get("issued_usd", "0"))
            ret_usd = Decimal(per_material[m.pk].get("returned_usd", "0"))
            w_usd = Decimal(per_material[m.pk].get("written_off_usd", "0"))
            c["received_usd"] += r_usd
            c["issued_usd"] += i_usd
            c["returned_usd"] += ret_usd
            c["written_off_usd"] += w_usd
            c["net_issued_usd"] += (i_usd - ret_usd)

    result["categories_breakdown"] = [
        {
            "id": c["id"],
            "name": c["name"],
            "materials_count": c["materials_count"],
            "received_units": str(c["received_units"]),
            "issued_units": str(c["issued_units"]),
            "returned_units": str(c["returned_units"]),
            "written_off_units": str(c["written_off_units"]),
            "net_issued_units": str(c["net_issued_units"]),
            **(
                {
                    "received_usd": cash(c["received_usd"]),
                    "issued_usd": cash(c["issued_usd"]),
                    "returned_usd": cash(c["returned_usd"]),
                    "written_off_usd": cash(c["written_off_usd"]),
                    "net_issued_usd": cash(c["net_issued_usd"]),
                }
                if prices
                else {}
            ),
        }
        for c in sorted(cat_summary.values(), key=lambda x: x["name"])
    ]

    # Recipients breakdown
    rec_breakdown = []
    rec_sums = {"total_quantity": Sum("quantity"), "issues_count": Count("issue_id", distinct=True)}
    if prices:
        rec_sums["total_cost"] = Sum(
            F("quantity") * F("batch__unit_price"),
            output_field=DecimalField(max_digits=30, decimal_places=8),
        )
    rec_qs = issues.values("issue__recipient_name").annotate(**rec_sums).order_by("-total_quantity")[:15]
    for r in rec_qs:
        rec_breakdown.append(
            {
                "recipient": r["issue__recipient_name"] or "Noma'lum",
                "total_quantity": str(r["total_quantity"]),
                "issues_count": r["issues_count"],
                **(
                    {"total_usd": cash(r.get("total_cost"))}
                    if prices and "total_cost" in r
                    else {}
                ),
            }
        )
    result["recipients_breakdown"] = rec_breakdown

    # Totals
    if prices:
        value = Batch.objects.filter(
            material__in=materials, quantity_remaining__gt=0
        ).aggregate(total=Sum(F("quantity_remaining") * F("unit_price")))["total"]
        result["totals"] = {
            **{key: cash(amounts[key]) for key, *_ in scopes},
            "net_issued": cash(amounts["issued"] - amounts["returned"]),
            "warehouse_value": cash(value),
        }
        result["top_consumed"] = sorted(
            [r for r in rows if Decimal(r.get("net_issued_usd", "0")) > 0],
            key=lambda x: Decimal(x.get("net_issued_usd", "0")),
            reverse=True,
        )[:5]
    else:
        result["top_consumed"] = sorted(
            [r for r in rows if Decimal(r.get("net_issued", "0")) > 0],
            key=lambda x: Decimal(x.get("net_issued", "0")),
            reverse=True,
        )[:5]

    # Expenses
    if user.has_permission_code("expenses.view_expense"):
        exp_filter = Expense.objects.filter(spent_on__gte=start, spent_on__lt=end)
        exp_total = exp_filter.aggregate(total=Sum("amount"))["total"] or Decimal(0)
        result["expenses"] = cash(exp_total)

        exp_breakdown = []
        exp_groups = (
            exp_filter.values(
                "expense_type_id",
                "expense_type__code",
                "expense_type__name_uz",
                "expense_type__name_ru",
                "expense_type__name_en",
            )
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )
        for eg in exp_groups:
            amt = eg["total"] or Decimal(0)
            pct = round(float(amt / exp_total * 100), 1) if exp_total > 0 else 0.0
            exp_breakdown.append(
                {
                    "type_id": eg["expense_type_id"],
                    "code": eg["expense_type__code"],
                    "name_uz": eg["expense_type__name_uz"],
                    "name_ru": eg["expense_type__name_ru"] or eg["expense_type__name_uz"],
                    "name_en": eg["expense_type__name_en"] or eg["expense_type__name_uz"],
                    "amount": cash(amt),
                    "percentage": pct,
                    "count": eg["count"],
                }
            )
        result["expenses_breakdown"] = exp_breakdown

    return result


def current_month():
    return timezone.localdate().replace(day=1)
