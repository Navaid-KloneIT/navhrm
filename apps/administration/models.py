from django.db import models
from django.conf import settings
from apps.core.models import TenantAwareModel, TimeStampedModel


# =============================================================================
# 9.1 User Management Models
# =============================================================================

class Role(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        unique_together = ['code', 'tenant']

    def __str__(self):
        return self.name


class Permission(TenantAwareModel, TimeStampedModel):
    MODULE_CHOICES = [
        ('employees', 'Employees'),
        ('organization', 'Organization'),
        ('attendance', 'Attendance & Leave'),
        ('payroll', 'Payroll'),
        ('performance', 'Performance'),
        ('training', 'Training'),
        ('ess', 'Employee Self-Service'),
        ('recruitment', 'Recruitment'),
        ('reports', 'Reports'),
        ('administration', 'Administration'),
    ]
    ACTION_CHOICES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('export', 'Export'),
    ]

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    is_granted = models.BooleanField(default=False)

    class Meta:
        ordering = ['module', 'action']
        unique_together = ['role', 'module', 'action', 'tenant']

    def __str__(self):
        status = 'Granted' if self.is_granted else 'Denied'
        return f"{self.role.name} - {self.get_module_display()} - {self.get_action_display()} ({status})"


class LoginHistory(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('locked', 'Locked'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    failure_reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-login_at']
        verbose_name_plural = 'Login histories'

    def __str__(self):
        return f"{self.user} - {self.get_status_display()} - {self.login_at}"


# =============================================================================
# 9.2 Workflow Configuration Models
# =============================================================================

class ApprovalWorkflow(TenantAwareModel, TimeStampedModel):
    MODULE_CHOICES = [
        ('leave', 'Leave'),
        ('attendance_regularization', 'Attendance Regularization'),
        ('expense', 'Expense'),
        ('timesheet', 'Timesheet'),
        ('loan', 'Loan'),
        ('resignation', 'Resignation'),
        ('recruitment', 'Recruitment'),
        ('training_nomination', 'Training Nomination'),
    ]

    name = models.CharField(max_length=200)
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_module_display()})"


class ApprovalStep(TenantAwareModel, TimeStampedModel):
    APPROVER_TYPE_CHOICES = [
        ('reporting_manager', 'Reporting Manager'),
        ('department_head', 'Department Head'),
        ('hr_manager', 'HR Manager'),
        ('specific_user', 'Specific User'),
        ('role_based', 'Role Based'),
    ]

    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.CASCADE, related_name='steps')
    step_order = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    approver_type = models.CharField(max_length=30, choices=APPROVER_TYPE_CHOICES)
    specific_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_steps'
    )
    specific_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_steps'
    )
    can_skip = models.BooleanField(default=False)
    auto_approve_days = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['step_order']
        unique_together = ['workflow', 'step_order', 'tenant']

    def __str__(self):
        return f"Step {self.step_order}: {self.name}"


class EmailTemplate(TenantAwareModel, TimeStampedModel):
    EVENT_CHOICES = [
        ('leave_applied', 'Leave Applied'),
        ('leave_approved', 'Leave Approved'),
        ('leave_rejected', 'Leave Rejected'),
        ('attendance_regularization', 'Attendance Regularization'),
        ('expense_submitted', 'Expense Submitted'),
        ('expense_approved', 'Expense Approved'),
        ('new_employee', 'New Employee'),
        ('employee_birthday', 'Employee Birthday'),
        ('salary_processed', 'Salary Processed'),
        ('password_reset', 'Password Reset'),
        ('welcome_email', 'Welcome Email'),
        ('exit_initiated', 'Exit Initiated'),
        ('custom', 'Custom'),
    ]

    name = models.CharField(max_length=200)
    event = models.CharField(max_length=50, choices=EVENT_CHOICES)
    subject = models.CharField(max_length=500)
    body = models.TextField(help_text='HTML content with {{variable}} placeholders')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class NotificationSetting(TenantAwareModel, TimeStampedModel):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('in_app', 'In-App'),
        ('both', 'Both'),
        ('none', 'None'),
    ]
    RECIPIENT_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('hr', 'HR'),
        ('admin', 'Admin'),
        ('custom', 'Custom'),
    ]

    event = models.CharField(max_length=50, choices=EmailTemplate.EVENT_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='email')
    recipients = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='employee')
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['event']
        unique_together = ['event', 'tenant']

    def __str__(self):
        return f"{self.get_event_display()} - {self.get_channel_display()}"


