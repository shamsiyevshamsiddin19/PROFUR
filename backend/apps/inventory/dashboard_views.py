"""Dashboard va eksport API endpointlari.

Dashboard — ombor umumiy ko'rinishi: qoldiq qiymati, kam qoldiq, oylik oqim.
Eksport — harakatlar ro'yxatini CSV formatida yuklab olish.
"""

from datetime import date

from accounts.permissions import HasPermissionCode
from django.http import StreamingHttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.access import is_shop_worker, visible_materials

from .models import StockMovement
from .monthly import current_month, month_report

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class DashboardView(APIView):
    permission_classes = [HasPermissionCode]
    required_permission = "inventory.view_report"

    def get(self, request):
        raw = request.query_params.get("month")
        try:
            month = date.fromisoformat(raw + "-01") if raw else current_month()
            if month.year > 9998:
                raise ValueError
        except ValueError:
            raise ValidationError(
                {"month": _("Oy YYYY-MM shaklida bo‘lishi kerak.")}
            ) from None
        return Response(month_report(request.user, month))


def _csv_safe(value):
    """Neutralize spreadsheet formula injection."""
    s = str(value)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


class ExportMovementsView(APIView):
    permission_classes = [HasPermissionCode]
    required_permission = "inventory.view_stock"

    def get(self, request):
        qs = StockMovement.objects.select_related(
            "material", "batch", "created_by"
        ).order_by("-created_at")

        qs = qs.filter(material__in=visible_materials(request.user))
        if is_shop_worker(request.user):
            qs = qs.filter(created_by=request.user)
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
