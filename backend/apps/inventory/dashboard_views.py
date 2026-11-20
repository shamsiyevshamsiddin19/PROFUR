"""Dashboard va eksport API endpointlari.

Dashboard — ombor umumiy ko'rinishi: qoldiq qiymati, kam qoldiq, oylik oqim.
Eksport — harakatlar ro'yxatini CSV formatida yuklab olish.
"""

from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasPermissionCode
from apps.inventory import selectors
from apps.inventory.models import StockMovement

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class DashboardView(APIView):
    permission_classes = [HasPermissionCode]
    permission_code = "inventory.view_stock"

    def get(self, request):
        can_see_prices = request.user.has_permission_code(
            "inventory.view_purchase_price"
        )
        flows = selectors.recent_month_flows(6)
        current = flows[-1] if flows else None
        low_stock = selectors.low_stock_materials()

        data = {
            "currency": "USD",
            "low_stock_count": low_stock.count(),
            "low_stock": [
                {
                    "material_id": bal.material_id,
                    "material_name": str(bal.material),
                    "quantity_on_hand": bal.quantity_on_hand,
                    "min_quantity": bal.min_quantity,
                }
                for bal in low_stock[:10]
            ],
            "current_month": {
                "kirim_count": current.kirim_count if current else 0,
                "chiqim_count": current.chiqim_count if current else 0,
            },
            "monthly_flows": [
                {
                    "month": f.month.isoformat(),
                    "kirim_count": f.kirim_count,
                    "chiqim_count": f.chiqim_count,
                }
                for f in flows
            ],
        }

        if can_see_prices:
            data["warehouse_valuation"] = str(selectors.warehouse_valuation())
            data["current_month"]["kirim_usd"] = (
                str(current.kirim_usd) if current else "0"
            )
            data["current_month"]["chiqim_usd"] = (
                str(current.chiqim_usd) if current else "0"
            )
            for i, f in enumerate(flows):
                data["monthly_flows"][i]["kirim_usd"] = str(f.kirim_usd)
                data["monthly_flows"][i]["chiqim_usd"] = str(f.chiqim_usd)

        return Response(data)


# ---------------------------------------------------------------------------
# CSV eksport
# ---------------------------------------------------------------------------


def _csv_safe(value):
    """Neutralize spreadsheet formula injection."""
    s = str(value)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


class ExportMovementsView(APIView):
    permission_classes = [HasPermissionCode]
    permission_code = "inventory.view_stock"

    def get(self, request):
        qs = StockMovement.objects.select_related(
            "material", "batch", "created_by"
        ).order_by("-created_at")

        material = request.query_params.get("material")
        if material:
            qs = qs.filter(material_id=material)

        move_type = request.query_params.get("type")
        if move_type:
            qs = qs.filter(type=move_type)

        date_from = request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        can_see_prices = request.user.has_permission_code(
            "inventory.view_purchase_price"
        )

        def rows():
            # UTF-8 BOM for Excel
            yield b"\xef\xbb\xbf"

            header = [
                "ID",
                "Type",
                "Material",
                "Quantity",
                "On Hand After",
                "Reason",
                "Created By",
                "Date",
            ]
            if can_see_prices:
                header.insert(5, "Unit Price")
            yield ",".join(header) + "\r\n"

            for chunk_start in range(0, qs.count(), 500):
                for m in qs[chunk_start : chunk_start + 500]:
                    row = [
                        _csv_safe(m.id),
                        _csv_safe(m.type),
                        _csv_safe(str(m.material)),
                        _csv_safe(m.quantity),
                        _csv_safe(m.quantity_on_hand_after),
                    ]
                    if can_see_prices:
                        row.append(_csv_safe(m.batch.unit_price if m.batch else ""))
                    row.extend(
                        [
                            _csv_safe(m.reason),
                            _csv_safe(str(m.created_by) if m.created_by else ""),
                            _csv_safe(m.created_at.strftime("%Y-%m-%d %H:%M")),
                        ]
                    )
                    yield ",".join(str(v) for v in row) + "\r\n"

        response = StreamingHttpResponse(rows(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="movements.csv"'
        return response
