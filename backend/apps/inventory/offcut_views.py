"""Qoldiq materiallar API: ro'yxat, qayd etish va ishlatish."""

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import HasPermissionCode
from apps.catalog.models import Material
from apps.inventory import offcut_services
from apps.inventory.models import LeftoverOffcut


class OffcutSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.__str__", read_only=True)
    registered_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeftoverOffcut
        fields = [
            "id",
            "material",
            "material_name",
            "length_mm",
            "width_mm",
            "quantity",
            "note",
            "registered_by",
            "registered_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "registered_by", "created_at"]

    def get_registered_by_name(self, obj):
        u = obj.registered_by
        return f"{u.first_name} {u.last_name}".strip() or u.username


class OffcutCreateSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    length_mm = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
    )
    width_mm = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        required=False,
        allow_null=True,
    )
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        default=1,
    )
    note = serializers.CharField(max_length=500, required=False, default="")


class OffcutWithdrawSerializer(serializers.Serializer):
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
    )
    reason = serializers.CharField(max_length=500, required=False, default="")


class OffcutViewSet(ModelViewSet):
    serializer_class = OffcutSerializer
    permission_classes = [HasPermissionCode]
    permission_code = "inventory.view_stock"
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = LeftoverOffcut.objects.select_related(
            "material", "material__category", "registered_by"
        )
        material = self.request.query_params.get("material")
        if material:
            qs = qs.filter(material_id=material)
        return qs

    def create(self, request, *args, **kwargs):
        ser = OffcutCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        try:
            material = Material.objects.get(pk=d["material_id"], is_active=True)
        except Material.DoesNotExist:
            return Response(
                {"material_id": ["Material not found or inactive."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            offcut = offcut_services.register_offcut(
                material=material,
                length_mm=d["length_mm"],
                width_mm=d.get("width_mm"),
                quantity=d["quantity"],
                user=request.user,
                note=d.get("note", ""),
            )
        except (
            offcut_services.OffcutDimensionError,
            offcut_services.OffcutUnitError,
        ) as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OffcutSerializer(offcut).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="withdraw")
    def withdraw(self, request, pk=None):
        ser = OffcutWithdrawSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            offcut_services.withdraw_offcut(
                offcut_id=pk,
                quantity=ser.validated_data["quantity"],
                user=request.user,
                reason=ser.validated_data.get("reason", ""),
            )
        except LeftoverOffcut.DoesNotExist:
            return Response(
                {"detail": "Offcut not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Withdrawn successfully."})
