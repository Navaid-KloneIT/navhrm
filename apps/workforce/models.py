from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


# ============================================================
# DEMAND FORECASTING
# ============================================================

class DemandForecast(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='demand_forecasts'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='demand_forecasts'
    )
    fiscal_year = models.CharField(max_length=20)
    current_headcount = models.PositiveIntegerField(default=0)
    projected_headcount = models.PositiveIntegerField(default=0)
    growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    justification = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        dept = self.department or 'No Dept'
        desig = self.designation or 'No Designation'
        return f"{dept} - {desig} ({self.fiscal_year})"

    @property
    def gap_count(self):
        return self.projected_headcount - self.current_headcount


# ============================================================
# SUPPLY ANALYSIS
# ============================================================

class SkillInventory(TenantAwareModel, TimeStampedModel):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='skill_inventories'
    )
    skill_name = models.CharField(max_length=255)
    proficiency_level = models.CharField(
        max_length=15, choices=PROFICIENCY_CHOICES, default='beginner'
    )
    years_of_experience = models.DecimalField(
        max_digits=4, decimal_places=1, default=0
    )
    certified = models.BooleanField(default=False)
    certification_expiry = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['employee', 'skill_name']
        unique_together = ['employee', 'skill_name', 'tenant']
        verbose_name_plural = 'Skill Inventories'

    def __str__(self):
        return f"{self.employee} - {self.skill_name} ({self.get_proficiency_level_display()})"


class TalentAvailability(TenantAwareModel, TimeStampedModel):
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='talent_availability'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='talent_availability'
    )
    available_count = models.PositiveIntegerField(default=0)
    on_notice_count = models.PositiveIntegerField(default=0)
    retiring_count = models.PositiveIntegerField(default=0)
    transfer_ready_count = models.PositiveIntegerField(default=0)
    period = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Talent Availabilities'

    def __str__(self):
        dept = self.department or 'No Dept'
        return f"{dept} - {self.period}"

    @property
    def total_at_risk(self):
        return self.on_notice_count + self.retiring_count


# ============================================================
# GAP ANALYSIS
# ============================================================

class WorkforceGap(TenantAwareModel, TimeStampedModel):
    GAP_TYPE_CHOICES = [
        ('surplus', 'Surplus'),
        ('deficit', 'Deficit'),
        ('balanced', 'Balanced'),
    ]
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('deferred', 'Deferred'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='workforce_gaps'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='workforce_gaps'
    )
    required_count = models.PositiveIntegerField(default=0)
    available_count = models.PositiveIntegerField(default=0)
    gap_type = models.CharField(
        max_length=10, choices=GAP_TYPE_CHOICES, default='balanced'
    )
    skills_gap_description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    action_plan = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='identified')
    fiscal_year = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        dept = self.department or 'No Dept'
        desig = self.designation or 'No Designation'
        return f"{dept} - {desig} ({self.get_gap_type_display()})"

    @property
    def gap_count(self):
        return self.required_count - self.available_count

    def save(self, *args, **kwargs):
        diff = self.required_count - self.available_count
        if diff > 0:
            self.gap_type = 'deficit'
        elif diff < 0:
            self.gap_type = 'surplus'
        else:
            self.gap_type = 'balanced'
        super().save(*args, **kwargs)


# ============================================================
# BUDGET PLANNING
# ============================================================

class HiringBudget(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hiring_budgets'
    )
    fiscal_year = models.CharField(max_length=20)
    allocated_budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    utilized_budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    positions_budgeted = models.PositiveIntegerField(default=0)
    positions_filled = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        dept = self.department or 'No Dept'
        return f"{dept} - {self.fiscal_year}"

    @property
    def remaining_budget(self):
        return self.allocated_budget - self.utilized_budget

    @property
    def utilization_percentage(self):
        if self.allocated_budget > 0:
            return round(float(self.utilized_budget) / float(self.allocated_budget) * 100, 1)
        return 0

    @property
    def positions_remaining(self):
        return self.positions_budgeted - self.positions_filled


class SalaryForecast(TenantAwareModel, TimeStampedModel):
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_forecasts'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_forecasts'
    )
    current_avg_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    projected_avg_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    increment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    effective_date = models.DateField(null=True, blank=True)
    fiscal_year = models.CharField(max_length=20)
    headcount = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        dept = self.department or 'No Dept'
        desig = self.designation or 'No Designation'
        return f"{dept} - {desig} ({self.fiscal_year})"

    @property
    def total_current_cost(self):
        return self.current_avg_salary * self.headcount

    @property
    def total_projected_cost(self):
        return self.projected_avg_salary * self.headcount

    @property
    def cost_impact(self):
        return self.total_projected_cost - self.total_current_cost


# ============================================================
# SCENARIO PLANNING
# ============================================================

class WorkforceScenario(TenantAwareModel, TimeStampedModel):
    SCENARIO_TYPE_CHOICES = [
        ('growth', 'Growth'),
        ('restructuring', 'Restructuring'),
        ('downsizing', 'Downsizing'),
        ('merger', 'Merger'),
        ('expansion', 'Expansion'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scenario_type = models.CharField(
        max_length=15, choices=SCENARIO_TYPE_CHOICES, default='growth'
    )
    base_year = models.CharField(max_length=20)
    projection_year = models.CharField(max_length=20)
    assumptions = models.TextField(blank=True)
    impact_summary = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_scenarios'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_scenario_type_display()})"

    @property
    def detail_count(self):
        return self.details.count()

    @property
    def total_cost_impact(self):
        return self.details.aggregate(
            total=models.Sum('cost_impact')
        )['total'] or 0


class ScenarioDetail(TenantAwareModel, TimeStampedModel):
    scenario = models.ForeignKey(
        WorkforceScenario, on_delete=models.CASCADE, related_name='details'
    )
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scenario_details'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scenario_details'
    )
    current_headcount = models.PositiveIntegerField(default=0)
    projected_headcount = models.PositiveIntegerField(default=0)
    cost_impact = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['department', 'designation']

    def __str__(self):
        dept = self.department or 'No Dept'
        return f"{self.scenario.name} - {dept}"

    @property
    def headcount_change(self):
        return self.projected_headcount - self.current_headcount


# ============================================================
# WORKFORCE ANALYTICS
# ============================================================

class ProductivityMetric(TenantAwareModel, TimeStampedModel):
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productivity_metrics'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productivity_metrics'
    )
    metric_name = models.CharField(max_length=255)
    metric_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    measurement_period = models.CharField(max_length=20)
    measurement_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-measurement_date']

    def __str__(self):
        return f"{self.metric_name} - {self.measurement_period}"

    @property
    def variance(self):
        return self.metric_value - self.target_value

    @property
    def achievement_percentage(self):
        if self.target_value > 0:
            return round(float(self.metric_value) / float(self.target_value) * 100, 1)
        return 0


class UtilizationRate(TenantAwareModel, TimeStampedModel):
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='utilization_rates'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='utilization_rates'
    )
    period = models.CharField(max_length=20)
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    productive_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    billable_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    non_billable_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        name = self.employee or self.department or 'Unknown'
        return f"{name} - {self.period}"

    @property
    def utilization_percentage(self):
        if self.total_hours > 0:
            return round(float(self.productive_hours) / float(self.total_hours) * 100, 1)
        return 0

    @property
    def billable_percentage(self):
        if self.total_hours > 0:
            return round(float(self.billable_hours) / float(self.total_hours) * 100, 1)
        return 0
