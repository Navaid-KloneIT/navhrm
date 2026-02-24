from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


# ==========================================================================
# SHIFT MANAGEMENT
# ==========================================================================

class Shift(TenantAwareModel, TimeStampedModel):
    """Defines work shifts (e.g., Day Shift 9am-6pm)."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_period_minutes = models.PositiveIntegerField(
        default=15, help_text='Grace period in minutes before marking late')
    half_day_threshold_hours = models.DecimalField(
        max_digits=4, decimal_places=2, default=4.0,
        help_text='Minimum hours to count as half day')
    full_day_threshold_hours = models.DecimalField(
        max_digits=4, decimal_places=2, default=8.0,
        help_text='Minimum hours to count as full day')
    is_night_shift = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')})"


class ShiftAssignment(TenantAwareModel, TimeStampedModel):
    """Assigns a shift to an employee for a date range."""
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='shift_assignments')
    shift = models.ForeignKey(
        Shift, on_delete=models.CASCADE, related_name='assignments')
    effective_from = models.DateField()
    effective_to = models.DateField(
        null=True, blank=True,
        help_text='Leave blank for indefinite assignment')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.employee} - {self.shift.name}"


# ==========================================================================
# ATTENDANCE MANAGEMENT
# ==========================================================================

class Attendance(TenantAwareModel, TimeStampedModel):
    """Daily attendance record for an employee."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('on_leave', 'On Leave'),
        ('holiday', 'Holiday'),
        ('weekend', 'Weekend'),
        ('not_marked', 'Not Marked'),
    ]
    SOURCE_CHOICES = [
        ('web', 'Web Punch'),
        ('manual', 'Manual Entry'),
        ('regularized', 'Regularized'),
        ('system', 'System Generated'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='attendances')
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    shift = models.ForeignKey(
        Shift, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='not_marked')
    total_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    is_late = models.BooleanField(default=False)
    late_minutes = models.PositiveIntegerField(default=0)
    is_early_departure = models.BooleanField(default=False)
    early_departure_minutes = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default='web')

    class Meta:
        ordering = ['-date']
        unique_together = ['employee', 'date', 'tenant']

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"

    def calculate_hours(self):
        """Calculate total working hours from check_in and check_out."""
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            return round(delta.total_seconds() / 3600, 2)
        return 0


