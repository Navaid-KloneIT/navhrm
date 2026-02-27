import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import TenantAwareModel, TimeStampedModel, get_current_tenant


# ===========================================================================
# Asset Management Models
# ===========================================================================

class AssetCategory(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.name


class Asset(TenantAwareModel, TimeStampedModel):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('allocated', 'Allocated'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('disposed', 'Disposed'),
    ]

    asset_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        AssetCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assets'
    )
    serial_number = models.CharField(max_length=255, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.asset_id})"

    @property
    def is_under_warranty(self):
        if self.warranty_expiry:
            return self.warranty_expiry >= timezone.now().date()
        return False

    @property
    def current_allocation(self):
        return self.allocations.filter(status='active').first()


class AssetAllocation(TenantAwareModel, TimeStampedModel):
    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE,
        related_name='additional_assetallocation_set'
    )

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name='allocations'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='asset_allocations'
    )
    allocated_date = models.DateField()
    allocated_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='asset_allocations_made'
    )
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    condition_at_allocation = models.CharField(
        max_length=20, choices=Asset.CONDITION_CHOICES, blank=True
    )
    condition_at_return = models.CharField(
        max_length=20, choices=Asset.CONDITION_CHOICES, blank=True
    )
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['-allocated_date']

    def __str__(self):
        return f"{self.asset.name} -> {self.employee}"


class AssetMaintenance(TenantAwareModel, TimeStampedModel):
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('amc', 'AMC'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name='maintenance_records'
    )
    maintenance_type = models.CharField(
        max_length=20, choices=MAINTENANCE_TYPE_CHOICES, default='preventive'
    )
    description = models.TextField(blank=True)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    vendor = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name_plural = 'Asset Maintenance'

    def __str__(self):
        return f"{self.asset.name} - {self.get_maintenance_type_display()} ({self.scheduled_date})"


# ===========================================================================
# Expense Management Models
# ===========================================================================

class ExpenseCategory(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Expense Categories'

    def __str__(self):
        return self.name


class ExpensePolicy(TenantAwareModel, TimeStampedModel):
    APPLIES_TO_CHOICES = [
        ('all', 'All Employees'),
        ('department', 'Department'),
        ('designation', 'Designation'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO_CHOICES, default='all')
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='expense_policies'
    )
    designation = models.ForeignKey(
        'organization.Designation', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='expense_policies'
    )
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    requires_receipt_above = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Expense Policies'

    def __str__(self):
        return self.name


class ExpenseClaim(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('reimbursed', 'Reimbursed'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='expense_claims'
    )
    claim_number = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='claims'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    receipt = models.FileField(upload_to='additional/expense_receipts/', blank=True, null=True)
    expense_date = models.DateField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='expense_approvals'
    )
    approved_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    reimbursement_date = models.DateField(null=True, blank=True)
    reimbursement_reference = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.claim_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.claim_number:
            self.claim_number = f"EXP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


# ===========================================================================
# Travel Management Models
# ===========================================================================

class TravelPolicy(TenantAwareModel, TimeStampedModel):
    TRAVEL_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    travel_class = models.CharField(max_length=20, choices=TRAVEL_CLASS_CHOICES, default='economy')
    daily_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hotel_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Travel Policies'

    def __str__(self):
        return self.name


class TravelRequest(TenantAwareModel, TimeStampedModel):
    TRAVEL_TYPE_CHOICES = [
        ('domestic', 'Domestic'),
        ('international', 'International'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='travel_requests'
    )
    request_number = models.CharField(max_length=50, unique=True, editable=False)
    purpose = models.TextField()
    travel_type = models.CharField(max_length=20, choices=TRAVEL_TYPE_CHOICES, default='domestic')
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    departure_date = models.DateField()
    return_date = models.DateField()
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_required = models.BooleanField(default=False)
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='travel_approvals'
    )
    approved_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_number} - {self.employee}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = f"TRV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_expenses(self):
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or 0


class TravelExpense(TenantAwareModel, TimeStampedModel):
    EXPENSE_TYPE_CHOICES = [
        ('flight', 'Flight'),
        ('hotel', 'Hotel'),
        ('cab', 'Cab/Transport'),
        ('food', 'Food'),
        ('other', 'Other'),
    ]

    travel_request = models.ForeignKey(
        TravelRequest, on_delete=models.CASCADE, related_name='expenses'
    )
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPE_CHOICES, default='other')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    receipt = models.FileField(upload_to='additional/travel_receipts/', blank=True, null=True)
    description = models.TextField(blank=True)
    date = models.DateField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.amount}"


class TravelSettlement(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('settled', 'Settled'),
    ]

    travel_request = models.OneToOneField(
        TravelRequest, on_delete=models.CASCADE, related_name='settlement'
    )
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_given = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    settlement_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    settled_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Settlement - {self.travel_request.request_number}"


# ===========================================================================
# Helpdesk Models
# ===========================================================================

class TicketCategory(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='ticket_categories'
    )
    default_assignee = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='default_ticket_categories'
    )
    sla_response_hours = models.IntegerField(default=24)
    sla_resolution_hours = models.IntegerField(default=72)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Ticket Categories'

    def __str__(self):
        return self.name


class Ticket(TenantAwareModel, TimeStampedModel):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]

    ticket_number = models.CharField(max_length=50, unique=True, editable=False)
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='tickets'
    )
    category = models.ForeignKey(
        TicketCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tickets'
    )
    subject = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tickets'
    )
    resolution = models.TextField(blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    satisfaction_rating = models.IntegerField(null=True, blank=True)
    satisfaction_feedback = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class TicketComment(TenantAwareModel, TimeStampedModel):
    tenant = models.ForeignKey(
        'core.Tenant', on_delete=models.CASCADE,
        related_name='additional_ticketcomment_set'
    )

    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='comments'
    )
    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='ticket_comments'
    )
    comment = models.TextField()
    is_internal = models.BooleanField(default=False)
    attachment = models.FileField(
        upload_to='additional/ticket_attachments/', blank=True, null=True
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.user}"


class KnowledgeBase(TenantAwareModel, TimeStampedModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        TicketCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='knowledge_articles'
    )
    content = models.TextField()
    author = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='knowledge_articles'
    )
    is_published = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Knowledge Base Articles'

    def __str__(self):
        return self.title
