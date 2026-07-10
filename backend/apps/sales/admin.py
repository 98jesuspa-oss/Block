from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('importe',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('folio','fecha','customer','user','metodo','total')
    list_filter = ('fecha','metodo','aplica_iva')
    search_fields = ('folio',)
    inlines = [SaleItemInline]
    readonly_fields = ('created_at',)