import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import TenantAwareModel, TimeStampedModel, get_current_tenant


# ===========================================================================
# Salary Benchmarking Models
# ===========================================================================

class SalaryBenchmark(TenantAwareModel, TimeStampedModel):
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_benchmarks'
    )
    job_title = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    median_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    percentile_25 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    percentile_75 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='INR')
    source = models.CharField(max_length=255, blank=True)
    effective_date = models.DateField()
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.job_title} - {self.location}"


# ===========================================================================
# Benefits Administration Models
# ===========================================================================

class BenefitPlan(TenantAwareModel, TimeStampedModel):
    PLAN_TYPE_CHOICES = [
        ('health_insurance', 'Health Insurance'),
        ('life_insurance', 'Life Insurance'),
        ('dental', 'Dental'),
        ('vision', 'Vision'),
        ('retirement', 'Retirement'),
        ('disability', 'Disability'),
        ('wellness', 'Wellness'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='health_insurance')
    provider = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    coverage_details = models.TextField(blank=True)
    premium_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premium_employer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    eligibility_criteria = models.TextField(blank=True)
    enrollment_start = models.DateField(null=True, blank=True)
    enrollment_end = models.DateField(null=True, blank=True)
    effective_start = models.DateField(null=True, blank=True)
    effective_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_premium(self):
        return self.premium_employee + self.premium_employer

    @property
    def is_enrollment_open(self):
        today = timezone.now().date()
        if self.enrollment_start and self.enrollment_end:
            return self.enrollment_start <= today <= self.enrollment_end
        return False


class EmployeeBenefit(TenantAwareModel, TimeStampedModel):
    COVERAGE_LEVEL_CHOICES = [
        ('employee_only', 'Employee Only'),
        ('employee_spouse', 'Employee + Spouse'),
        ('employee_children', 'Employee + Children'),
        ('family', 'Family'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='employee_benefits'
    )
    benefit_plan = models.ForeignKey(
        BenefitPlan, on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrollment_date = models.DateField()
    coverage_level = models.CharField(
        max_length=20, choices=COVERAGE_LEVEL_CHOICES, default='employee_only'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    nominated_dependents = models.TextField(blank=True)
    policy_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.employee} - {self.benefit_plan.name}"


# ===========================================================================
# Flexible Benefits Models
# ===========================================================================

class FlexBenefitPlan(TenantAwareModel, TimeStampedModel):
    ALLOCATION_TYPE_CHOICES = [
        ('amount', 'Amount'),
        ('points', 'Points'),
    ]
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_allocation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allocation_type = models.CharField(
        max_length=10, choices=ALLOCATION_TYPE_CHOICES, default='amount'
    )
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='annual')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FlexBenefitOption(TenantAwareModel, TimeStampedModel):
    flex_plan = models.ForeignKey(
        FlexBenefitPlan, on_delete=models.CASCADE,
        related_name='options'
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.flex_plan.name})"


class EmployeeFlexSelection(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('selected', 'Selected'),
        ('opted_out', 'Opted Out'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='flex_selections'
    )
    flex_plan = models.ForeignKey(
        FlexBenefitPlan, on_delete=models.CASCADE,
        related_name='selections'
    )
    flex_option = models.ForeignKey(
        FlexBenefitOption, on_delete=models.CASCADE,
        related_name='selections'
    )
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='selected')
    selected_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-selected_date']

    def __str__(self):
        return f"{self.employee} - {self.flex_option.name}"


# ===========================================================================
# Stock/ESOP Management Models
# ===========================================================================

class EquityGrant(TenantAwareModel, TimeStampedModel):
    GRANT_TYPE_CHOICES = [
        ('esop', 'ESOP'),
        ('rsu', 'RSU'),
        ('stock_option', 'Stock Option'),
        ('phantom_stock', 'Phantom Stock'),
    ]
    VESTING_SCHEDULE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('cliff', 'Cliff'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('partially_vested', 'Partially Vested'),
        ('fully_vested', 'Fully Vested'),
        ('exercised', 'Exercised'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='equity_grants'
    )
    grant_number = models.CharField(max_length=50, unique=True, editable=False)
    grant_type = models.CharField(max_length=20, choices=GRANT_TYPE_CHOICES, default='esop')
    grant_date = models.DateField()
    total_shares = models.IntegerField(default=0)
    exercise_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_value_per_share = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vesting_start_date = models.DateField()
    vesting_end_date = models.DateField()
    vesting_schedule = models.CharField(
        max_length=10, choices=VESTING_SCHEDULE_CHOICES, default='annual'
    )
    cliff_months = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-grant_date']

    def __str__(self):
        return f"{self.grant_number} - {self.employee}"

    def save(self, *args, **kwargs):
        if not self.grant_number:
            self.grant_number = f"EQG-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_vested_shares(self):
        return self.vesting_events.filter(is_vested=True).aggregate(
            total=models.Sum('shares_vested')
        )['total'] or 0

    @property
    def unvested_shares(self):
        return self.total_shares - self.total_vested_shares

    @property
    def total_exercised_shares(self):
        return self.exercise_records.filter(status='completed').aggregate(
            total=models.Sum('shares_exercised')
        )['total'] or 0


class VestingEvent(TenantAwareModel, TimeStampedModel):
    equity_grant = models.ForeignKey(
        EquityGrant, on_delete=models.CASCADE,
        related_name='vesting_events'
    )
    vesting_date = models.DateField()
    shares_vested = models.IntegerField(default=0)
    is_vested = models.BooleanField(default=False)
    vested_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['vesting_date']

    def __str__(self):
        return f"{self.equity_grant.grant_number} - {self.vesting_date} ({self.shares_vested} shares)"


class ExerciseRecord(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    equity_grant = models.ForeignKey(
        EquityGrant, on_delete=models.CASCADE,
        related_name='exercise_records'
    )
    exercise_date = models.DateField()
    shares_exercised = models.IntegerField(default=0)
    exercise_price_per_share = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    market_price_per_share = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-exercise_date']

    def __str__(self):
        return f"{self.equity_grant.grant_number} - {self.shares_exercised} shares on {self.exercise_date}"

    @property
    def profit_per_share(self):
        return self.market_price_per_share - self.exercise_price_per_share


# ===========================================================================
# Compensation Planning Models
# ===========================================================================

class CompensationPlan(TenantAwareModel, TimeStampedModel):
    PLAN_TYPE_CHOICES = [
        ('merit_increase', 'Merit Increase'),
        ('promotion', 'Promotion'),
        ('market_adjustment', 'Market Adjustment'),
        ('annual_review', 'Annual Review'),
        ('special', 'Special'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='annual_review')
    fiscal_year = models.CharField(max_length=20)
    budget_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    budget_utilized = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_compensation_plans'
    )

    class Meta:
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"{self.name} ({self.fiscal_year})"

    @property
    def budget_remaining(self):
        return self.budget_amount - self.budget_utilized

    @property
    def utilization_percentage(self):
        if self.budget_amount > 0:
            return round((self.budget_utilized / self.budget_amount) * 100, 1)
        return 0


class CompensationRecommendation(TenantAwareModel, TimeStampedModel):
    INCREASE_TYPE_CHOICES = [
        ('merit', 'Merit'),
        ('promotion', 'Promotion'),
        ('market_adjustment', 'Market Adjustment'),
        ('retention', 'Retention'),
        ('equity', 'Equity'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]

    compensation_plan = models.ForeignKey(
        CompensationPlan, on_delete=models.CASCADE,
        related_name='recommendations'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='compensation_recommendations'
    )
    current_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    recommended_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    increase_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    increase_type = models.CharField(
        max_length=20, choices=INCREASE_TYPE_CHOICES, default='merit'
    )
    justification = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_recommendations'
    )
    implemented_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.get_increase_type_display()} ({self.increase_percentage}%)"


# ===========================================================================
# Rewards & Recognition Models
# ===========================================================================

class RewardProgram(TenantAwareModel, TimeStampedModel):
    PROGRAM_TYPE_CHOICES = [
        ('spot_award', 'Spot Award'),
        ('service_award', 'Service Award'),
        ('peer_recognition', 'Peer Recognition'),
        ('performance_bonus', 'Performance Bonus'),
        ('team_award', 'Team Award'),
    ]

    name = models.CharField(max_length=255)
    program_type = models.CharField(
        max_length=20, choices=PROGRAM_TYPE_CHOICES, default='spot_award'
    )
    description = models.TextField(blank=True)
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_utilized = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reward_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_monetary = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def budget_remaining(self):
        return self.budget_amount - self.budget_utilized


class Recognition(TenantAwareModel, TimeStampedModel):
    RECOGNITION_TYPE_CHOICES = [
        ('spot_award', 'Spot Award'),
        ('service_award', 'Service Award'),
        ('peer_recognition', 'Peer Recognition'),
        ('achievement', 'Achievement'),
        ('innovation', 'Innovation'),
        ('leadership', 'Leadership'),
        ('teamwork', 'Teamwork'),
    ]
    STATUS_CHOICES = [
        ('nominated', 'Nominated'),
        ('approved', 'Approved'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
    ]

    reward_program = models.ForeignKey(
        RewardProgram, on_delete=models.CASCADE,
        related_name='recognitions'
    )
    nominee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='recognitions_received'
    )
    nominator = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='recognitions_given'
    )
    recognition_type = models.CharField(
        max_length=20, choices=RECOGNITION_TYPE_CHOICES, default='spot_award'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    reward_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nominated')
    awarded_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_recognitions'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.nominee}"
