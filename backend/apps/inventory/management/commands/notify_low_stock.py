"""Oldingi minimal qoldiqlar uchun xabarlarni bir marta yaratish."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.inventory.models import StockBalance
from apps.inventory.services import sync_low_stock


class Command(BaseCommand):
    help = "Mavjud qoldiqlar uchun minimal chegara xabarlarini sinxronlash."

    def handle(self, *args, **options):
        for pk in StockBalance.objects.values_list("pk", flat=True).iterator():
            with transaction.atomic():
                balance = StockBalance.objects.select_for_update().get(pk=pk)
                sync_low_stock(balance)
        self.stdout.write(self.style.SUCCESS("Qoldiq xabarlari sinxronlandi."))
