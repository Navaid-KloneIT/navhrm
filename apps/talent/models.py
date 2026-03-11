from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


# ===========================================================================
# Talent Pool Models
# ===========================================================================

class TalentAssessment(TenantAwareModel, TimeStampedModel):
    PERFORMANCE_RATING_CHOICES = [
        (1, '1 - Below Expectations'),
        (2, '2 - Needs Improvement'),
        (3, '3 - Meets Expectations'),
        (4, '4 - Exceeds Expectations'),
        (5, '5 - Outstanding'),
    ]
    POTENTIAL_RATING_CHOICES = [
        (1, '1 - Low Potential'),
        (2, '2 - Below Average Potential'),
        (3, '3 - Average Potential'),
        (4, '4 - High Potential'),
        (5, '5 - Exceptional Potential'),
    ]
    CATEGORY_CHOICES = [
        ('high_potential', 'High Potential'),
        ('key_talent', 'Key Talent'),
        ('solid_performer', 'Solid Performer'),
        ('emerging_talent', 'Emerging Talent'),
        ('inconsistent_performer', 'Inconsistent Performer'),
        ('underperformer', 'Underperformer'),
        ('new_to_role', 'New to Role'),
        ('risk_of_stagnation', 'Risk of Stagnation'),
        ('misplaced_talent', 'Misplaced Talent'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='talent_assessments'
    )
    performance_rating = models.IntegerField(choices=PERFORMANCE_RATING_CHOICES)
    potential_rating = models.IntegerField(choices=POTENTIAL_RATING_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, blank=True)
    assessment_date = models.DateField()
    assessed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='talent_assessments_given'
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-assessment_date']

    def __str__(self):
        return f"{self.employee} - {self.get_category_display()} ({self.assessment_date})"

    def save(self, *args, **kwargs):
        self.category = self.calculate_nine_box_category()
        super().save(*args, **kwargs)

    def calculate_nine_box_category(self):
        p = self.performance_rating
        pot = self.potential_rating
        if p >= 4 and pot >= 4:
            return 'high_potential'
        elif p >= 4 and pot == 3:
            return 'key_talent'
        elif p >= 4 and pot <= 2:
            return 'solid_performer'
        elif p == 3 and pot >= 4:
            return 'emerging_talent'
        elif p == 3 and pot == 3:
            return 'solid_performer'
        elif p == 3 and pot <= 2:
            return 'risk_of_stagnation'
        elif p <= 2 and pot >= 4:
            return 'misplaced_talent'
        elif p <= 2 and pot == 3:
            return 'inconsistent_performer'
        else:
            return 'underperformer'

    @property
    def nine_box_position(self):
        return (self.potential_rating, self.performance_rating)


# ===========================================================================
# Succession Planning Models
# ===========================================================================

class CriticalPosition(TenantAwareModel, TimeStampedModel):
    CRITICALITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.CASCADE,
        related_name='critical_positions'
    )
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='critical_positions'
    )
    criticality = models.CharField(max_length=10, choices=CRITICALITY_CHOICES, default='medium')
    incumbent = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='critical_position_held'
    )
    reason = models.TextField(blank=True, help_text='Why this position is critical')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.designation} ({self.get_criticality_display()})"

    @property
    def successor_count(self):
        return self.successors.count()

    @property
    def has_ready_now_successor(self):
        return self.successors.filter(readiness='ready_now').exists()


class SuccessionCandidate(TenantAwareModel, TimeStampedModel):
    READINESS_CHOICES = [
        ('ready_now', 'Ready Now'),
        ('ready_1_2_years', 'Ready in 1-2 Years'),
        ('ready_3_5_years', 'Ready in 3-5 Years'),
    ]
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('in_development', 'In Development'),
        ('ready', 'Ready'),
        ('placed', 'Placed'),
        ('withdrawn', 'Withdrawn'),
    ]

    critical_position = models.ForeignKey(
        CriticalPosition, on_delete=models.CASCADE,
        related_name='successors'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='succession_candidacies'
    )
    readiness = models.CharField(max_length=20, choices=READINESS_CHOICES, default='ready_3_5_years')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')
    development_needs = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['readiness']
        unique_together = ['critical_position', 'employee']

    def __str__(self):
        return f"{self.employee} -> {self.critical_position.designation} ({self.get_readiness_display()})"


# ===========================================================================
# Career Pathing Models
# ===========================================================================

