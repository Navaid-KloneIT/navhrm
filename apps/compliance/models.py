from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


# ===========================================================================
# Labor Law Compliance Models
# ===========================================================================

class LaborLaw(TenantAwareModel, TimeStampedModel):
    CATEGORY_CHOICES = [
        ('wages', 'Wages & Compensation'),
        ('working_hours', 'Working Hours & Overtime'),
        ('leave', 'Leave & Holidays'),
        ('safety', 'Occupational Safety & Health'),
        ('discrimination', 'Anti-Discrimination'),
        ('termination', 'Termination & Severance'),
        ('child_labor', 'Child Labor'),
        ('social_security', 'Social Security'),
        ('industrial_relations', 'Industrial Relations'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('amended', 'Amended'),
        ('repealed', 'Repealed'),
        ('draft', 'Draft'),
    ]

    name = models.CharField(max_length=255)
    jurisdiction = models.CharField(max_length=255, help_text='Country/state/region')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    compliance_requirements = models.TextField(blank=True, help_text='Key compliance requirements')
    penalties = models.TextField(blank=True, help_text='Penalties for non-compliance')
    reference_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.name} ({self.jurisdiction})"

    @property
    def is_active(self):
        return self.status == 'active'


class LaborLawCompliance(TenantAwareModel, TimeStampedModel):
    COMPLIANCE_STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partial', 'Partially Compliant'),
        ('under_review', 'Under Review'),
    ]

    labor_law = models.ForeignKey(
        LaborLaw, on_delete=models.CASCADE,
        related_name='compliance_records'
    )
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='labor_law_compliance'
    )
    compliance_status = models.CharField(
        max_length=15, choices=COMPLIANCE_STATUS_CHOICES, default='under_review'
    )
    review_date = models.DateField()
    next_review_date = models.DateField(null=True, blank=True)
    responsible_person = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='law_compliance_responsibilities'
    )
    compliance_notes = models.TextField(blank=True)
    action_required = models.TextField(blank=True)

    class Meta:
        ordering = ['-review_date']
        verbose_name_plural = 'Labor law compliance records'

    def __str__(self):
        return f"{self.labor_law.name} - {self.get_compliance_status_display()}"


# ===========================================================================
# Contract Management Models
# ===========================================================================

class EmploymentContract(TenantAwareModel, TimeStampedModel):
    CONTRACT_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('fixed_term', 'Fixed Term'),
        ('probation', 'Probation'),
        ('internship', 'Internship'),
        ('consultant', 'Consultant'),
        ('part_time', 'Part Time'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('renewed', 'Renewed'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='employment_contracts'
    )
    contract_type = models.CharField(max_length=15, choices=CONTRACT_TYPE_CHOICES, default='permanent')
    contract_number = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    terms = models.TextField(blank=True, help_text='Contract terms and conditions')
    salary_details = models.TextField(blank=True)
    probation_period_months = models.PositiveIntegerField(default=0)
    notice_period_days = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    signed_date = models.DateField(null=True, blank=True)
    signed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='signed_contracts'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee} - {self.get_contract_type_display()} ({self.get_status_display()})"

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def amendment_count(self):
        return self.amendments.count()


