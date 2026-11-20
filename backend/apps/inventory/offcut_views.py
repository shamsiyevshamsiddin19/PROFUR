"""Separate stock of reusable cut pieces."""

from decimal import Decimal

from accounts.permissions import HasPermissionCode
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action

from apps.catalog.access import is_shop_worker, visible_materials

from . import offcut_services
from .issue_views import IdempotentCreateMixin
from .models import LeftoverOffcut, StockIssue

DIMENSION = {"max_digits": 10, "decimal_places": 2, "min_value": Decimal("0.01")}


class OffcutSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.__str__")
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
            "source_issue",
            "note",
            "registered_by_name",
            "created_at",
        ]

    def get_registered_by_name(self, obj):
        return obj.registered_by.get_full_name() or obj.registered_by.username


class OffcutCreateSerializer(serializers.Serializer):
    issue_id = serializers.IntegerField(min_value=1)
    length_mm = serializers.DecimalField(**DIMENSION)
    width_mm = serializers.DecimalField(**DIMENSION, required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, max_value=999_999_999)
    note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )


class OffcutWithdrawSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, max_value=999_999_999)
    reason = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )


class OffcutViewSet(
    IdempotentCreateMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OffcutSerializer
    permission_classes = [HasPermissionCode]
    http_method_names = ["get", "post", "head", "options"]
    idempotency_endpoint = "offcuts:create"

    @property
    def required_permission(self):
        return {
            "create": "inventory.add_offcut",
            "withdraw": "inventory.use_offcut",
        }.get(self.action, "inventory.view_offcut")

    def get_queryset(self):
        qs = LeftoverOffcut.objects.select_related("material", "registered_by").filter(
            material__in=visible_materials(self.request.user)
        )
        if self.action == "list":
            qs = qs.filter(quantity__gt=0)
            if search := self.request.query_params.get("search", "").strip():
                qs = qs.filter(material__name__icontains=search)
        return qs

    def create(self, request, *args, **kwargs):
        def perform():
            form = OffcutCreateSerializer(data=request.data)
            form.is_valid(raise_exception=True)
            data = dict(form.validated_data)
            issues = StockIssue.objects.filter(
                material__in=visible_materials(request.user)
            )
            if is_shop_worker(request.user):
                issues = issues.filter(created_by=request.user)
            issue = get_object_or_404(issues, pk=data.pop("issue_id"))
            try:
                offcut = offcut_services.register_offcut(
                    material=issue.material,
                    source_issue=issue,
                    user=request.user,
                    **{"width_mm": None, **data},
                )
            except (
                offcut_services.OffcutDimensionError,
                offcut_services.OffcutUnitError,
            ) as error:
                raise serializers.ValidationError({"detail": str(error)}) from error
            return self.get_serializer(offcut).data

        return self.idempotent_create(request, perform)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        self.idempotency_endpoint = f"offcuts:{pk}:withdraw"

        def perform():
            offcut = self.get_object()
            form = OffcutWithdrawSerializer(data=request.data)
            form.is_valid(raise_exception=True)
            try:
                result = offcut_services.withdraw_offcut(
                    offcut.pk, user=request.user, **form.validated_data
                )
            except DjangoValidationError as error:
                raise serializers.ValidationError(
                    {"quantity": error.messages}
                ) from error
            return self.get_serializer(result).data

        return self.idempotent_create(request, perform)

    def replay_body(self, body, user):
        get_object_or_404(self.get_queryset(), pk=body["id"])
        return body
