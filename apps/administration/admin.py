from django.contrib import admin
from .models import (
    Role, Permission, LoginHistory,
    ApprovalWorkflow, ApprovalStep, EmailTemplate, NotificationSetting, EscalationRule,
    SystemSetting, FinancialYear, FinancialPeriod, WorkingHoursPolicy, IntegrationSetting,
    AuditTrail, DataRetentionPolicy, BackupConfiguration, BackupLog,
)


class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 0


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_system_role', 'is_active', 'tenant']
    list_filter = ['is_active', 'is_system_role', 'tenant']
    search_fields = ['name', 'code']
    inlines = [PermissionInline]


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'ip_address', 'login_at', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['user', 'login_at', 'ip_address', 'user_agent', 'status']


class ApprovalStepInline(admin.TabularInline):
    model = ApprovalStep
    extra = 0


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'module', 'is_active', 'tenant']
    list_filter = ['module', 'is_active', 'tenant']
    search_fields = ['name']
    inlines = [ApprovalStepInline]


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'is_active', 'tenant']
    list_filter = ['event', 'is_active', 'tenant']
    search_fields = ['name', 'subject']


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ['event', 'channel', 'recipients', 'is_enabled', 'tenant']
    list_filter = ['channel', 'is_enabled', 'tenant']


@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'action', 'trigger_after_days', 'is_active', 'tenant']
    list_filter = ['action', 'is_active', 'tenant']


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'category', 'value_type', 'tenant']
    list_filter = ['category', 'value_type', 'tenant']
    search_fields = ['key', 'description']


@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'is_locked', 'tenant']
    list_filter = ['is_active', 'is_locked', 'tenant']


@admin.register(FinancialPeriod)
class FinancialPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'financial_year', 'period_number', 'start_date', 'end_date', 'is_locked', 'tenant']
    list_filter = ['is_locked', 'tenant']


@admin.register(WorkingHoursPolicy)
class WorkingHoursPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'work_start_time', 'work_end_time', 'total_hours', 'is_default', 'is_active', 'tenant']
    list_filter = ['is_active', 'is_default', 'tenant']


@admin.register(IntegrationSetting)
class IntegrationSettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'status', 'is_active', 'tenant']
    list_filter = ['provider', 'status', 'is_active', 'tenant']
    search_fields = ['name']


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp', 'tenant']
    list_filter = ['action', 'model_name', 'tenant']
    search_fields = ['model_name', 'object_repr']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address', 'timestamp']


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ['data_type', 'retention_days', 'action', 'is_active', 'tenant']
    list_filter = ['data_type', 'action', 'is_active', 'tenant']


@admin.register(BackupConfiguration)
class BackupConfigurationAdmin(admin.ModelAdmin):
    list_display = ['backup_type', 'frequency', 'retention_count', 'last_backup_at', 'is_active', 'tenant']
    list_filter = ['backup_type', 'frequency', 'is_active', 'tenant']


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ['backup_config', 'status', 'started_at', 'completed_at', 'initiated_by', 'tenant']
    list_filter = ['status', 'tenant']
    readonly_fields = ['backup_config', 'status', 'started_at', 'completed_at', 'file_path', 'file_size', 'error_message', 'initiated_by']
