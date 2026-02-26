from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


# ===========================================================================
# Goal Setting Models
# ===========================================================================

class GoalPeriod(TenantAwareModel, TimeStampedModel):
    PERIOD_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('annual', 'Annual'),
        ('custom', 'Custom'),
    ]
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=255)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Goal(TenantAwareModel, TimeStampedModel):
    GOAL_TYPE_CHOICES = [
        ('okr', 'OKR (Objective & Key Result)'),
        ('kpi', 'KPI (Key Performance Indicator)'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('behind', 'Behind'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    VISIBILITY_CHOICES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
        ('department', 'Department'),
        ('organization', 'Organization'),
    ]

    period = models.ForeignKey(GoalPeriod, on_delete=models.CASCADE, related_name='goals')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='goals')
    parent_goal = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_goals')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=10, choices=GOAL_TYPE_CHOICES, default='kpi')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    target_value = models.CharField(max_length=255, blank=True)
    current_value = models.CharField(max_length=255, blank=True)
    progress = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='individual')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.employee}"


class GoalUpdate(TenantAwareModel, TimeStampedModel):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    progress = models.IntegerField(default=0)
    current_value = models.CharField(max_length=255, blank=True)
    note = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update on {self.goal.title}"


# ===========================================================================
# Performance Review Models
# ===========================================================================

class ReviewCycle(TenantAwareModel, TimeStampedModel):
    CYCLE_TYPE_CHOICES = [
        ('annual', 'Annual'),
        ('half_yearly', 'Half Yearly'),
        ('quarterly', 'Quarterly'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('self_assessment', 'Self Assessment Phase'),
        ('manager_review', 'Manager Review Phase'),
        ('peer_review', 'Peer Review Phase'),
        ('calibration', 'Calibration Phase'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    cycle_type = models.CharField(max_length=20, choices=CYCLE_TYPE_CHOICES)
    period = models.ForeignKey(GoalPeriod, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_cycles')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField()
    end_date = models.DateField()
    self_assessment_deadline = models.DateField(null=True, blank=True)
    manager_review_deadline = models.DateField(null=True, blank=True)
    peer_review_deadline = models.DateField(null=True, blank=True)
    calibration_deadline = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class PerformanceReview(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('self_assessment', 'Self Assessment'),
        ('manager_review', 'Manager Review'),
        ('peer_review', 'Peer Review'),
        ('calibration', 'Calibration'),
        ('completed', 'Completed'),
    ]

    cycle = models.ForeignKey(ReviewCycle, on_delete=models.CASCADE, related_name='reviews')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews_as_manager')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    self_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    self_comments = models.TextField(blank=True)
    manager_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    manager_comments = models.TextField(blank=True)
    final_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    final_comments = models.TextField(blank=True)
    calibrated_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='calibrated_reviews')
    calibrated_at = models.DateTimeField(null=True, blank=True)
    strengths = models.TextField(blank=True)
    areas_of_improvement = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['cycle', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.cycle}"


class ReviewGoalRating(TenantAwareModel, TimeStampedModel):
    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, related_name='goal_ratings')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='review_ratings')
    self_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    self_comments = models.TextField(blank=True)
    manager_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    manager_comments = models.TextField(blank=True)

    class Meta:
        ordering = ['goal__weight']
        unique_together = ['review', 'goal']

    def __str__(self):
        return f"Rating for {self.goal.title}"


class PeerReviewer(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    ]

    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, related_name='peer_reviewers')
    reviewer = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='peer_review_assignments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_peer_reviews')

    class Meta:
        ordering = ['-created_at']
        unique_together = ['review', 'reviewer']

    def __str__(self):
        return f"Peer: {self.reviewer} for {self.review.employee}"


class PeerFeedback(TenantAwareModel, TimeStampedModel):
    peer_reviewer = models.OneToOneField(PeerReviewer, on_delete=models.CASCADE, related_name='feedback')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    strengths = models.TextField(blank=True)
    areas_of_improvement = models.TextField(blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Peer Feedback by {self.peer_reviewer.reviewer}"


# ===========================================================================
# Continuous Feedback Models
# ===========================================================================

class Feedback(TenantAwareModel, TimeStampedModel):
    FEEDBACK_TYPE_CHOICES = [
        ('kudos', 'Kudos'),
        ('constructive', 'Constructive'),
        ('general', 'General'),
    ]
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('anonymous', 'Anonymous'),
    ]

    from_employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='feedback_given')
    to_employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='feedback_received')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, default='general')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_feedback_type_display()} to {self.to_employee}"


class OneOnOneMeeting(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    manager = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='one_on_one_as_manager')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='one_on_one_as_employee')
    title = models.CharField(max_length=255)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=30)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    manager_notes = models.TextField(blank=True)
    employee_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']

    def __str__(self):
        return f"1:1 {self.manager} & {self.employee} ({self.scheduled_date})"


class MeetingActionItem(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    meeting = models.ForeignKey(OneOnOneMeeting, on_delete=models.CASCADE, related_name='action_items')
    description = models.CharField(max_length=500)
    assigned_to = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='meeting_action_items')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return self.description[:50]


# ===========================================================================
# Performance Improvement Models
# ===========================================================================

class PIP(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('extended', 'Extended'),
        ('completed_success', 'Completed - Successful'),
        ('completed_failure', 'Completed - Unsuccessful'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='pips')
    initiated_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='initiated_pips')
    title = models.CharField(max_length=255)
    reason = models.TextField()
    goals = models.TextField()
    support_provided = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    outcome_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Performance Improvement Plan'
        verbose_name_plural = 'Performance Improvement Plans'

    def __str__(self):
        return f"PIP: {self.employee} - {self.title}"


class PIPCheckpoint(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('on_track', 'On Track'),
        ('needs_improvement', 'Needs Improvement'),
        ('met', 'Met'),
        ('not_met', 'Not Met'),
    ]

    pip = models.ForeignKey(PIP, on_delete=models.CASCADE, related_name='checkpoints')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    review_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    manager_notes = models.TextField(blank=True)
    employee_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.pip}"


class WarningLetter(TenantAwareModel, TimeStampedModel):
    WARNING_TYPE_CHOICES = [
        ('verbal', 'Verbal Warning'),
        ('written', 'Written Warning'),
        ('final', 'Final Warning'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('acknowledged', 'Acknowledged'),
        ('appealed', 'Appealed'),
        ('resolved', 'Resolved'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='warning_letters')
    issued_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_warnings')
    warning_type = models.CharField(max_length=20, choices=WARNING_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    issue_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    acknowledged_date = models.DateField(null=True, blank=True)
    employee_response = models.TextField(blank=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.get_warning_type_display()}: {self.employee} - {self.subject}"


class CoachingNote(TenantAwareModel, TimeStampedModel):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='coaching_notes')
    coach = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='coaching_given')
    session_date = models.DateField()
    topic = models.CharField(max_length=255)
    notes = models.TextField()
    action_items = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-session_date']

    def __str__(self):
        return f"Coaching: {self.employee} - {self.topic}"
