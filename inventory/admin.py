from django.contrib import admin

from .models import Category, Product, StockTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "quantity", "reorder_level", "price"]
    list_filter = ["category"]
    search_fields = ["name", "sku"]


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ["product", "transaction_type", "quantity", "created_at"]
    list_filter = ["transaction_type", "created_at"]
    search_fields = ["product__name", "product__sku"]
