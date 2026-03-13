from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TenantAwareModel, TimeStampedModel


# =============================================================================
# SUB-MODULE 1: ENGAGEMENT SURVEYS
# =============================================================================

class EngagementSurvey(TenantAwareModel, TimeStampedModel):
    SURVEY_TYPE_CHOICES = [
        ('pulse', 'Pulse Survey'),
        ('enps', 'eNPS Survey'),
        ('engagement', 'Engagement Survey'),
        ('custom', 'Custom Survey'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]
    TARGET_AUDIENCE_CHOICES = [
        ('all', 'All Employees'),
        ('department', 'By Department'),
        ('designation', 'By Designation'),
        ('custom', 'Custom Selection'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    survey_type = models.CharField(max_length=20, choices=SURVEY_TYPE_CHOICES, default='pulse')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField()
    end_date = models.DateField()
    is_anonymous = models.BooleanField(default=False)
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE_CHOICES, default='all')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def response_count(self):
        return self.responses.filter(is_complete=True).count()

    @property
    def question_count(self):
        return self.questions.count()


class EngagementSurveyQuestion(TenantAwareModel, TimeStampedModel):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating (1-5)'),
        ('yes_no', 'Yes/No'),
        ('scale', 'Scale (1-10)'),
    ]

    survey = models.ForeignKey(EngagementSurvey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='text')
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.survey.title} - Q{self.order}: {self.question_text[:50]}"


