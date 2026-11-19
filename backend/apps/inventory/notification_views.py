"""Serverda saqlanadigan shaxsiy minimal qoldiq xabarlari."""

from accounts.permissions import HasPermissionCode
from django.utils import timezone
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import StockNotification


class NotificationSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material", read_only=True)

    class Meta:
        model = StockNotification
        fields = [
            "id",
            "material",
            "material_name",
            "quantity",
            "minimum",
            "created_at",
            "read_at",
        ]
        read_only_fields = fields


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [HasPermissionCode]
    required_permission = "inventory.view_stock"
    serializer_class = NotificationSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = StockNotification.objects.filter(
            recipient=self.request.user
        ).select_related("material")
        if self.request.query_params.get("unread") == "true":
            queryset = queryset.filter(read_at__isnull=True)
        return queryset

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notification = self.get_object()
        StockNotification.objects.filter(
            pk=notification.pk, read_at__isnull=True
        ).update(read_at=timezone.now())
        notification.refresh_from_db()
        return Response(self.get_serializer(notification).data)
