from django.contrib import admin

from .models import Category, Material


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "color",
        "length_cm",
        "width_cm",
        "thickness_cm",
        "unit",
        "is_active",
    ]
    list_filter = ["category", "unit", "is_active"]
    search_fields = ["name", "color"]
    list_select_related = ["category"]