class ContractAmendment(TenantAwareModel, TimeStampedModel):
    AMENDMENT_TYPE_CHOICES = [
        ('salary_revision', 'Salary Revision'),
        ('designation_change', 'Designation Change'),
        ('department_transfer', 'Department Transfer'),
        ('terms_update', 'Terms Update'),
        ('extension', 'Contract Extension'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    contract = models.ForeignKey(
        EmploymentContract, on_delete=models.CASCADE,
        related_name='amendments'
    )
    amendment_type = models.CharField(max_length=20, choices=AMENDMENT_TYPE_CHOICES)
    amendment_date = models.DateField()
    description = models.TextField()
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    effective_date = models.DateField()
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_amendments'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-amendment_date']

    def __str__(self):
        return f"{self.contract.employee} - {self.get_amendment_type_display()} ({self.amendment_date})"


# ===========================================================================
# Policy Management Models
# ===========================================================================

class CompliancePolicy(TenantAwareModel, TimeStampedModel):
    CATEGORY_CHOICES = [
        ('hr', 'Human Resources'),
        ('safety', 'Health & Safety'),
        ('conduct', 'Code of Conduct'),
        ('leave', 'Leave Policy'),
        ('travel', 'Travel Policy'),
        ('expense', 'Expense Policy'),
        ('data_privacy', 'Data Privacy'),
        ('anti_harassment', 'Anti-Harassment'),
        ('it_security', 'IT Security'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('under_review', 'Under Review'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='hr')
    description = models.TextField(blank=True)
    content = models.TextField(help_text='Full policy content')
    version = models.CharField(max_length=20, default='1.0')
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_policies'
    )
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='compliance_policies',
        help_text='Leave blank for organization-wide policies'
    )

    class Meta:
        ordering = ['-effective_date']
        verbose_name_plural = 'Compliance policies'

    def __str__(self):
        return f"{self.title} (v{self.version})"

    @property
    def acknowledgment_count(self):
        return self.acknowledgments.filter(is_acknowledged=True).count()

    @property
    def version_count(self):
        return self.versions.count()


class PolicyVersion(TenantAwareModel, TimeStampedModel):
    policy = models.ForeignKey(
        CompliancePolicy, on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.CharField(max_length=20)
    changes_summary = models.TextField()
    content = models.TextField()
    created_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='policy_versions_created'
    )
    effective_date = models.DateField()

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.policy.title} - v{self.version_number}"


class PolicyAcknowledgment(TenantAwareModel, TimeStampedModel):
    policy = models.ForeignKey(
        CompliancePolicy, on_delete=models.CASCADE,
        related_name='acknowledgments'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='policy_acknowledgments'
    )
    acknowledged_date = models.DateTimeField(null=True, blank=True)
    is_acknowledged = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-acknowledged_date']
        unique_together = ['policy', 'employee']

    def __str__(self):
        status = 'Acknowledged' if self.is_acknowledged else 'Pending'
        return f"{self.employee} - {self.policy.title} ({status})"


# ===========================================================================
# Disciplinary Actions Models
# ===========================================================================

class DisciplinaryIncident(TenantAwareModel, TimeStampedModel):
    INCIDENT_TYPE_CHOICES = [
        ('misconduct', 'Misconduct'),
        ('absenteeism', 'Absenteeism'),
        ('insubordination', 'Insubordination'),
        ('harassment', 'Harassment'),
        ('policy_violation', 'Policy Violation'),
        ('performance', 'Poor Performance'),
        ('theft', 'Theft'),
        ('fraud', 'Fraud'),
        ('safety_violation', 'Safety Violation'),
        ('other', 'Other'),
    ]
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('under_investigation', 'Under Investigation'),
        ('action_taken', 'Action Taken'),
        ('closed', 'Closed'),
        ('dismissed', 'Dismissed'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='disciplinary_incidents'
    )
    incident_date = models.DateField()
    reported_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reported_incidents'
    )
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='minor')
    description = models.TextField()
    witness = models.TextField(blank=True, help_text='Names of witnesses')
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-incident_date']

    def __str__(self):
        return f"{self.employee} - {self.get_incident_type_display()} ({self.incident_date})"

    @property
    def warning_count(self):
        return self.warnings.count()


class WarningRecord(TenantAwareModel, TimeStampedModel):
    WARNING_TYPE_CHOICES = [
        ('verbal', 'Verbal Warning'),
        ('written', 'Written Warning'),
        ('final', 'Final Warning'),
        ('suspension', 'Suspension'),
        ('termination', 'Termination'),
    ]
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('acknowledged', 'Acknowledged'),
        ('appealed', 'Appealed'),
        ('resolved', 'Resolved'),
        ('expired', 'Expired'),
    ]

    incident = models.ForeignKey(
        DisciplinaryIncident, on_delete=models.CASCADE,
        related_name='warnings'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='warning_records'
    )
    warning_type = models.CharField(max_length=15, choices=WARNING_TYPE_CHOICES)
    issued_date = models.DateField()
    issued_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='warnings_issued'
    )
    reason = models.TextField()
    action_required = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='issued')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issued_date']

    def __str__(self):
        return f"{self.employee} - {self.get_warning_type_display()} ({self.issued_date})"