class EngagementSurveyQuestionOption(TenantAwareModel, TimeStampedModel):
    question = models.ForeignKey(EngagementSurveyQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.option_text


class EngagementSurveyResponse(TenantAwareModel, TimeStampedModel):
    survey = models.ForeignKey(EngagementSurvey, on_delete=models.CASCADE, related_name='responses')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='engagement_survey_responses'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        emp = self.employee or 'Anonymous'
        return f"{self.survey.title} - {emp}"


class EngagementSurveyAnswer(TenantAwareModel, TimeStampedModel):
    response = models.ForeignKey(EngagementSurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(EngagementSurveyQuestion, on_delete=models.CASCADE, related_name='answers')
    text_answer = models.TextField(blank=True)
    selected_option = models.ForeignKey(
        EngagementSurveyQuestionOption, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='answers'
    )
    rating_value = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['question__order']

    def __str__(self):
        return f"Answer to: {self.question.question_text[:50]}"


class EngagementActionPlan(TenantAwareModel, TimeStampedModel):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    survey = models.ForeignKey(EngagementSurvey, on_delete=models.CASCADE, related_name='action_plans')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='engagement_action_plans'
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# =============================================================================
# SUB-MODULE 2: WELLBEING PROGRAMS
# =============================================================================

class WellbeingProgram(TenantAwareModel, TimeStampedModel):
    CATEGORY_CHOICES = [
        ('mental_health', 'Mental Health'),
        ('physical_health', 'Physical Health'),
        ('nutrition', 'Nutrition'),
        ('financial', 'Financial Wellness'),
        ('social', 'Social Wellbeing'),
        ('mindfulness', 'Mindfulness'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField()
    end_date = models.DateField()
    max_participants = models.PositiveIntegerField(default=0, help_text='0 = unlimited')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class WellbeingResource(TenantAwareModel, TimeStampedModel):
    RESOURCE_TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('podcast', 'Podcast'),
        ('webinar', 'Webinar'),
        ('tool', 'Tool'),
        ('guide', 'Guide'),
    ]
    CATEGORY_CHOICES = WellbeingProgram.CATEGORY_CHOICES

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class WellnessChallenge(TenantAwareModel, TimeStampedModel):
    CHALLENGE_TYPE_CHOICES = [
        ('steps', 'Steps Challenge'),
        ('meditation', 'Meditation'),
        ('hydration', 'Hydration'),
        ('exercise', 'Exercise'),
        ('sleep', 'Sleep'),
        ('custom', 'Custom'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    goal_target = models.DecimalField(max_digits=10, decimal_places=2)
    goal_unit = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def participant_count(self):
        return self.participants.count()


class ChallengeParticipant(TenantAwareModel, TimeStampedModel):
    challenge = models.ForeignKey(WellnessChallenge, on_delete=models.CASCADE, related_name='participants')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='challenge_participations'
    )
    progress = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-joined_at']
        unique_together = ['challenge', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.challenge.title}"

    @property
    def progress_percentage(self):
        if self.challenge.goal_target:
            return min(round((self.progress / self.challenge.goal_target) * 100, 1), 100)
        return 0


# =============================================================================
# SUB-MODULE 3: WORK-LIFE BALANCE
# =============================================================================

class FlexibleWorkArrangement(TenantAwareModel, TimeStampedModel):
    ARRANGEMENT_TYPE_CHOICES = [
        ('remote', 'Remote Work'),
        ('hybrid', 'Hybrid'),
        ('flexible_hours', 'Flexible Hours'),
        ('compressed_week', 'Compressed Work Week'),
        ('job_sharing', 'Job Sharing'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='work_arrangements'
    )
    arrangement_type = models.CharField(max_length=20, choices=ARRANGEMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    days_per_week = models.PositiveIntegerField(default=5)
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_arrangements'
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.get_arrangement_type_display()}"


class RemoteWorkPolicy(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    eligibility_criteria = models.TextField(blank=True)
    equipment_provided = models.TextField(blank=True)
    communication_expectations = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Remote work policies'

    def __str__(self):
        return self.name


class WorkLifeBalanceAssessment(TenantAwareModel, TimeStampedModel):
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='wlb_assessments'
    )
    assessment_date = models.DateField()
    work_satisfaction = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    life_satisfaction = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    stress_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    overall_score = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assessment_date']

    def __str__(self):
        return f"{self.employee} - {self.assessment_date}"

    def save(self, *args, **kwargs):
        self.overall_score = round(
            (self.work_satisfaction + self.life_satisfaction + (6 - self.stress_level)) / 3, 1
        )
        super().save(*args, **kwargs)


# =============================================================================
# SUB-MODULE 4: EMPLOYEE ASSISTANCE
# =============================================================================

class EAPProgram(TenantAwareModel, TimeStampedModel):
    SERVICE_TYPE_CHOICES = [
        ('counseling', 'Counseling'),
        ('legal', 'Legal Assistance'),
        ('financial', 'Financial Advice'),
        ('career', 'Career Guidance'),
        ('family', 'Family Support'),
        ('substance_abuse', 'Substance Abuse'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    provider = models.CharField(max_length=255, blank=True)
    contact_info = models.TextField(blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'EAP Program'
        verbose_name_plural = 'EAP Programs'

    def __str__(self):
        return self.name


class CounselingSession(TenantAwareModel, TimeStampedModel):
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('family', 'Family'),
        ('crisis', 'Crisis'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='counseling_sessions'
    )
    program = models.ForeignKey(EAPProgram, on_delete=models.CASCADE, related_name='sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='individual')
    session_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    counselor_name = models.CharField(max_length=255, blank=True)
    is_confidential = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.employee} - {self.session_date.strftime('%Y-%m-%d')}"


class EAPUtilization(TenantAwareModel, TimeStampedModel):
    program = models.ForeignKey(EAPProgram, on_delete=models.CASCADE, related_name='utilizations')
    period_start = models.DateField()
    period_end = models.DateField()
    total_sessions = models.PositiveIntegerField(default=0)
    total_participants = models.PositiveIntegerField(default=0)
    satisfaction_score = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )

    class Meta:
        ordering = ['-period_start']
        verbose_name = 'EAP Utilization'

    def __str__(self):
        return f"{self.program.name} - {self.period_start} to {self.period_end}"


# =============================================================================
# SUB-MODULE 5: CULTURE & VALUES
# =============================================================================

class CompanyValue(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Remix icon class e.g. ri-heart-line')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def nomination_count(self):
        return self.nominations.filter(status='approved').count()


class CultureAssessment(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assessment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_culture_assessments'
    )

    class Meta:
        ordering = ['-assessment_date']

    def __str__(self):
        return self.title

    @property
    def response_count(self):
        return self.responses.count()

    @property
    def avg_alignment_score(self):
        avg = self.responses.aggregate(models.Avg('alignment_score'))['alignment_score__avg']
        return round(avg, 1) if avg else None


class CultureAssessmentResponse(TenantAwareModel, TimeStampedModel):
    assessment = models.ForeignKey(CultureAssessment, on_delete=models.CASCADE, related_name='responses')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='culture_responses'
    )
    alignment_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['assessment', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.assessment.title}"


class ValueNomination(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    value = models.ForeignKey(CompanyValue, on_delete=models.CASCADE, related_name='nominations')
    nominee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='value_nominations_received'
    )
    nominated_by = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='value_nominations_given'
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nominee} nominated for {self.value.name}"


# =============================================================================
# SUB-MODULE 6: SOCIAL CONNECT
# =============================================================================

class TeamEvent(TenantAwareModel, TimeStampedModel):
    EVENT_TYPE_CHOICES = [
        ('team_building', 'Team Building'),
        ('celebration', 'Celebration'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('learning', 'Learning'),
        ('social', 'Social'),
    ]
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    organizer = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='organized_events'
    )
    max_participants = models.PositiveIntegerField(default=0, help_text='0 = unlimited')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    @property
    def participant_count(self):
        return self.participants.filter(rsvp_status='attending').count()


class EventParticipant(TenantAwareModel, TimeStampedModel):
    RSVP_CHOICES = [
        ('attending', 'Attending'),
        ('maybe', 'Maybe'),
        ('not_attending', 'Not Attending'),
    ]

    event = models.ForeignKey(TeamEvent, on_delete=models.CASCADE, related_name='participants')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='event_participations'
    )
    rsvp_status = models.CharField(max_length=20, choices=RSVP_CHOICES, default='attending')
    attended = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['event', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.event.title}"


class InterestGroup(TenantAwareModel, TimeStampedModel):
    CATEGORY_CHOICES = [
        ('sports', 'Sports'),
        ('arts', 'Arts'),
        ('technology', 'Technology'),
        ('reading', 'Reading'),
        ('music', 'Music'),
        ('gaming', 'Gaming'),
        ('outdoor', 'Outdoor'),
        ('cooking', 'Cooking'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_interest_groups'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class InterestGroupMember(TenantAwareModel, TimeStampedModel):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
    ]

    group = models.ForeignKey(InterestGroup, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='interest_group_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_at']
        unique_together = ['group', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.group.name}"


class VolunteerActivity(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    activity_date = models.DateField()
    location = models.CharField(max_length=255, blank=True)
    hours_required = models.DecimalField(max_digits=5, decimal_places=1)
    max_volunteers = models.PositiveIntegerField(default=0, help_text='0 = unlimited')
    organizer = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='organized_volunteer_activities'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-activity_date']
        verbose_name_plural = 'Volunteer activities'

    def __str__(self):
        return self.title

    @property
    def volunteer_count(self):
        return self.participants.count()


class VolunteerParticipant(TenantAwareModel, TimeStampedModel):
    activity = models.ForeignKey(VolunteerActivity, on_delete=models.CASCADE, related_name='participants')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='volunteer_participations'
    )
    hours_contributed = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['activity', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.activity.title}"
