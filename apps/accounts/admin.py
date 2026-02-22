from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserInvite


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'tenant', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'tenant']
    inlines = [UserProfileInline]
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HRM Info', {'fields': ('tenant', 'role', 'avatar', 'phone', 'is_tenant_admin')}),
    )


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = ['email', 'tenant', 'role', 'status', 'invited_by', 'created_at']
    list_filter = ['status', 'role']
