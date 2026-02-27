from django.contrib import admin
from .models import (
    AssetCategory, Asset, AssetAllocation, AssetMaintenance,
    ExpenseCategory, ExpensePolicy, ExpenseClaim,
    TravelPolicy, TravelRequest, TravelExpense, TravelSettlement,
    TicketCategory, Ticket, TicketComment, KnowledgeBase,
)


# ===========================================================================
# Asset Management Admin
# ===========================================================================

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'name', 'category', 'condition', 'status', 'tenant']
    list_filter = ['condition', 'status', 'tenant']
    search_fields = ['asset_id', 'name', 'serial_number']


@admin.register(AssetAllocation)
class AssetAllocationAdmin(admin.ModelAdmin):
    list_display = ['asset', 'employee', 'allocated_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['asset__name', 'employee__first_name', 'employee__last_name']


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['asset', 'maintenance_type', 'scheduled_date', 'status', 'cost', 'tenant']
    list_filter = ['maintenance_type', 'status', 'tenant']
    search_fields = ['asset__name', 'vendor']


# ===========================================================================
# Expense Management Admin
# ===========================================================================

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_limit', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name']


@admin.register(ExpensePolicy)
class ExpensePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'applies_to', 'max_amount', 'is_active', 'tenant']
    list_filter = ['applies_to', 'is_active', 'tenant']
    search_fields = ['name']


@admin.register(ExpenseClaim)
class ExpenseClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_number', 'employee', 'title', 'amount', 'status', 'expense_date', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['claim_number', 'title', 'employee__first_name', 'employee__last_name']


# ===========================================================================
# Travel Management Admin
# ===========================================================================

@admin.register(TravelPolicy)
class TravelPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'travel_class', 'daily_allowance', 'hotel_limit', 'is_active', 'tenant']
    list_filter = ['travel_class', 'is_active', 'tenant']
    search_fields = ['name']


@admin.register(TravelRequest)
class TravelRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'employee', 'travel_type', 'from_location', 'to_location', 'status', 'tenant']
    list_filter = ['travel_type', 'status', 'tenant']
    search_fields = ['request_number', 'employee__first_name', 'employee__last_name']


@admin.register(TravelExpense)
class TravelExpenseAdmin(admin.ModelAdmin):
    list_display = ['travel_request', 'expense_type', 'amount', 'date', 'tenant']
    list_filter = ['expense_type', 'tenant']


@admin.register(TravelSettlement)
class TravelSettlementAdmin(admin.ModelAdmin):
    list_display = ['travel_request', 'total_expenses', 'advance_given', 'settlement_amount', 'status', 'tenant']
    list_filter = ['status', 'tenant']


# ===========================================================================
# Helpdesk Admin
# ===========================================================================

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'sla_response_hours', 'sla_resolution_hours', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'employee', 'subject', 'priority', 'status', 'assigned_to', 'tenant']
    list_filter = ['priority', 'status', 'tenant']
    search_fields = ['ticket_number', 'subject', 'employee__first_name', 'employee__last_name']


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'is_internal', 'created_at', 'tenant']
    list_filter = ['is_internal', 'tenant']


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'view_count', 'tenant']
    list_filter = ['is_published', 'tenant']
    search_fields = ['title']
