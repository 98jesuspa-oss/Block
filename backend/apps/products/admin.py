from django.contrib import admin
from .models import Product, InventoryMovement

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'precio', 'stock', 'stock_min', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('sku', 'nombre')

@admin.register(InventoryMovement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'tipo', 'cantidad', 'stock_after', 'user', 'created_at')
    list_filter = ('tipo',)
    readonly_fields = ('created_at',)