class CareerPath(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='career_paths'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def step_count(self):
        return self.steps.count()


class CareerPathStep(TenantAwareModel, TimeStampedModel):
    career_path = models.ForeignKey(
        CareerPath, on_delete=models.CASCADE,
        related_name='steps'
    )
    sequence = models.PositiveIntegerField(default=1)
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.CASCADE,
        related_name='career_path_steps'
    )
    required_experience_years = models.PositiveIntegerField(
        default=0, help_text='Minimum years of experience required'
    )
    required_skills = models.TextField(blank=True, help_text='Comma-separated skills required')
    required_competencies = models.TextField(blank=True, help_text='Competencies needed for this step')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['career_path', 'sequence']
        unique_together = ['career_path', 'sequence']

    def __str__(self):
        return f"{self.career_path.name} - Step {self.sequence}: {self.designation}"


class EmployeeCareerPlan(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='career_plans'
    )
    career_path = models.ForeignKey(
        CareerPath, on_delete=models.CASCADE,
        related_name='employee_plans'
    )
    current_step = models.ForeignKey(
        CareerPathStep, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='current_employees'
    )
    target_step = models.ForeignKey(
        CareerPathStep, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='target_employees'
    )
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.career_path.name}"


# ===========================================================================
# Internal Mobility Models
# ===========================================================================

class InternalJobPosting(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('on_hold', 'On Hold'),
    ]

    title = models.CharField(max_length=255)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='internal_postings'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='internal_postings'
    )
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    positions = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    posted_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='posted_internal_jobs'
    )
    closing_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def application_count(self):
        return self.transfer_applications.count()

    @property
    def is_open(self):
        return self.status == 'open'


class TransferApplication(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    posting = models.ForeignKey(
        InternalJobPosting, on_delete=models.CASCADE,
        related_name='transfer_applications'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='transfer_applications'
    )
    current_department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transfer_applications_from'
    )
    current_designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transfer_applications_from'
    )
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')
    reviewed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_transfers'
    )
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['posting', 'employee']

    def __str__(self):
        return f"{self.employee} -> {self.posting.title} ({self.get_status_display()})"


# ===========================================================================
# Talent Review Models
# ===========================================================================

class TalentReviewSession(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    session_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    facilitator = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='facilitated_talent_reviews'
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-session_date']

    def __str__(self):
        return self.name

    @property
    def participant_count(self):
        return self.participants.count()


class TalentReviewParticipant(TenantAwareModel, TimeStampedModel):
    session = models.ForeignKey(
        TalentReviewSession, on_delete=models.CASCADE,
        related_name='participants'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='talent_review_participations'
    )
    initial_performance_rating = models.IntegerField(null=True, blank=True)
    initial_potential_rating = models.IntegerField(null=True, blank=True)
    calibrated_performance_rating = models.IntegerField(null=True, blank=True)
    calibrated_potential_rating = models.IntegerField(null=True, blank=True)
    calibration_notes = models.TextField(blank=True)
    development_recommendations = models.TextField(blank=True)

    class Meta:
        ordering = ['employee__first_name']
        unique_together = ['session', 'employee']

    def __str__(self):
        return f"{self.employee} in {self.session.name}"


# ===========================================================================
# Retention Strategy Models
# ===========================================================================

class FlightRiskAssessment(TenantAwareModel, TimeStampedModel):
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='flight_risk_assessments'
    )
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='medium')
    risk_factors = models.TextField(blank=True, help_text='Factors contributing to flight risk')
    impact_if_lost = models.TextField(blank=True, help_text='Impact on the organization if the employee leaves')
    assessed_date = models.DateField()
    assessed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='flight_risk_assessments_given'
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assessed_date']

    def __str__(self):
        return f"{self.employee} - {self.get_risk_level_display()} Risk ({self.assessed_date})"


class RetentionPlan(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='retention_plans'
    )
    flight_risk = models.ForeignKey(
        FlightRiskAssessment, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='retention_plans'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    responsible_person = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='responsible_retention_plans'
    )
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planned')
    outcome_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.employee}"

    @property
    def action_count(self):
        return self.actions.count()

    @property
    def completed_action_count(self):
        return self.actions.filter(status='completed').count()


class RetentionAction(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    retention_plan = models.ForeignKey(
        RetentionPlan, on_delete=models.CASCADE,
        related_name='actions'
    )
    description = models.CharField(max_length=500)
    assigned_to = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_retention_actions'
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    completion_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return self.description[:50]
