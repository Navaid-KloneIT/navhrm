from django import forms
from apps.employees.models import Employee
from apps.organization.models import Department, Designation
from apps.accounts.models import User
from .models import (
    AssetCategory, Asset, AssetAllocation, AssetMaintenance,
    ExpenseCategory, ExpensePolicy, ExpenseClaim,
    TravelPolicy, TravelRequest, TravelExpense, TravelSettlement,
    TicketCategory, Ticket, TicketComment, KnowledgeBase,
)


# ===========================================================================
# Asset Management Forms
# ===========================================================================

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_id', 'name', 'category', 'serial_number', 'purchase_date',
            'purchase_cost', 'warranty_expiry', 'condition', 'status', 'location', 'notes',
        ]
        widgets = {
            'asset_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['category'].queryset = AssetCategory.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['category'].required = False


class AssetAllocationForm(forms.ModelForm):
    class Meta:
        model = AssetAllocation
        fields = [
            'asset', 'employee', 'allocated_date', 'expected_return_date',
            'condition_at_allocation', 'notes',
        ]
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'allocated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'condition_at_allocation': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['asset'].queryset = Asset.all_objects.filter(tenant=tenant, status='available')
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['expected_return_date'].required = False
        self.fields['condition_at_allocation'].required = False


class AssetReturnForm(forms.ModelForm):
    class Meta:
        model = AssetAllocation
        fields = ['actual_return_date', 'condition_at_return', 'notes']
        widgets = {
            'actual_return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'condition_at_return': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AssetMaintenanceForm(forms.ModelForm):
    class Meta:
        model = AssetMaintenance
        fields = [
            'asset', 'maintenance_type', 'description', 'scheduled_date',
            'completed_date', 'cost', 'vendor', 'status', 'notes',
        ]
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['asset'].queryset = Asset.all_objects.filter(tenant=tenant)


# ===========================================================================
# Expense Management Forms
# ===========================================================================

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'max_limit', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }


class ExpensePolicyForm(forms.ModelForm):
    class Meta:
        model = ExpensePolicy
        fields = [
            'name', 'description', 'applies_to', 'department', 'designation',
            'max_amount', 'requires_receipt_above', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'applies_to': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'max_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'requires_receipt_above': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant)
        self.fields['department'].required = False
        self.fields['designation'].required = False


class ExpenseClaimForm(forms.ModelForm):
    class Meta:
        model = ExpenseClaim
        fields = [
            'employee', 'title', 'category', 'amount', 'receipt',
            'expense_date', 'description',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['category'].queryset = ExpenseCategory.all_objects.filter(tenant=tenant, is_active=True)
        self.fields['category'].required = False


# ===========================================================================
# Travel Management Forms
# ===========================================================================

class TravelPolicyForm(forms.ModelForm):
    class Meta:
        model = TravelPolicy
        fields = ['name', 'description', 'travel_class', 'daily_allowance', 'hotel_limit', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'travel_class': forms.Select(attrs={'class': 'form-select'}),
            'daily_allowance': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'hotel_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }


class TravelRequestForm(forms.ModelForm):
    class Meta:
        model = TravelRequest
        fields = [
            'employee', 'purpose', 'travel_type', 'from_location', 'to_location',
            'departure_date', 'return_date', 'estimated_cost',
            'advance_required', 'advance_amount', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'travel_type': forms.Select(attrs={'class': 'form-select'}),
            'from_location': forms.TextInput(attrs={'class': 'form-control'}),
            'to_location': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'advance_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class TravelExpenseForm(forms.ModelForm):
    class Meta:
        model = TravelExpense
        fields = ['expense_type', 'amount', 'receipt', 'description', 'date']
        widgets = {
            'expense_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class TravelSettlementForm(forms.ModelForm):
    class Meta:
        model = TravelSettlement
        fields = ['total_expenses', 'advance_given', 'settlement_amount', 'status', 'settled_date', 'notes']
        widgets = {
            'total_expenses': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'advance_given': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'settlement_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'settled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ===========================================================================
# Helpdesk Forms
# ===========================================================================

class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = [
            'name', 'description', 'department', 'default_assignee',
            'sla_response_hours', 'sla_resolution_hours', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'default_assignee': forms.Select(attrs={'class': 'form-select'}),
            'sla_response_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'sla_resolution_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant)
            self.fields['default_assignee'].queryset = User.objects.filter(tenant=tenant)
        self.fields['department'].required = False
        self.fields['default_assignee'].required = False


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'employee', 'category', 'subject', 'description',
            'priority', 'status', 'assigned_to',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['category'].queryset = TicketCategory.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['assigned_to'].queryset = User.objects.filter(tenant=tenant)
        self.fields['category'].required = False
        self.fields['assigned_to'].required = False


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['comment', 'is_internal', 'attachment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class KnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBase
        fields = ['title', 'category', 'content', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['category'].queryset = TicketCategory.all_objects.filter(tenant=tenant, is_active=True)
        self.fields['category'].required = False
