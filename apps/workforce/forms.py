from django import forms
from apps.employees.models import Employee
from apps.organization.models import Department, Designation
from .models import (
    DemandForecast, SkillInventory, TalentAvailability,
    WorkforceGap, HiringBudget, SalaryForecast,
    WorkforceScenario, ScenarioDetail,
    ProductivityMetric, UtilizationRate,
)


# ===========================================================================
# Demand Forecasting Forms
# ===========================================================================

class DemandForecastForm(forms.ModelForm):
    class Meta:
        model = DemandForecast
        fields = [
            'department', 'designation', 'fiscal_year',
            'current_headcount', 'projected_headcount', 'growth_rate',
            'justification', 'status', 'priority',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'fiscal_year': forms.TextInput(attrs={'class': 'form-control'}),
            'current_headcount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'projected_headcount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'growth_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)


# ===========================================================================
# Supply Analysis Forms
# ===========================================================================

class SkillInventoryForm(forms.ModelForm):
    class Meta:
        model = SkillInventory
        fields = [
            'employee', 'skill_name', 'proficiency_level',
            'years_of_experience', 'certified', 'certification_expiry',
            'is_active',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'skill_name': forms.TextInput(attrs={'class': 'form-control'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'certification_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class TalentAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TalentAvailability
        fields = [
            'department', 'designation', 'available_count',
            'on_notice_count', 'retiring_count', 'transfer_ready_count',
            'period', 'notes',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'available_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'on_notice_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'retiring_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'transfer_ready_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)


# ===========================================================================
# Gap Analysis Forms
# ===========================================================================

class WorkforceGapForm(forms.ModelForm):
    class Meta:
        model = WorkforceGap
        fields = [
            'department', 'designation', 'required_count',
            'available_count', 'skills_gap_description', 'priority',
            'action_plan', 'status', 'fiscal_year',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'required_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'available_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'skills_gap_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'action_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'fiscal_year': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)


# ===========================================================================
# Budget Planning Forms
# ===========================================================================

class HiringBudgetForm(forms.ModelForm):
    class Meta:
        model = HiringBudget
        fields = [
            'department', 'fiscal_year', 'allocated_budget',
            'utilized_budget', 'positions_budgeted', 'positions_filled',
            'status', 'notes',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'fiscal_year': forms.TextInput(attrs={'class': 'form-control'}),
            'allocated_budget': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'utilized_budget': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'positions_budgeted': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'positions_filled': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)


class SalaryForecastForm(forms.ModelForm):
    class Meta:
        model = SalaryForecast
        fields = [
            'department', 'designation', 'current_avg_salary',
            'projected_avg_salary', 'increment_percentage',
            'effective_date', 'fiscal_year', 'headcount', 'notes',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'current_avg_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'projected_avg_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'increment_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fiscal_year': forms.TextInput(attrs={'class': 'form-control'}),
            'headcount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)


# ===========================================================================
# Scenario Planning Forms
# ===========================================================================

class WorkforceScenarioForm(forms.ModelForm):
    class Meta:
        model = WorkforceScenario
        fields = [
            'name', 'description', 'scenario_type',
            'base_year', 'projection_year', 'assumptions',
            'impact_summary', 'status', 'created_by',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scenario_type': forms.Select(attrs={'class': 'form-select'}),
            'base_year': forms.TextInput(attrs={'class': 'form-control'}),
            'projection_year': forms.TextInput(attrs={'class': 'form-control'}),
            'assumptions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'impact_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'created_by': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['created_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['created_by'].required = False


class ScenarioDetailForm(forms.ModelForm):
    class Meta:
        model = ScenarioDetail
        fields = [
            'department', 'designation', 'current_headcount',
            'projected_headcount', 'cost_impact', 'notes',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'current_headcount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'projected_headcount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cost_impact': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)


# ===========================================================================
# Workforce Analytics Forms
# ===========================================================================

class ProductivityMetricForm(forms.ModelForm):
    class Meta:
        model = ProductivityMetric
        fields = [
            'department', 'employee', 'metric_name',
            'metric_value', 'target_value', 'measurement_period',
            'measurement_date', 'notes',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'metric_name': forms.TextInput(attrs={'class': 'form-control'}),
            'metric_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'measurement_period': forms.TextInput(attrs={'class': 'form-control'}),
            'measurement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class UtilizationRateForm(forms.ModelForm):
    class Meta:
        model = UtilizationRate
        fields = [
            'department', 'employee', 'period',
            'total_hours', 'productive_hours', 'billable_hours',
            'non_billable_hours', 'notes',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'total_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'productive_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'billable_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'non_billable_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
