"""Remove the retired default roles once they have no dependents."""

from accounts.models import Role
from apps.catalog.models import Material
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

RETIRED_CODES = ("PRODUCTION_SUPERVISOR", "ACCOUNTANT", "PROCUREMENT")


class Command(BaseCommand):
    help = "Ishlab chiqarish ustasi, bosh hisobchi va ta’minotchi rollarini olib tashlaydi."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true", help="O‘chirishni bajarish."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        roles = list(Role.objects.select_for_update().filter(code__in=RETIRED_CODES))
        codes = {role.code for role in roles}
        assigned = [role.code for role in roles if role.users.exists()]
        if assigned:
            raise CommandError(
                "Avval biriktirilgan rollarni yeching: " + ", ".join(assigned)
            )

        # Earlier warehouse releases have no role restrictions at material level.
        if codes and hasattr(Material, "allowed_roles"):
            restrictions = (
                Material.objects.exclude(allowed_roles=[])
                .values_list("allowed_roles", flat=True)
                .iterator()
            )
            if any(codes.intersection(restriction) for restriction in restrictions):
                raise CommandError("Bu rollar material ko‘rinishida ishlatilmoqda.")

        if not roles:
            self.stdout.write("Olib tashlanadigan rollar qolmagan.")
        elif options["apply"]:
            Role.objects.filter(pk__in=[role.pk for role in roles]).delete()
            self.stdout.write("Olib tashlandi: " + ", ".join(sorted(codes)))
        else:
            self.stdout.write("Olib tashlash mumkin: " + ", ".join(sorted(codes)))
