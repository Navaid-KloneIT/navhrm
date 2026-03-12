from django.contrib import admin
from .models import (
    DemandForecast, SkillInventory, TalentAvailability,
    WorkforceGap, HiringBudget, SalaryForecast,
    WorkforceScenario, ScenarioDetail,
    ProductivityMetric, UtilizationRate,
)


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ['department', 'designation', 'fiscal_year', 'current_headcount', 'projected_headcount', 'status', 'priority', 'tenant']
    list_filter = ['status', 'priority', 'tenant']
    search_fields = ['department__name', 'designation__name', 'fiscal_year']


@admin.register(SkillInventory)
class SkillInventoryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'skill_name', 'proficiency_level', 'years_of_experience', 'certified', 'is_active', 'tenant']
    list_filter = ['proficiency_level', 'certified', 'is_active', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'skill_name']


@admin.register(TalentAvailability)
class TalentAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['department', 'designation', 'available_count', 'on_notice_count', 'retiring_count', 'period', 'tenant']
    list_filter = ['tenant']
    search_fields = ['department__name', 'designation__name', 'period']


@admin.register(WorkforceGap)
class WorkforceGapAdmin(admin.ModelAdmin):
    list_display = ['department', 'designation', 'required_count', 'available_count', 'gap_type', 'priority', 'status', 'tenant']
    list_filter = ['gap_type', 'status', 'priority', 'tenant']
    search_fields = ['department__name', 'designation__name', 'fiscal_year']


@admin.register(HiringBudget)
class HiringBudgetAdmin(admin.ModelAdmin):
    list_display = ['department', 'fiscal_year', 'allocated_budget', 'utilized_budget', 'positions_budgeted', 'positions_filled', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['department__name', 'fiscal_year']


@admin.register(SalaryForecast)
class SalaryForecastAdmin(admin.ModelAdmin):
    list_display = ['department', 'designation', 'current_avg_salary', 'projected_avg_salary', 'increment_percentage', 'fiscal_year', 'tenant']
    list_filter = ['tenant']
    search_fields = ['department__name', 'designation__name', 'fiscal_year']


@admin.register(WorkforceScenario)
class WorkforceScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario_type', 'base_year', 'projection_year', 'status', 'created_by', 'tenant']
    list_filter = ['scenario_type', 'status', 'tenant']
    search_fields = ['name']


@admin.register(ScenarioDetail)
class ScenarioDetailAdmin(admin.ModelAdmin):
    list_display = ['scenario', 'department', 'designation', 'current_headcount', 'projected_headcount', 'cost_impact', 'tenant']
    list_filter = ['tenant']
    search_fields = ['scenario__name', 'department__name', 'designation__name']


@admin.register(ProductivityMetric)
class ProductivityMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'department', 'employee', 'metric_value', 'target_value', 'measurement_period', 'measurement_date', 'tenant']
    list_filter = ['tenant']
    search_fields = ['metric_name', 'department__name', 'employee__first_name', 'employee__last_name']


@admin.register(UtilizationRate)
class UtilizationRateAdmin(admin.ModelAdmin):
    list_display = ['department', 'employee', 'period', 'total_hours', 'productive_hours', 'billable_hours', 'tenant']
    list_filter = ['tenant']
    search_fields = ['department__name', 'employee__first_name', 'employee__last_name', 'period']
