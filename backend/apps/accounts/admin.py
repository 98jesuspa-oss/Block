from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('VerdeBlock', {'fields': ('role', 'pin', 'avatar_color')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('VerdeBlock', {'fields': ('role', 'pin')}),
    )
