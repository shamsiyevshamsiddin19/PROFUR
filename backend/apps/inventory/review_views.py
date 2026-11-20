"""Admin review of already applied warehouse operations."""

from accounts.permissions import IsAdminRole
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import WarehouseReview
from .offcut_services import correct_offcut
from .serializers import material_brief, user_brief


class ReviewSerializer(serializers.ModelSerializer):
    material = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    corrected = serializers.SerializerMethodField()

    def get_corrected(self, obj):
        return hasattr(obj, "correction")

    class Meta:
        model = WarehouseReview
        fields = [
            "id",
            "kind",
            "state",
            "material",
            "issue",
            "offcut",
            "quantity",
            "actor",
            "note",
            "created_at",
            "reviewer",
            "reviewed_at",
            "review_note",
            "corrected",
        ]

    def get_material(self, obj):
        return material_brief(obj.material)

    def get_actor(self, obj):
        return user_brief(obj.actor)

    def get_reviewer(self, obj):
        return user_brief(obj.reviewer) if obj.reviewer_id else None


class DecisionSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=["reviewed", "flagged"])
    note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )

    def validate(self, data):
        if data["state"] == "flagged" and not data["note"]:
            raise serializers.ValidationError({"note": _("Tuzatish sababini yozing.")})
        return data


class WarehouseReviewViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        rows = WarehouseReview.objects.select_related(
            "material", "actor", "reviewer", "correction"
        )
        return (
            rows.filter(state="pending")
            if self.request.query_params.get("pending") == "true"
            else rows
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def decide(self, request, pk=None):
        row = WarehouseReview.objects.select_for_update().get(pk=self.get_object().pk)
        serializer = DecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if row.state == WarehouseReview.State.PENDING:
            row.state = serializer.validated_data["state"]
            row.review_note = serializer.validated_data["note"]
            row.reviewer = request.user
            row.reviewed_at = timezone.now()
            row.save(update_fields=["state", "review_note", "reviewer", "reviewed_at"])
        return Response(self.get_serializer(row).data)

    @action(detail=True, methods=["post"])
    def correct(self, request, pk=None):
        form = serializers.CharField(max_length=500)
        reason = form.run_validation(request.data.get("note"))
        try:
            record = correct_offcut(self.get_object().pk, request.user, reason)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"detail": error.messages[0]}) from error
        return Response(self.get_serializer(record).data)
