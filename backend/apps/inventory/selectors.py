"""Ombor analitika so'rovlari (read-side queries).

Yozish amallari ``services`` modulida, o'qish so'rovlari shu yerda.
Dashboard, hisobot va filtrlar uchun ishlatiladi.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import (
    Count,
    DecimalField,
    F,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce, TruncMonth

from apps.catalog.models import Material
from apps.inventory.models import (
    MONEY_STEP,
    Batch,
    StockBalance,
    StockMovement,
)


# ---------------------------------------------------------------------------
# Yordamchi: oy qo'shish (python-dateutil talab qilinmaydi)
# ---------------------------------------------------------------------------

def _add_months(d: date, months: int) -> date:
    """Sanaga oy qo'shadi, oyning 1-kuniga qaytaradi."""
    m = d.month - 1 + months
    year = d.year + m // 12
    month = m % 12 + 1
    return d.replace(year=year, month=month, day=1)


# ---------------------------------------------------------------------------
# Umumiy qiymat
# ---------------------------------------------------------------------------

def warehouse_valuation() -> Decimal:
    """Total warehouse value: SUM(batch.quantity_remaining * batch.unit_price) for open batches."""
    result = (
        Batch.objects
        .filter(quantity_remaining__gt=0)
        .aggregate(
            total=Sum(
                F("quantity_remaining") * F("unit_price"),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            )
        )
    )
    return (result["total"] or Decimal("0")).quantize(MONEY_STEP)


# ---------------------------------------------------------------------------
# Minimal qoldiqdan past materiallar
# ---------------------------------------------------------------------------

def low_stock_materials():
    """Materials where current stock is below minimum threshold."""
    return (
        StockBalance.objects
        .filter(
            min_quantity__isnull=False,
            quantity_on_hand__lt=F("min_quantity"),
        )
        .select_related("material", "material__category")
        .order_by("material__name")
    )


# ---------------------------------------------------------------------------
# Oylik kirim/chiqim oqimi
# ---------------------------------------------------------------------------

@dataclass
class MonthFlow:
    month: date
    kirim_count: int = 0
    kirim_usd: Decimal = Decimal("0")
    chiqim_count: int = 0
    chiqim_usd: Decimal = Decimal("0")


def recent_month_flows(months: int = 6) -> list[MonthFlow]:
    """Return per-month kirim/chiqim totals for the last N months."""
    today = date.today()
    start = _add_months(today.replace(day=1), -(months - 1))

    movements = (
        StockMovement.objects
        .filter(created_at__date__gte=start)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            kirim_count=Count("id", filter=Q(quantity__gt=0)),
            kirim_usd=Coalesce(
                Sum(
                    F("quantity") * F("batch__unit_price"),
                    filter=Q(quantity__gt=0, batch__isnull=False),
                    output_field=DecimalField(max_digits=18, decimal_places=2),
                ),
                Value(Decimal("0")),
            ),
            chiqim_count=Count("id", filter=Q(quantity__lt=0)),
            chiqim_usd=Coalesce(
                Sum(
                    -F("quantity") * F("batch__unit_price"),
                    filter=Q(quantity__lt=0, batch__isnull=False),
                    output_field=DecimalField(max_digits=18, decimal_places=2),
                ),
                Value(Decimal("0")),
            ),
        )
        .order_by("month")
    )

    by_month: dict[date, MonthFlow] = {}
    for row in movements:
        m = row["month"].date() if hasattr(row["month"], "date") else row["month"]
        by_month[m] = MonthFlow(
            month=m,
            kirim_count=row["kirim_count"],
            kirim_usd=row["kirim_usd"].quantize(MONEY_STEP),
            chiqim_count=row["chiqim_count"],
            chiqim_usd=row["chiqim_usd"].quantize(MONEY_STEP),
        )

    # Bo'sh oylarni to'ldirish
    result: list[MonthFlow] = []
    cursor = start
    today_first = today.replace(day=1)
    while cursor <= today_first:
        result.append(by_month.get(cursor, MonthFlow(month=cursor)))
        cursor = _add_months(cursor, 1)

    return result


# ---------------------------------------------------------------------------
# Foydalanuvchiga ko'rinadigan materiallar
# ---------------------------------------------------------------------------

def visible_materials(user):
    """Filter materials by user's allowed roles. Admin/superuser sees all."""
    qs = Material.objects.filter(is_active=True).select_related("category")
    if user.is_superuser or user.has_role("ADMIN"):
        return qs
    user_roles = user.role_codes
    if not user_roles:
        return qs.none()
    # Materials with empty allowed_roles are visible to all
    # Materials with specific roles are visible only to those roles
    return qs.filter(
        Q(allowed_roles=[]) | Q(allowed_roles__contained_by=user_roles)
    )


# ---------------------------------------------------------------------------
# Qoldiq qidirish filtrlari
# ---------------------------------------------------------------------------

def stock_search(queryset, search="", category=None, below_min=None):
    """Apply common stock filters."""
    if search:
        queryset = queryset.filter(
            Q(material__name__icontains=search)
            | Q(material__color__icontains=search)
            | Q(material__category__name__icontains=search)
        )
    if category:
        queryset = queryset.filter(material__category_id=category)
    if below_min is True:
        queryset = queryset.filter(
            min_quantity__isnull=False,
            quantity_on_hand__lt=F("min_quantity"),
        )
    return queryset


# ---------------------------------------------------------------------------
# Vaznli o'rtacha narx (weighted average cost)
# ---------------------------------------------------------------------------

def weighted_average_price(material) -> Decimal:
    """Materialning vaznli o'rtacha narxini hisoblaydi.

    Formulasi: SUM(batch.quantity_remaining * batch.unit_price)
               / SUM(batch.quantity_remaining)
    """
    result = (
        Batch.objects
        .filter(material=material, quantity_remaining__gt=0)
        .aggregate(
            total_value=Sum(
                F("quantity_remaining") * F("unit_price"),
                output_field=DecimalField(max_digits=18, decimal_places=6),
            ),
            total_qty=Sum("quantity_remaining"),
        )
    )
    total_value = result["total_value"]
    total_qty = result["total_qty"]
    if not total_value or not total_qty:
        return Decimal("0")
    return (total_value / total_qty).quantize(Decimal("0.000001"))


# ---------------------------------------------------------------------------
# Material bo'yicha iste'mol
# ---------------------------------------------------------------------------

def consumption_by_material(months: int = 1):
    """Total quantity consumed (issued) per material in the last N months."""
    start = _add_months(date.today().replace(day=1), -(months - 1))
    return (
        StockMovement.objects
        .filter(
            type="issue",
            created_at__date__gte=start,
        )
        .values("material__id", "material__name")
        .annotate(
            total_quantity=Sum(-F("quantity")),
        )
        .order_by("-total_quantity")
    )