class AttendanceRegularization(TenantAwareModel, TimeStampedModel):
    """Request to correct/regularize attendance."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    REASON_CHOICES = [
        ('forgot_punch', 'Forgot to Punch'),
        ('system_error', 'System Error'),
        ('on_duty', 'On Duty / Client Visit'),
        ('work_from_home', 'Work From Home'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='regularization_requests')
    attendance = models.ForeignKey(
        Attendance, on_delete=models.CASCADE,
        related_name='regularizations', null=True, blank=True)
    date = models.DateField()
    requested_check_in = models.DateTimeField(null=True, blank=True)
    requested_check_out = models.DateTimeField(null=True, blank=True)
    requested_status = models.CharField(
        max_length=20, choices=Attendance.STATUS_CHOICES, default='present')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_detail = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_regularizations')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comments = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"


# ==========================================================================
# LEAVE MANAGEMENT
# ==========================================================================

class LeaveType(TenantAwareModel, TimeStampedModel):
    """Defines types of leave (Sick, Casual, Earned, etc.)."""
    CATEGORY_CHOICES = [
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('earned', 'Earned/Privilege Leave'),
        ('unpaid', 'Unpaid/Loss of Pay'),
        ('comp_off', 'Compensatory Off'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('bereavement', 'Bereavement Leave'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_paid = models.BooleanField(default=True)
    max_days_per_year = models.DecimalField(
        max_digits=5, decimal_places=1, default=12)
    max_consecutive_days = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Maximum consecutive days allowed. Blank for no limit.')
    requires_approval = models.BooleanField(default=True)
    requires_document = models.BooleanField(
        default=False, help_text='Require supporting document')
    document_after_days = models.PositiveIntegerField(
        default=0, help_text='Require document if leave exceeds these days. 0 = always.')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    color_code = models.CharField(
        max_length=7, default='#3b82f6',
        help_text='Hex color for calendar display')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LeavePolicy(TenantAwareModel, TimeStampedModel):
    """Accrual, carry-forward, and encashment rules for a leave type."""
    ACCRUAL_FREQUENCY_CHOICES = [
        ('annual', 'Annual (Full at start)'),
        ('monthly', 'Monthly Accrual'),
        ('quarterly', 'Quarterly Accrual'),
        ('none', 'No Accrual (Manual)'),
    ]

    name = models.CharField(max_length=100)
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name='policies')
    accrual_frequency = models.CharField(
        max_length=20, choices=ACCRUAL_FREQUENCY_CHOICES, default='annual')
    accrual_amount = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.0,
        help_text='Days accrued per period')
    allow_carry_forward = models.BooleanField(default=False)
    max_carry_forward_days = models.DecimalField(
        max_digits=5, decimal_places=1, default=0)
    carry_forward_expiry_months = models.PositiveIntegerField(
        default=0, help_text='Months after which carried-forward days expire. 0 = never.')
    allow_encashment = models.BooleanField(default=False)
    max_encashment_days = models.DecimalField(
        max_digits=5, decimal_places=1, default=0)
    applicable_from_days = models.PositiveIntegerField(
        default=0, help_text='Eligible after these many days from joining. 0 = immediate.')
    applicable_employment_types = models.CharField(
        max_length=200, blank=True,
        help_text='Comma-separated: full_time,part_time,contract. Blank = all.')
    prorate_for_joining = models.BooleanField(
        default=True, help_text='Prorate leave for mid-year joiners')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.leave_type.name})"


class LeaveBalance(TenantAwareModel, TimeStampedModel):
    """Tracks leave balance per employee per leave type per year."""
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='leave_balances')
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name='balances')
    year = models.PositiveIntegerField()
    allocated = models.DecimalField(
        max_digits=5, decimal_places=1, default=0)
    used = models.DecimalField(
        max_digits=5, decimal_places=1, default=0)
    carried_forward = models.DecimalField(
        max_digits=5, decimal_places=1, default=0)
    adjustment = models.DecimalField(
        max_digits=5, decimal_places=1, default=0,
        help_text='Manual adjustment (+/-)')
    encashed = models.DecimalField(
        max_digits=5, decimal_places=1, default=0)

    class Meta:
        ordering = ['-year', 'leave_type__name']
        unique_together = ['employee', 'leave_type', 'year', 'tenant']

    def __str__(self):
        return f"{self.employee} - {self.leave_type.name} ({self.year})"

    @property
    def available(self):
        return (self.allocated + self.carried_forward
                + self.adjustment - self.used - self.encashed)


class LeaveApplication(TenantAwareModel, TimeStampedModel):
    """An employee's leave request."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    DAY_TYPE_CHOICES = [
        ('full_day', 'Full Day'),
        ('first_half', 'First Half'),
        ('second_half', 'Second Half'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='leave_applications')
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name='applications')
    from_date = models.DateField()
    to_date = models.DateField()
    from_day_type = models.CharField(
        max_length=15, choices=DAY_TYPE_CHOICES, default='full_day')
    to_day_type = models.CharField(
        max_length=15, choices=DAY_TYPE_CHOICES, default='full_day')
    total_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    document = models.FileField(
        upload_to='attendance/leave_documents/', blank=True)
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (f"{self.employee} - {self.leave_type.name} "
                f"({self.from_date} to {self.to_date})")

    def calculate_total_days(self):
        """Calculate total leave days considering half-day options."""
        if self.from_date == self.to_date:
            if self.from_day_type != 'full_day':
                return 0.5
            return 1.0
        delta = (self.to_date - self.from_date).days + 1
        total = float(delta)
        if self.from_day_type != 'full_day':
            total -= 0.5
        if self.to_day_type != 'full_day':
            total -= 0.5
        return total


# ==========================================================================
# TIME TRACKING
# ==========================================================================

