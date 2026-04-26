from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_member', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Role', {'fields': ('is_admin', 'is_member')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Role', {'fields': ('is_admin', 'is_member')}),
    )