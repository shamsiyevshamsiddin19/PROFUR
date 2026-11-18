"""TZ 6.6 dagi uchta boshlang'ich xarajat turini qo'shadi: nalog, produkta, stanok.

Turlarning aniq ma'nosi TZ'da tasdiqlanmagan (TZ 19-bo'lim, 3-savol). Admin
nomlarni keyin panel yoki API orqali o'zgartira oladi; ``code`` o'zgarmaydi.
"""

from django.db import migrations

INITIAL_TYPES = [
    {"code": "tax", "name_uz": "Soliq", "name_ru": "Налог", "name_en": "Tax"},
    {
        "code": "products",
        "name_uz": "Mahsulot",
        "name_ru": "Продукты",
        "name_en": "Products",
    },
    {"code": "machine", "name_uz": "Stanok", "name_ru": "Станок", "name_en": "Machine"},
]


def create_initial_types(apps, schema_editor):
    """Boshlang'ich turlarni yaratadi; bor bo'lsa, qayta yaratmaydi."""
    expense_type = apps.get_model("expenses", "ExpenseType")
    for values in INITIAL_TYPES:
        expense_type.objects.get_or_create(code=values["code"], defaults=values)


def remove_initial_types(apps, schema_editor):
    """Migratsiya orqaga qaytarilganda boshlang'ich turlarni o'chiradi."""
    expense_type = apps.get_model("expenses", "ExpenseType")
    codes = [values["code"] for values in INITIAL_TYPES]
    expense_type.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("expenses", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_types, remove_initial_types),
    ]