class DisciplinaryAppeal(TenantAwareModel, TimeStampedModel):
    DECISION_CHOICES = [
        ('pending', 'Pending'),
        ('upheld', 'Upheld'),
        ('modified', 'Modified'),
        ('overturned', 'Overturned'),
    ]

    warning = models.ForeignKey(
        WarningRecord, on_delete=models.CASCADE,
        related_name='appeals'
    )
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='disciplinary_appeals'
    )
    appeal_date = models.DateField()
    grounds = models.TextField(help_text='Grounds for appeal')
    supporting_documents = models.TextField(blank=True, help_text='Description of supporting documents')
    reviewed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_appeals'
    )
    review_date = models.DateField(null=True, blank=True)
    decision = models.CharField(max_length=12, choices=DECISION_CHOICES, default='pending')
    decision_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-appeal_date']

    def __str__(self):
        return f"{self.employee} - Appeal ({self.get_decision_display()})"


# ===========================================================================
# Grievance Handling Models
# ===========================================================================

class Grievance(TenantAwareModel, TimeStampedModel):
    CATEGORY_CHOICES = [
        ('workplace', 'Workplace Conditions'),
        ('compensation', 'Compensation & Benefits'),
        ('discrimination', 'Discrimination'),
        ('harassment', 'Harassment'),
        ('safety', 'Health & Safety'),
        ('management', 'Management Issues'),
        ('policy', 'Policy Related'),
        ('workload', 'Workload'),
        ('other', 'Other'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('under_investigation', 'Under Investigation'),
        ('hearing', 'Hearing Scheduled'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('withdrawn', 'Withdrawn'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE,
        related_name='grievances'
    )
    grievance_date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    assigned_to = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_grievances'
    )
    resolution_date = models.DateField(null=True, blank=True)
    resolution_summary = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        ordering = ['-grievance_date']

    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"

    @property
    def investigation_count(self):
        return self.investigations.count()


class GrievanceInvestigation(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    grievance = models.ForeignKey(
        Grievance, on_delete=models.CASCADE,
        related_name='investigations'
    )
    investigator = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='grievance_investigations'
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    findings = models.TextField(blank=True)
    evidence = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"Investigation for {self.grievance.subject} ({self.get_status_display()})"


# ===========================================================================
# Statutory Registers Models
# ===========================================================================

class MusterRoll(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('final', 'Final'),
    ]

    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='muster_rolls'
    )
    generated_date = models.DateField()
    generated_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='muster_rolls_generated'
    )
    total_employees = models.PositiveIntegerField(default=0)
    total_working_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    class Meta:
        ordering = ['-year', '-month']

    def __str__(self):
        return f"Muster Roll - {self.get_month_display()}/{self.year}"

    def get_month_display(self):
        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December',
        }
        return months.get(self.month, '')

    @property
    def period_display(self):
        return f"{self.get_month_display()} {self.year}"


class WageRegister(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('final', 'Final'),
    ]

    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='wage_registers'
    )
    generated_date = models.DateField()
    generated_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='wage_registers_generated'
    )
    total_gross = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    class Meta:
        ordering = ['-year', '-month']

    def __str__(self):
        return f"Wage Register - {self.get_month_display()}/{self.year}"

    def get_month_display(self):
        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December',
        }
        return months.get(self.month, '')

    @property
    def period_display(self):
        return f"{self.get_month_display()} {self.year}"


class InspectionReport(TenantAwareModel, TimeStampedModel):
    INSPECTION_TYPE_CHOICES = [
        ('routine', 'Routine'),
        ('surprise', 'Surprise'),
        ('complaint_based', 'Complaint Based'),
        ('follow_up', 'Follow-Up'),
    ]
    COMPLIANCE_STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partial', 'Partially Compliant'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('follow_up_required', 'Follow-Up Required'),
        ('closed', 'Closed'),
    ]

    inspection_date = models.DateField()
    inspector_name = models.CharField(max_length=255)
    inspector_designation = models.CharField(max_length=255, blank=True)
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPE_CHOICES, default='routine')
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='inspection_reports'
    )
    areas_inspected = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    compliance_status = models.CharField(
        max_length=15, choices=COMPLIANCE_STATUS_CHOICES, default='compliant'
    )
    recommendations = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-inspection_date']

    def __str__(self):
        return f"Inspection - {self.inspection_date} ({self.get_inspection_type_display()})"