class EscalationRule(TenantAwareModel, TimeStampedModel):
    ACTION_CHOICES = [
        ('remind', 'Send Reminder'),
        ('escalate_next', 'Escalate to Next Level'),
        ('auto_approve', 'Auto Approve'),
        ('notify_admin', 'Notify Admin'),
    ]

    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.CASCADE, related_name='escalation_rules')
    trigger_after_days = models.PositiveIntegerField(default=3)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    notify_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='escalation_notifications'
    )
    max_reminders = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['workflow', 'trigger_after_days']

    def __str__(self):
        return f"{self.workflow.name} - {self.get_action_display()} after {self.trigger_after_days} days"


# =============================================================================
# 9.3 System Configuration Models
# =============================================================================

class SystemSetting(TenantAwareModel, TimeStampedModel):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('display', 'Display'),
        ('email', 'Email'),
        ('security', 'Security'),
        ('notifications', 'Notifications'),
    ]
    VALUE_TYPE_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]

    key = models.CharField(max_length=100)
    value = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    value_type = models.CharField(max_length=10, choices=VALUE_TYPE_CHOICES, default='string')
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['category', 'key']
        unique_together = ['key', 'tenant']

    def __str__(self):
        return f"{self.key} = {self.value}"


class FinancialYear(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class FinancialPeriod(TenantAwareModel, TimeStampedModel):
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=100)
    period_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['period_number']
        unique_together = ['financial_year', 'period_number', 'tenant']

    def __str__(self):
        return f"{self.name} ({self.financial_year.name})"


class WorkingHoursPolicy(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=200)
    work_start_time = models.TimeField()
    work_end_time = models.TimeField()
    break_duration = models.PositiveIntegerField(default=60, help_text='Break duration in minutes')
    total_hours = models.DecimalField(max_digits=4, decimal_places=2)
    grace_late_minutes = models.PositiveIntegerField(default=15)
    grace_early_minutes = models.PositiveIntegerField(default=15)
    overtime_threshold = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    working_days = models.JSONField(default=list, help_text='List of working day numbers (0=Mon, 6=Sun)')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Working hours policies'

    def __str__(self):
        return self.name

    def get_working_days_display(self):
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return ', '.join(day_names[d] for d in self.working_days if d < 7)


class IntegrationSetting(TenantAwareModel, TimeStampedModel):
    PROVIDER_CHOICES = [
        ('smtp', 'SMTP Email'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('whatsapp', 'WhatsApp'),
        ('sms_gateway', 'SMS Gateway'),
        ('biometric', 'Biometric Device'),
        ('google_workspace', 'Google Workspace'),
        ('microsoft_365', 'Microsoft 365'),
        ('custom_api', 'Custom API'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]

    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    base_url = models.URLField(blank=True)
    config_json = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_tested_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"


# =============================================================================
# 9.4 Audit & Compliance Models
# =============================================================================

class AuditTrail(TenantAwareModel):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_trails'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.model_name} - {self.timestamp}"


class DataRetentionPolicy(TenantAwareModel, TimeStampedModel):
    DATA_TYPE_CHOICES = [
        ('employee_records', 'Employee Records'),
        ('payroll_data', 'Payroll Data'),
        ('attendance_data', 'Attendance Data'),
        ('audit_logs', 'Audit Logs'),
        ('login_history', 'Login History'),
        ('documents', 'Documents'),
        ('applicant_data', 'Applicant Data'),
    ]
    ACTION_CHOICES = [
        ('archive', 'Archive'),
        ('anonymize', 'Anonymize'),
        ('delete', 'Delete'),
    ]

    data_type = models.CharField(max_length=30, choices=DATA_TYPE_CHOICES)
    retention_days = models.PositiveIntegerField(default=365)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='archive')
    is_active = models.BooleanField(default=True)
    last_executed = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['data_type']
        verbose_name_plural = 'Data retention policies'

    def __str__(self):
        return f"{self.get_data_type_display()} - {self.retention_days} days"


class BackupConfiguration(TenantAwareModel, TimeStampedModel):
    BACKUP_TYPE_CHOICES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup'),
    ]
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('manual', 'Manual'),
    ]

    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES, default='full')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='manual')
    retention_count = models.PositiveIntegerField(default=5, help_text='Number of backups to retain')
    include_media = models.BooleanField(default=True)
    last_backup_at = models.DateTimeField(null=True, blank=True)
    last_backup_size = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_backup_type_display()} - {self.get_frequency_display()}"


class BackupLog(TenantAwareModel):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    backup_config = models.ForeignKey(
        BackupConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backup_logs'
    )

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Backup {self.get_status_display()} - {self.started_at}"
