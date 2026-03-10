from django import forms
from apps.employees.models import Employee
from apps.organization.models import Designation
from .models import (
    SalaryBenchmark,
    BenefitPlan, EmployeeBenefit,
    FlexBenefitPlan, FlexBenefitOption, EmployeeFlexSelection,
    EquityGrant, VestingEvent, ExerciseRecord,
    CompensationPlan, CompensationRecommendation,
    RewardProgram, Recognition,
)


# ===========================================================================
# Salary Benchmarking Forms
# ===========================================================================

class SalaryBenchmarkForm(forms.ModelForm):
    class Meta:
        model = SalaryBenchmark
        fields = [
            'designation', 'job_title', 'industry', 'location',
            'min_salary', 'median_salary', 'max_salary',
            'percentile_25', 'percentile_75', 'currency',
            'source', 'effective_date', 'notes', 'is_active',
        ]
        widgets = {
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'median_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'max_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'percentile_25': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'percentile_75': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant)
        self.fields['designation'].required = False


# ===========================================================================
# Benefits Administration Forms
# ===========================================================================

class BenefitPlanForm(forms.ModelForm):
    class Meta:
        model = BenefitPlan
        fields = [
            'name', 'plan_type', 'provider', 'description', 'coverage_details',
            'premium_employee', 'premium_employer', 'eligibility_criteria',
            'enrollment_start', 'enrollment_end', 'effective_start', 'effective_end', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_type': forms.Select(attrs={'class': 'form-select'}),
            'provider': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'coverage_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'premium_employee': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'premium_employer': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'eligibility_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'enrollment_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'enrollment_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'effective_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'effective_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class EmployeeBenefitForm(forms.ModelForm):
    class Meta:
        model = EmployeeBenefit
        fields = [
            'employee', 'benefit_plan', 'enrollment_date', 'coverage_level',
            'status', 'nominated_dependents', 'policy_number', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'benefit_plan': forms.Select(attrs={'class': 'form-select'}),
            'enrollment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'coverage_level': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'nominated_dependents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['benefit_plan'].queryset = BenefitPlan.all_objects.filter(tenant=tenant, is_active=True)


# ===========================================================================
# Flexible Benefits Forms
# ===========================================================================

class FlexBenefitPlanForm(forms.ModelForm):
    class Meta:
        model = FlexBenefitPlan
        fields = ['name', 'description', 'total_allocation', 'allocation_type', 'period', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_allocation': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'allocation_type': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
        }


class FlexBenefitOptionForm(forms.ModelForm):
    class Meta:
        model = FlexBenefitOption
        fields = ['flex_plan', 'name', 'category', 'description', 'cost', 'is_active']
        widgets = {
            'flex_plan': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['flex_plan'].queryset = FlexBenefitPlan.all_objects.filter(tenant=tenant, is_active=True)


class EmployeeFlexSelectionForm(forms.ModelForm):
    class Meta:
        model = EmployeeFlexSelection
        fields = ['employee', 'flex_plan', 'flex_option', 'period_start', 'period_end', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'flex_plan': forms.Select(attrs={'class': 'form-select'}),
            'flex_option': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['flex_plan'].queryset = FlexBenefitPlan.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['flex_option'].queryset = FlexBenefitOption.all_objects.filter(tenant=tenant, is_active=True)


# ===========================================================================
# Stock/ESOP Management Forms
# ===========================================================================

class EquityGrantForm(forms.ModelForm):
    class Meta:
        model = EquityGrant
        fields = [
            'employee', 'grant_type', 'grant_date', 'total_shares',
            'exercise_price', 'current_value_per_share',
            'vesting_start_date', 'vesting_end_date', 'vesting_schedule',
            'cliff_months', 'status', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'grant_type': forms.Select(attrs={'class': 'form-select'}),
            'grant_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_shares': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'exercise_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'current_value_per_share': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'vesting_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vesting_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vesting_schedule': forms.Select(attrs={'class': 'form-select'}),
            'cliff_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class VestingEventForm(forms.ModelForm):
    class Meta:
        model = VestingEvent
        fields = ['vesting_date', 'shares_vested', 'is_vested']
        widgets = {
            'vesting_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shares_vested': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class ExerciseRecordForm(forms.ModelForm):
    class Meta:
        model = ExerciseRecord
        fields = [
            'exercise_date', 'shares_exercised', 'exercise_price_per_share',
            'market_price_per_share', 'total_value', 'status',
        ]
        widgets = {
            'exercise_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shares_exercised': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'exercise_price_per_share': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'market_price_per_share': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'total_value': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


# ===========================================================================
# Compensation Planning Forms
# ===========================================================================

class CompensationPlanForm(forms.ModelForm):
    class Meta:
        model = CompensationPlan
        fields = [
            'name', 'plan_type', 'fiscal_year', 'budget_amount',
            'effective_date', 'end_date', 'description', 'status',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_type': forms.Select(attrs={'class': 'form-select'}),
            'fiscal_year': forms.TextInput(attrs={'class': 'form-control'}),
            'budget_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CompensationRecommendationForm(forms.ModelForm):
    class Meta:
        model = CompensationRecommendation
        fields = [
            'compensation_plan', 'employee', 'current_salary', 'recommended_salary',
            'increase_percentage', 'increase_type', 'justification', 'status',
        ]
        widgets = {
            'compensation_plan': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'current_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'recommended_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'increase_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'increase_type': forms.Select(attrs={'class': 'form-select'}),
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['compensation_plan'].queryset = CompensationPlan.all_objects.filter(tenant=tenant)
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


# ===========================================================================
# Rewards & Recognition Forms
# ===========================================================================

class RewardProgramForm(forms.ModelForm):
    class Meta:
        model = RewardProgram
        fields = [
            'name', 'program_type', 'description', 'budget_amount',
            'reward_value', 'is_monetary', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'program_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'budget_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'reward_value': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }


class RecognitionForm(forms.ModelForm):
    class Meta:
        model = Recognition
        fields = [
            'reward_program', 'nominee', 'nominator', 'recognition_type',
            'title', 'description', 'reward_value',
        ]
        widgets = {
            'reward_program': forms.Select(attrs={'class': 'form-select'}),
            'nominee': forms.Select(attrs={'class': 'form-select'}),
            'nominator': forms.Select(attrs={'class': 'form-select'}),
            'recognition_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reward_value': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['reward_program'].queryset = RewardProgram.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['nominee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['nominator'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
