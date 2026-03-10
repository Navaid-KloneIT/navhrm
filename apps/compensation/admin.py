from django.contrib import admin
from .models import (
    SalaryBenchmark,
    BenefitPlan, EmployeeBenefit,
    FlexBenefitPlan, FlexBenefitOption, EmployeeFlexSelection,
    EquityGrant, VestingEvent, ExerciseRecord,
    CompensationPlan, CompensationRecommendation,
    RewardProgram, Recognition,
)


# ===========================================================================
# Salary Benchmarking Admin
# ===========================================================================

@admin.register(SalaryBenchmark)
class SalaryBenchmarkAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'designation', 'location', 'median_salary', 'effective_date', 'is_active', 'tenant']
    list_filter = ['is_active', 'currency', 'tenant']
    search_fields = ['job_title', 'location', 'industry']


# ===========================================================================
# Benefits Administration Admin
# ===========================================================================

@admin.register(BenefitPlan)
class BenefitPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'provider', 'premium_employee', 'premium_employer', 'is_active', 'tenant']
    list_filter = ['plan_type', 'is_active', 'tenant']
    search_fields = ['name', 'provider']


@admin.register(EmployeeBenefit)
class EmployeeBenefitAdmin(admin.ModelAdmin):
    list_display = ['employee', 'benefit_plan', 'coverage_level', 'enrollment_date', 'status', 'tenant']
    list_filter = ['coverage_level', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'policy_number']


# ===========================================================================
# Flexible Benefits Admin
# ===========================================================================

@admin.register(FlexBenefitPlan)
class FlexBenefitPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_allocation', 'allocation_type', 'period', 'is_active', 'tenant']
    list_filter = ['allocation_type', 'period', 'is_active', 'tenant']
    search_fields = ['name']


@admin.register(FlexBenefitOption)
class FlexBenefitOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'flex_plan', 'category', 'cost', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'category']


@admin.register(EmployeeFlexSelection)
class EmployeeFlexSelectionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'flex_plan', 'flex_option', 'status', 'selected_date', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


# ===========================================================================
# Stock/ESOP Management Admin
# ===========================================================================

@admin.register(EquityGrant)
class EquityGrantAdmin(admin.ModelAdmin):
    list_display = ['grant_number', 'employee', 'grant_type', 'total_shares', 'grant_date', 'status', 'tenant']
    list_filter = ['grant_type', 'status', 'vesting_schedule', 'tenant']
    search_fields = ['grant_number', 'employee__first_name', 'employee__last_name']


@admin.register(VestingEvent)
class VestingEventAdmin(admin.ModelAdmin):
    list_display = ['equity_grant', 'vesting_date', 'shares_vested', 'is_vested', 'tenant']
    list_filter = ['is_vested', 'tenant']


@admin.register(ExerciseRecord)
class ExerciseRecordAdmin(admin.ModelAdmin):
    list_display = ['equity_grant', 'exercise_date', 'shares_exercised', 'total_value', 'status', 'tenant']
    list_filter = ['status', 'tenant']


# ===========================================================================
# Compensation Planning Admin
# ===========================================================================

@admin.register(CompensationPlan)
class CompensationPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'fiscal_year', 'budget_amount', 'budget_utilized', 'status', 'tenant']
    list_filter = ['plan_type', 'status', 'tenant']
    search_fields = ['name', 'fiscal_year']


@admin.register(CompensationRecommendation)
class CompensationRecommendationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'compensation_plan', 'current_salary', 'recommended_salary', 'increase_percentage', 'status', 'tenant']
    list_filter = ['increase_type', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


# ===========================================================================
# Rewards & Recognition Admin
# ===========================================================================

@admin.register(RewardProgram)
class RewardProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'program_type', 'budget_amount', 'reward_value', 'is_monetary', 'is_active', 'tenant']
    list_filter = ['program_type', 'is_monetary', 'is_active', 'tenant']
    search_fields = ['name']


@admin.register(Recognition)
class RecognitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'nominee', 'nominator', 'recognition_type', 'reward_value', 'status', 'tenant']
    list_filter = ['recognition_type', 'status', 'tenant']
    search_fields = ['title', 'nominee__first_name', 'nominee__last_name']
