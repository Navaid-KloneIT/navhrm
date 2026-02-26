from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


# ===========================================================================
# 7.1 Personal Information
# ===========================================================================

class FamilyMember(TenantAwareModel, TimeStampedModel):
    """Dependent / family member information for benefits."""
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('other', 'Other'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='family_members')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    occupation = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_dependent = models.BooleanField(default=False)
    is_nominee = models.BooleanField(default=False)
    nominee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Nomination percentage for PF/Gratuity')
    covered_under_insurance = models.BooleanField(default=False)
    insurance_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()}) - {self.employee}"


# ===========================================================================
# 7.2 Request Management
# ===========================================================================

class DocumentRequest(TenantAwareModel, TimeStampedModel):
    """Request for official documents (experience letter, salary certificate, etc.)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    DOCUMENT_TYPE_CHOICES = [
        ('experience_letter', 'Experience Letter'),
        ('salary_certificate', 'Salary Certificate'),
        ('employment_certificate', 'Employment Certificate'),
        ('relieving_letter', 'Relieving Letter'),
        ('bonafide_letter', 'Bonafide Letter'),
        ('address_proof_letter', 'Address Proof Letter'),
        ('custom', 'Custom Request'),
    ]
    DELIVERY_METHOD_CHOICES = [
        ('email', 'Email'),
        ('print', 'Print Copy'),
        ('both', 'Both'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='document_requests')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    purpose = models.TextField(help_text='Purpose for requesting this document')
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='processed_document_requests')
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    generated_file = models.FileField(upload_to='ess/document_requests/', blank=True)
    copies_needed = models.PositiveIntegerField(default=1)
    delivery_method = models.CharField(
        max_length=20, choices=DELIVERY_METHOD_CHOICES, default='email')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.get_document_type_display()} ({self.get_status_display()})"


class IDCardRequest(TenantAwareModel, TimeStampedModel):
    """Request for new or replacement ID card."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Collection'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    REQUEST_TYPE_CHOICES = [
        ('new', 'New ID Card'),
        ('replacement', 'Replacement (Lost/Damaged)'),
        ('renewal', 'Renewal (Expired)'),
        ('update', 'Update Details'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='idcard_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    photo = models.ImageField(upload_to='ess/idcard_photos/', blank=True, null=True)
    processed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='processed_idcard_requests')
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.get_request_type_display()} ({self.get_status_display()})"


class AssetRequest(TenantAwareModel, TimeStampedModel):
    """Request for equipment or assets."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('allocated', 'Allocated'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    ASSET_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('monitor', 'Monitor'),
        ('keyboard_mouse', 'Keyboard & Mouse'),
        ('headset', 'Headset'),
        ('mobile', 'Mobile Phone'),
        ('sim_card', 'SIM Card'),
        ('access_card', 'Access Card'),
        ('furniture', 'Furniture'),
        ('stationery', 'Stationery'),
        ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='asset_requests')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    asset_name = models.CharField(max_length=255,
        help_text='Specific asset description e.g. "MacBook Pro 16 inch"')
    quantity = models.PositiveIntegerField(default=1)
    reason = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_asset_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    expected_date = models.DateField(null=True, blank=True)
    allocated_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.asset_name} ({self.get_status_display()})"


# ===========================================================================
# 7.3 Communication Hub
# ===========================================================================

class Announcement(TenantAwareModel, TimeStampedModel):
    """Company-wide or department-specific announcements."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('policy', 'Policy Update'),
        ('event', 'Event'),
        ('holiday', 'Holiday'),
        ('achievement', 'Achievement'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    published_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='published_announcements')
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    target_departments = models.ManyToManyField(
        'organization.Department', blank=True,
        help_text='Leave blank for company-wide announcements')
    attachment = models.FileField(upload_to='ess/announcements/', blank=True)

    class Meta:
        ordering = ['-is_pinned', '-publish_date']

    def __str__(self):
        return self.title


class BirthdayWish(TenantAwareModel, TimeStampedModel):
    """Birthday or work anniversary wishes between employees."""
    OCCASION_CHOICES = [
        ('birthday', 'Birthday'),
        ('work_anniversary', 'Work Anniversary'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='received_wishes')
    wished_by = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='sent_wishes')
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES)
    message = models.TextField()
    occasion_date = models.DateField()

    class Meta:
        ordering = ['-created_at']
        unique_together = ['employee', 'wished_by', 'occasion', 'occasion_date', 'tenant']

    def __str__(self):
        return f"{self.wished_by} → {self.employee} ({self.get_occasion_display()})"


class Survey(TenantAwareModel, TimeStampedModel):
    """Employee engagement surveys."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_surveys')
    start_date = models.DateField()
    end_date = models.DateField()
    is_anonymous = models.BooleanField(default=True)
    target_departments = models.ManyToManyField(
        'organization.Department', blank=True,
        help_text='Leave blank for all departments')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def response_count(self):
        return self.responses.values('respondent').distinct().count()


class SurveyQuestion(TenantAwareModel, TimeStampedModel):
    """Individual questions within a survey."""
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text Answer'),
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating (1-5)'),
        ('yes_no', 'Yes/No'),
    ]

    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    choices = models.TextField(
        blank=True, help_text='Pipe-separated choices: Option1|Option2|Option3')
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"

    def get_choices_list(self):
        if self.choices:
            return [c.strip() for c in self.choices.split('|')]
        return []


class SurveyResponse(TenantAwareModel, TimeStampedModel):
    """Employee responses to survey questions."""
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(
        SurveyQuestion, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='survey_responses')
    answer_text = models.TextField(blank=True)
    answer_rating = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['question', 'respondent', 'tenant']

    def __str__(self):
        return f"{self.respondent} - {self.question}"


class Suggestion(TenantAwareModel, TimeStampedModel):
    """Employee suggestion / idea box."""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
    ]
    CATEGORY_CHOICES = [
        ('workplace', 'Workplace'),
        ('process', 'Process Improvement'),
        ('culture', 'Culture'),
        ('technology', 'Technology'),
        ('policy', 'Policy'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='suggestions')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    reviewed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_suggestions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_response = models.TextField(blank=True)
    upvotes = models.PositiveIntegerField(default=0)
    attachment = models.FileField(upload_to='ess/suggestions/', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class HelpDeskTicket(TenantAwareModel, TimeStampedModel):
    """HR help desk ticket system."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_on_employee', 'Waiting on Employee'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    CATEGORY_CHOICES = [
        ('payroll', 'Payroll & Salary'),
        ('leave', 'Leave & Attendance'),
        ('benefits', 'Benefits & Insurance'),
        ('policy', 'Policy Query'),
        ('it_support', 'IT Support'),
        ('facilities', 'Facilities'),
        ('documents', 'Documents & Letters'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='helpdesk_tickets')
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    subject = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tickets')
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='ess/tickets/', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import uuid
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class TicketComment(TenantAwareModel, TimeStampedModel):
    """Comments on help desk tickets."""
    ticket = models.ForeignKey(
        HelpDeskTicket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='ticket_comments')
    message = models.TextField()
    is_internal = models.BooleanField(
        default=False, help_text='Internal notes only visible to HR')
    attachment = models.FileField(upload_to='ess/ticket_comments/', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.author}"
