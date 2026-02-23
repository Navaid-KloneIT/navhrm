from django.db import models
from django.utils import timezone
from apps.core.models import TenantAwareModel, TimeStampedModel


# ---------------------------------------------------------------------------
# Job Requisition Sub-Module
# ---------------------------------------------------------------------------

class JobTemplate(TenantAwareModel, TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class JobRequisition(TenantAwareModel, TimeStampedModel):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('freelance', 'Freelance'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('on_hold', 'On Hold'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='job_requisitions'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='job_requisitions'
    )
    location = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    experience_min = models.PositiveIntegerField(default=0)
    experience_max = models.PositiveIntegerField(null=True, blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    positions = models.PositiveIntegerField(default=1)
    filled_positions = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    requested_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='requested_requisitions'
    )
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_requisitions'
    )
    publish_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        return self.status in ('approved', 'published') and self.filled_positions < self.positions

    @property
    def application_count(self):
        return self.applications.count()

    @property
    def days_open(self):
        if self.publish_date:
            return (timezone.now().date() - self.publish_date).days
        return 0


class RequisitionApproval(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    requisition = models.ForeignKey(
        JobRequisition, on_delete=models.CASCADE, related_name='approvals'
    )
    approver = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='requisition_approvals'
    )
    level = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True)
    acted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return f"{self.requisition.title} - Level {self.level} ({self.get_status_display()})"


# ---------------------------------------------------------------------------
# Candidate Management Sub-Module
# ---------------------------------------------------------------------------

SOURCE_CHOICES = [
    ('career_page', 'Career Page'),
    ('referral', 'Referral'),
    ('job_portal', 'Job Portal'),
    ('social_media', 'Social Media'),
    ('recruitment_agency', 'Recruitment Agency'),
    ('direct', 'Direct'),
    ('other', 'Other'),
]


class Candidate(TenantAwareModel, TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    resume = models.FileField(upload_to='recruitment/resumes/', blank=True)
    photo = models.ImageField(upload_to='recruitment/photos/', blank=True, null=True)
    current_company = models.CharField(max_length=255, blank=True)
    current_designation = models.CharField(max_length=255, blank=True)
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    current_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    skills = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper() if self.first_name and self.last_name else "?"


class JobApplication(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    job = models.ForeignKey(
        JobRequisition, on_delete=models.CASCADE, related_name='applications'
    )
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name='applications'
    )
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='recruitment/applications/', blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')
    applied_date = models.DateField(auto_now_add=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct')
    notes = models.TextField(blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_date']
        unique_together = ['job', 'candidate', 'tenant']

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job.title}"


# ---------------------------------------------------------------------------
# Interview Process Sub-Module
# ---------------------------------------------------------------------------

class InterviewRound(TenantAwareModel, TimeStampedModel):
    requisition = models.ForeignKey(
        JobRequisition, on_delete=models.CASCADE, related_name='interview_rounds'
    )
    name = models.CharField(max_length=100)
    round_number = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['round_number']

    def __str__(self):
        return f"{self.requisition.title} - {self.name}"


class Interview(TenantAwareModel, TimeStampedModel):
    MODE_CHOICES = [
        ('in_person', 'In Person'),
        ('phone', 'Phone'),
        ('video', 'Video Call'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('on_hold', 'On Hold'),
    ]

    application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name='interviews'
    )
    round = models.ForeignKey(
        InterviewRound, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='interviews'
    )
    round_name = models.CharField(max_length=100)
    interviewers = models.ManyToManyField(
        'employees.Employee', related_name='conducted_interviews', blank=True
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=255, blank=True)
    mode = models.CharField(max_length=15, choices=MODE_CHOICES, default='in_person')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    overall_rating = models.PositiveIntegerField(null=True, blank=True)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending')

    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']

    def __str__(self):
        return f"{self.application.candidate.full_name} - {self.round_name}"


class InterviewFeedback(TenantAwareModel, TimeStampedModel):
    RECOMMENDATION_CHOICES = [
        ('strong_hire', 'Strong Hire'),
        ('hire', 'Hire'),
        ('no_hire', 'No Hire'),
        ('strong_no_hire', 'Strong No Hire'),
    ]

    interview = models.ForeignKey(
        Interview, on_delete=models.CASCADE, related_name='feedbacks'
    )
    interviewer = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='interview_feedbacks'
    )
    technical_rating = models.PositiveIntegerField(null=True, blank=True)
    communication_rating = models.PositiveIntegerField(null=True, blank=True)
    cultural_fit_rating = models.PositiveIntegerField(null=True, blank=True)
    overall_rating = models.PositiveIntegerField(null=True, blank=True)
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    recommendation = models.CharField(max_length=15, choices=RECOMMENDATION_CHOICES, default='hire')

    class Meta:
        ordering = ['-created_at']
        unique_together = ['interview', 'interviewer', 'tenant']

    def __str__(self):
        return f"Feedback by {self.interviewer} for {self.interview}"


# ---------------------------------------------------------------------------
# Offer Management Sub-Module
# ---------------------------------------------------------------------------

class OfferLetter(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('expired', 'Expired'),
    ]

    application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name='offers'
    )
    offered_designation = models.CharField(max_length=255)
    offered_department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='offer_letters'
    )
    offered_salary = models.DecimalField(max_digits=12, decimal_places=2)
    salary_currency = models.CharField(max_length=10, default='INR')
    joining_date = models.DateField()
    offer_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    probation_months = models.PositiveIntegerField(default=6)
    benefits = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_offers'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    candidate_response_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-offer_date']

    def __str__(self):
        return f"Offer - {self.application.candidate.full_name} ({self.get_status_display()})"