class Project(TenantAwareModel, TimeStampedModel):
    """Project for time tracking."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=255, blank=True)
    manager = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_projects')
    members = models.ManyToManyField(
        'employees.Employee', related_name='projects', blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget_hours = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Billing rate per hour')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active')
    is_billable = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_logged_hours(self):
        return self.time_entries.aggregate(
            total=models.Sum('hours'))['total'] or 0

    @property
    def billable_amount(self):
        billable_hours = self.time_entries.filter(
            is_billable=True).aggregate(
            total=models.Sum('hours'))['total'] or 0
        return billable_hours * self.hourly_rate


class Task(TenantAwareModel, TimeStampedModel):
    """Task within a project for granular time tracking."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tasks')
    estimated_hours = models.DecimalField(
        max_digits=7, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='open')
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['project', 'name']

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Timesheet(TenantAwareModel, TimeStampedModel):
    """Weekly timesheet for approval workflow."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='timesheets')
    week_start_date = models.DateField(
        help_text='Monday of the timesheet week')
    week_end_date = models.DateField(
        help_text='Sunday of the timesheet week')
    total_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    billable_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_timesheets')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-week_start_date']
        unique_together = ['employee', 'week_start_date', 'tenant']

    def __str__(self):
        return f"{self.employee} - Week of {self.week_start_date}"

    def compute_totals(self):
        entries = self.entries.all()
        self.total_hours = sum(e.hours for e in entries)
        self.billable_hours = sum(e.hours for e in entries if e.is_billable)


class TimeEntry(TenantAwareModel, TimeStampedModel):
    """Individual time entry against a project/task."""
    timesheet = models.ForeignKey(
        Timesheet, on_delete=models.CASCADE,
        related_name='entries', null=True, blank=True)
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='time_entries')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='time_entries')
    task = models.ForeignKey(
        Task, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='time_entries')
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    is_billable = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.project.name} ({self.date}: {self.hours}h)"


class OvertimeRequest(TenantAwareModel, TimeStampedModel):
    """Overtime tracking and approval."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    OT_TYPE_CHOICES = [
        ('weekday', 'Weekday Overtime'),
        ('weekend', 'Weekend Overtime'),
        ('holiday', 'Holiday Overtime'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='overtime_requests')
    date = models.DateField()
    ot_type = models.CharField(
        max_length=20, choices=OT_TYPE_CHOICES, default='weekday')
    planned_hours = models.DecimalField(max_digits=5, decimal_places=2)
    actual_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    reason = models.TextField()
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='overtime_entries')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_overtimes')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    generate_comp_off = models.BooleanField(
        default=False, help_text='Generate comp-off leave for this overtime')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - OT {self.date} ({self.planned_hours}h)"


# ==========================================================================
# HOLIDAY MANAGEMENT
# ==========================================================================

class Holiday(TenantAwareModel, TimeStampedModel):
    """Company/national/regional holidays."""
    HOLIDAY_TYPE_CHOICES = [
        ('national', 'National Holiday'),
        ('regional', 'Regional Holiday'),
        ('company', 'Company Holiday'),
        ('restricted', 'Restricted/Optional Holiday'),
    ]

    name = models.CharField(max_length=255)
    date = models.DateField()
    holiday_type = models.CharField(
        max_length=20, choices=HOLIDAY_TYPE_CHOICES, default='company')
    description = models.TextField(blank=True)
    location = models.ForeignKey(
        'organization.Location', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='holidays',
        help_text='Applicable location. Blank = all locations.')
    year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']
        unique_together = ['name', 'date', 'tenant']

    def __str__(self):
        return f"{self.name} ({self.date})"

    def save(self, *args, **kwargs):
        if not self.year:
            self.year = self.date.year
        super().save(*args, **kwargs)


class FloatingHoliday(TenantAwareModel, TimeStampedModel):
    """Optional/floating holidays employees can pick from a list."""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('selected', 'Selected'),
        ('availed', 'Availed'),
        ('expired', 'Expired'),
    ]

    holiday = models.ForeignKey(
        Holiday, on_delete=models.CASCADE, related_name='floating_selections')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='floating_holidays')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='selected')
    selected_date = models.DateField(
        null=True, blank=True,
        help_text='Date employee chooses to take this holiday')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['holiday', 'employee', 'tenant']

    def __str__(self):
        return f"{self.employee} - {self.holiday.name}"


class HolidayPolicy(TenantAwareModel, TimeStampedModel):
    """Rules for holiday assignment based on location/department."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.ForeignKey(
        'organization.Location', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='holiday_policies')
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='holiday_policies')
    applicable_employment_types = models.CharField(
        max_length=200, blank=True,
        help_text='Comma-separated: full_time,part_time,contract. Blank = all.')
    max_floating_holidays = models.PositiveIntegerField(
        default=2, help_text='Number of floating holidays per year')
    year = models.PositiveIntegerField()
    holidays = models.ManyToManyField(
        Holiday, related_name='policies', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-year', 'name']
        verbose_name_plural = 'Holiday Policies'

    def __str__(self):
        return f"{self.name} ({self.year})"
