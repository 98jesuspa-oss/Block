from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('nombre','tipo','tel','email','activo')
    list_filter = ('tipo','activo')
    search_fields = ('nombre','tel','rfc')