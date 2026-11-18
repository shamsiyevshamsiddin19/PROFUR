"""PCRM-5 bo‘yicha boshlang‘ich material kategoriyalari."""

from django.db import migrations


def create_categories(apps, schema_editor):
    category = apps.get_model("catalog", "Category")
    database = schema_editor.connection.alias
    for name in (
        "Furnitura", "Bo‘yoq", "Astar", "LMDF", "LDSP",
        "Faner", "PVC", "DSP", "Qadoqlash",
    ):
        category.objects.using(database).get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [
        migrations.RunPython(create_categories, migrations.RunPython.noop),
    ]
