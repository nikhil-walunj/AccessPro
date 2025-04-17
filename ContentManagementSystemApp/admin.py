from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'role', 'status', 'created_at', 'is_admin', 'is_superuser')
    search_fields = ('email', 'full_name')
    ordering = ('created_at',)
    list_filter = ('is_admin', 'is_superuser', 'status', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'role', 'status')}),
        ('Permissions', {'fields': ('is_admin', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin)
