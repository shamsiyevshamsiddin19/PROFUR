"""PCRM-38: kategoriya va material modellari bazaga to'g'ri saqlanishi."""

from decimal import Decimal

import pytest
from apps.catalog.models import Category, Material, Unit
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError

pytestmark = pytest.mark.django_db

# Noyoblik cheklovi NULLS NOT DISTINCT bilan faqat PostgreSQL 15+ da yaratiladi.
# Lokal SQLite'da Django uni yaratmaydi (models.W047), CI esa PostgreSQL'da ishlaydi.
postgres_only = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="Noyoblik cheklovi faqat PostgreSQL 15+ da yaratiladi",
)


@pytest.fixture
def category() -> Category:
    return Category.objects.create(name="LDSP")


def make_sheet(category: Category, **overrides) -> Material:
    data = {
        "category": category,
        "name": "LDSP Egger",
        "color": "oq",
        "length_cm": Decimal("280.00"),
        "width_cm": Decimal("207.00"),
        "thickness_cm": Decimal("1.60"),
        "unit": Unit.SHEET,
    }
    data.update(overrides)
    return Material.objects.create(**data)


def test_material_is_saved_and_read_back(category):
    created = make_sheet(category)

    material = Material.objects.select_related("category").get(pk=created.pk)

    assert material.category.name == "LDSP"
    assert material.thickness_cm == Decimal("1.60")
    assert material.unit == "sheet"
    assert material.is_active is True
    assert material.created_at is not None
    assert str(material) == "LDSP Egger · oq · 280×207×1.6"


def test_material_without_dimensions_is_allowed(category):
    glue = Material.objects.create(category=category, name="Kley", unit=Unit.KG)

    assert Material.objects.get(pk=glue.pk).length_cm is None
    assert str(glue) == "Kley"


@postgres_only
def test_same_nomenclature_cannot_be_duplicated(category):
    make_sheet(category)

    with pytest.raises(IntegrityError), transaction.atomic():
        make_sheet(category)


def test_different_thickness_is_a_separate_material(category):
    make_sheet(category)
    make_sheet(category, thickness_cm=Decimal("1.80"))

    assert Material.objects.count() == 2


@postgres_only
def test_duplicate_without_dimensions_is_rejected(category):
    Material.objects.create(category=category, name="Kley", unit=Unit.KG)

    with pytest.raises(IntegrityError), transaction.atomic():
        Material.objects.create(category=category, name="Kley", unit=Unit.KG)


@pytest.mark.parametrize("field", ["length_cm", "width_cm", "thickness_cm"])
@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1.5")])
def test_dimension_must_be_positive(category, field, value):
    with pytest.raises(IntegrityError), transaction.atomic():
        make_sheet(category, **{field: value})


def test_unknown_unit_is_rejected_by_database(category):
    with pytest.raises(IntegrityError), transaction.atomic():
        make_sheet(category, unit="box")


def test_category_with_materials_cannot_be_deleted(category):
    make_sheet(category)

    with pytest.raises(ProtectedError):
        category.delete()


def test_category_name_is_unique(category):
    with pytest.raises(IntegrityError), transaction.atomic():
        Category.objects.create(name="LDSP")
