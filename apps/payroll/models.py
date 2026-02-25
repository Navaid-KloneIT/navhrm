from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TenantAwareModel, TimeStampedModel


# ==========================================================================
# SECTION 1: SALARY STRUCTURE
# ==========================================================================

class PayComponent(TenantAwareModel, TimeStampedModel):
    """Defines individual pay components: Basic, HRA, DA, PF, etc."""
    COMPONENT_TYPE_CHOICES = [
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    ]
    CALCULATION_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percent_of_basic', 'Percentage of Basic'),
        ('percent_of_ctc', 'Percentage of CTC'),
        ('percent_of_gross', 'Percentage of Gross'),
    ]
    CATEGORY_CHOICES = [
        ('basic', 'Basic Pay'),
        ('hra', 'House Rent Allowance'),
        ('da', 'Dearness Allowance'),
        ('special', 'Special Allowance'),
        ('conveyance', 'Conveyance Allowance'),
        ('medical', 'Medical Allowance'),
        ('lta', 'Leave Travel Allowance'),
        ('bonus', 'Bonus'),
        ('incentive', 'Incentive'),
        ('commission', 'Commission'),
        ('pf_employee', 'PF (Employee)'),
        ('pf_employer', 'PF (Employer)'),
        ('esi_employee', 'ESI (Employee)'),
        ('esi_employer', 'ESI (Employer)'),
        ('professional_tax', 'Professional Tax'),
        ('tds', 'TDS / Income Tax'),
        ('lwf_employee', 'LWF (Employee)'),
        ('lwf_employer', 'LWF (Employer)'),
        ('other_earning', 'Other Earning'),
        ('other_deduction', 'Other Deduction'),
    ]

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    component_type = models.CharField(max_length=15, choices=COMPONENT_TYPE_CHOICES)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES, default='other_earning')
    calculation_type = models.CharField(
        max_length=20, choices=CALCULATION_TYPE_CHOICES, default='fixed')
    default_value = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Fixed amount or percentage value')
    is_taxable = models.BooleanField(default=True)
    is_statutory = models.BooleanField(default=False, help_text='PF, ESI, PT, TDS, LWF')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['component_type', 'display_order', 'name']
        unique_together = ['code', 'tenant']

    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"


class SalaryStructure(TenantAwareModel, TimeStampedModel):
    """Grade-wise salary structure template."""
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, blank=True)
    job_grade = models.ForeignKey(
        'organization.JobGrade', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_structures')
    base_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Reference CTC for this structure')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SalaryStructureComponent(TenantAwareModel, TimeStampedModel):
    """Maps a pay component to a salary structure with its value."""
    salary_structure = models.ForeignKey(
        SalaryStructure, on_delete=models.CASCADE, related_name='components')
    pay_component = models.ForeignKey(
        PayComponent, on_delete=models.CASCADE, related_name='structure_components')
    calculation_type = models.CharField(
        max_length=20, choices=PayComponent.CALCULATION_TYPE_CHOICES, default='fixed',
        help_text='Override component default calculation type')
    value = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Fixed amount or percentage')

    class Meta:
        ordering = ['pay_component__display_order']
        unique_together = ['salary_structure', 'pay_component', 'tenant']

    def __str__(self):
        return f"{self.salary_structure.name} - {self.pay_component.name}"


class EmployeeSalaryStructure(TenantAwareModel, TimeStampedModel):
    """Assigns a salary structure to an employee with their specific CTC."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('revised', 'Revised'),
        ('inactive', 'Inactive'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='salary_structures')
    salary_structure = models.ForeignKey(
        SalaryStructure, on_delete=models.CASCADE, related_name='employee_assignments')
    ctc = models.DecimalField(
        max_digits=12, decimal_places=2, help_text='Cost to Company (annual)')
    gross_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Monthly gross (auto-calculated)')
    net_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Monthly net (auto-calculated)')
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.employee} - {self.salary_structure.name} ({self.effective_from})"


class EmployeeSalaryComponent(TenantAwareModel, TimeStampedModel):
    """Individual component breakdown for an employee's salary."""
    employee_salary = models.ForeignKey(
        EmployeeSalaryStructure, on_delete=models.CASCADE, related_name='components')
    pay_component = models.ForeignKey(
        PayComponent, on_delete=models.CASCADE, related_name='employee_components')
    monthly_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_overridden = models.BooleanField(
        default=False, help_text='True if manually adjusted from structure default')

    class Meta:
        ordering = ['pay_component__display_order']
        unique_together = ['employee_salary', 'pay_component', 'tenant']

    def __str__(self):
        return f"{self.employee_salary.employee} - {self.pay_component.name}: {self.monthly_amount}"


# ==========================================================================
# SECTION 2: PAYROLL PROCESSING
# ==========================================================================

class PayrollPeriod(TenantAwareModel, TimeStampedModel):
    """Defines a payroll period (typically monthly)."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True, help_text='Salary credit date')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    total_gross = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    employee_count = models.PositiveIntegerField(default=0)
    processed_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='processed_payrolls')
    processed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_payrolls')
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year', 'tenant']

    def __str__(self):
        return f"{self.name} ({self.month}/{self.year})"


class PayrollEntry(TenantAwareModel, TimeStampedModel):
    """One employee's payroll record for a given period."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('held', 'Salary Held'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    payroll_period = models.ForeignKey(
        PayrollPeriod, on_delete=models.CASCADE, related_name='entries')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='payroll_entries')
    employee_salary = models.ForeignKey(
        EmployeeSalaryStructure, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='payroll_entries')
    gross_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    days_payable = models.PositiveIntegerField(default=0)
    days_present = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)
    lop_days = models.DecimalField(
        max_digits=5, decimal_places=1, default=0, help_text='Loss of Pay days')
    lop_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    arrears_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reimbursement_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    hold_reason = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-payroll_period__year', '-payroll_period__month']
        unique_together = ['payroll_period', 'employee', 'tenant']

    def __str__(self):
        return f"{self.employee} - {self.payroll_period}"


class PayrollEntryComponent(TenantAwareModel, TimeStampedModel):
    """Line-item component detail for each payroll entry."""
    payroll_entry = models.ForeignKey(
        PayrollEntry, on_delete=models.CASCADE, related_name='components')
    pay_component = models.ForeignKey(
        PayComponent, on_delete=models.CASCADE, related_name='payroll_entry_components')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_arrear = models.BooleanField(default=False)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['pay_component__display_order']

    def __str__(self):
        return f"{self.payroll_entry} - {self.pay_component.name}: {self.amount}"


class SalaryHold(TenantAwareModel, TimeStampedModel):
    """Hold salary disbursement for specific employees."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('released', 'Released'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='salary_holds')
    payroll_period = models.ForeignKey(
        PayrollPeriod, on_delete=models.CASCADE,
        related_name='salary_holds', null=True, blank=True,
        help_text='Blank = hold for all future periods')
    reason = models.TextField()
    held_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_holds_created')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    released_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_holds_released')
    released_at = models.DateTimeField(null=True, blank=True)
    release_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - Hold ({self.get_status_display()})"


class SalaryRevision(TenantAwareModel, TimeStampedModel):
    """Track salary revisions for arrears calculation."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('applied', 'Applied'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='salary_revisions')
    old_salary_structure = models.ForeignKey(
        EmployeeSalaryStructure, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='revisions_from')
    new_salary_structure = models.ForeignKey(
        EmployeeSalaryStructure, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='revisions_to')
    old_ctc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_ctc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_from = models.DateField()
    revision_date = models.DateField(help_text='Date revision was processed')
    arrears_from = models.DateField(
        null=True, blank=True, help_text='Calculate arrears from this date')
    arrears_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_revisions')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-revision_date']

    def __str__(self):
        return f"{self.employee} - Revision ({self.effective_from})"


# ==========================================================================
# SECTION 3: STATUTORY COMPLIANCE
# ==========================================================================

class PFConfiguration(TenantAwareModel, TimeStampedModel):
    """Provident Fund configuration for the organization."""
    pf_number = models.CharField(max_length=50, blank=True, help_text='PF establishment number')
    employee_contribution_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=12.00,
        help_text='Employee PF contribution %')
    employer_contribution_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=12.00,
        help_text='Employer PF contribution %')
    eps_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=8.33,
        help_text='Employer EPS contribution % (part of employer share)')
    admin_charge_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.50,
        help_text='Admin charges %')
    edli_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.50,
        help_text='EDLI contribution %')
    pf_ceiling = models.DecimalField(
        max_digits=12, decimal_places=2, default=15000,
        help_text='PF applicable on basic up to this amount')
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"PF Config (from {self.effective_from})"


class ESIConfiguration(TenantAwareModel, TimeStampedModel):
    """ESI configuration for the organization."""
    esi_number = models.CharField(max_length=50, blank=True)
    employee_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.75)
    employer_rate = models.DecimalField(max_digits=5, decimal_places=2, default=3.25)
    wage_ceiling = models.DecimalField(
        max_digits=12, decimal_places=2, default=21000,
        help_text='ESI applicable if gross <= this amount')
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"ESI Config (from {self.effective_from})"


class ProfessionalTaxSlab(TenantAwareModel, TimeStampedModel):
    """State-wise professional tax slabs."""
    state = models.CharField(max_length=100)
    salary_from = models.DecimalField(max_digits=12, decimal_places=2)
    salary_to = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()

    class Meta:
        ordering = ['state', 'salary_from']

    def __str__(self):
        return f"PT {self.state}: {self.salary_from}-{self.salary_to} = {self.tax_amount}"


class LWFConfiguration(TenantAwareModel, TimeStampedModel):
    """Labour Welfare Fund configuration (state-wise)."""
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('half_yearly', 'Half Yearly'),
        ('annual', 'Annual'),
    ]

    state = models.CharField(max_length=100)
    employee_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    employer_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='half_yearly')
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()

    class Meta:
        ordering = ['state']

    def __str__(self):
        return f"LWF {self.state}: Emp={self.employee_contribution}, Empr={self.employer_contribution}"


class StatutoryContribution(TenantAwareModel, TimeStampedModel):
    """Records actual statutory contribution per employee per payroll period."""
    CONTRIBUTION_TYPE_CHOICES = [
        ('pf_employee', 'PF Employee'),
        ('pf_employer', 'PF Employer'),
        ('eps', 'EPS (Employer)'),
        ('esi_employee', 'ESI Employee'),
        ('esi_employer', 'ESI Employer'),
        ('pt', 'Professional Tax'),
        ('lwf_employee', 'LWF Employee'),
        ('lwf_employer', 'LWF Employer'),
    ]

    payroll_entry = models.ForeignKey(
        PayrollEntry, on_delete=models.CASCADE, related_name='statutory_contributions')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='statutory_contributions')
    payroll_period = models.ForeignKey(
        PayrollPeriod, on_delete=models.CASCADE, related_name='statutory_contributions')
    contribution_type = models.CharField(max_length=20, choices=CONTRIBUTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    base_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Base salary used for calculation')

    class Meta:
        ordering = ['-payroll_period__year', '-payroll_period__month']

    def __str__(self):
        return f"{self.employee} - {self.get_contribution_type_display()}: {self.amount}"


# ==========================================================================
# SECTION 4: TAX & INVESTMENT
# ==========================================================================

class TaxRegimeChoice(TenantAwareModel, TimeStampedModel):
    """Employee's tax regime selection for a financial year."""
    REGIME_CHOICES = [
        ('old', 'Old Regime'),
        ('new', 'New Regime'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='tax_regime_choices')
    financial_year = models.CharField(max_length=10, help_text='e.g. 2025-26')
    regime = models.CharField(max_length=5, choices=REGIME_CHOICES, default='new')
    locked = models.BooleanField(default=False, help_text='Locked after payroll run')

    class Meta:
        ordering = ['-financial_year']
        unique_together = ['employee', 'financial_year', 'tenant']

    def __str__(self):
        return f"{self.employee} - {self.financial_year} ({self.get_regime_display()})"


class InvestmentDeclaration(TenantAwareModel, TimeStampedModel):
    """Employee's investment declaration for tax computation."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    SECTION_CHOICES = [
        ('80c', 'Section 80C'),
        ('80ccc', 'Section 80CCC'),
        ('80ccd1', 'Section 80CCD(1)'),
        ('80ccd1b', 'Section 80CCD(1B) - NPS'),
        ('80ccd2', 'Section 80CCD(2) - Employer NPS'),
        ('80d', 'Section 80D - Health Insurance'),
        ('80dd', 'Section 80DD - Disabled Dependent'),
        ('80ddb', 'Section 80DDB - Medical Treatment'),
        ('80e', 'Section 80E - Education Loan'),
        ('80ee', 'Section 80EE - Home Loan Interest'),
        ('80eea', 'Section 80EEA - Affordable Housing'),
        ('80g', 'Section 80G - Donations'),
        ('80tta', 'Section 80TTA - Savings Interest'),
        ('24b', 'Section 24(b) - Home Loan Interest'),
        ('hra', 'HRA Exemption'),
        ('lta', 'LTA Exemption'),
        ('other', 'Other Exemption'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='investment_declarations')
    financial_year = models.CharField(max_length=10)
    section = models.CharField(max_length=15, choices=SECTION_CHOICES)
    description = models.CharField(max_length=255)
    declared_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    verified_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    verified_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_declarations')
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-financial_year', 'section']

    def __str__(self):
        return f"{self.employee} - {self.get_section_display()} ({self.financial_year})"


class InvestmentProof(TenantAwareModel, TimeStampedModel):
    """Document proof uploaded for an investment declaration."""
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    declaration = models.ForeignKey(
        InvestmentDeclaration, on_delete=models.CASCADE, related_name='proofs')
    document_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='payroll/investment_proofs/')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_proofs')
    verified_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.declaration.employee} - {self.document_name}"


class TaxComputation(TenantAwareModel, TimeStampedModel):
    """Annual tax computation summary for an employee."""
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='tax_computations')
    financial_year = models.CharField(max_length=10)
    regime = models.CharField(
        max_length=5, choices=TaxRegimeChoice.REGIME_CHOICES, default='new')
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_exemptions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions_80c = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions_other = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_on_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    education_cess = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax_liability = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tds_deducted_ytd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_tds = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Projected monthly TDS to be deducted')

    class Meta:
        ordering = ['-financial_year']
        unique_together = ['employee', 'financial_year', 'tenant']

    def __str__(self):
        return f"{self.employee} - Tax ({self.financial_year})"


# ==========================================================================
# SECTION 5: PAYOUT & REPORTS
# ==========================================================================

class BankFile(TenantAwareModel, TimeStampedModel):
    """Generated bank transfer file for salary disbursement."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent to Bank'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    BANK_FORMAT_CHOICES = [
        ('hdfc', 'HDFC Bank'),
        ('icici', 'ICICI Bank'),
        ('sbi', 'SBI'),
        ('axis', 'Axis Bank'),
        ('neft', 'Generic NEFT'),
        ('csv', 'CSV Export'),
    ]

    payroll_period = models.ForeignKey(
        PayrollPeriod, on_delete=models.CASCADE, related_name='bank_files')
    file_name = models.CharField(max_length=255)
    bank_format = models.CharField(max_length=20, choices=BANK_FORMAT_CHOICES, default='neft')
    file = models.FileField(upload_to='payroll/bank_files/', blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    employee_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    generated_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='generated_bank_files')
    generated_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} ({self.get_status_display()})"


class Payslip(TenantAwareModel, TimeStampedModel):
    """Generated payslip for an employee for a payroll period."""
    payroll_entry = models.OneToOneField(
        PayrollEntry, on_delete=models.CASCADE, related_name='payslip')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='payslips')
    payroll_period = models.ForeignKey(
        PayrollPeriod, on_delete=models.CASCADE, related_name='payslips')
    file = models.FileField(upload_to='payroll/payslips/', blank=True)
    is_emailed = models.BooleanField(default=False)
    emailed_at = models.DateTimeField(null=True, blank=True)
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-payroll_period__year', '-payroll_period__month']
        unique_together = ['employee', 'payroll_period', 'tenant']

    def __str__(self):
        return f"Payslip - {self.employee} ({self.payroll_period})"


class PaymentRegister(TenantAwareModel, TimeStampedModel):
    """Payment register entry tracking actual disbursement."""
    PAYMENT_MODE_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('demand_draft', 'Demand Draft'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('reconciled', 'Reconciled'),
    ]

    payroll_period = models.ForeignKey(
        PayrollPeriod, on_delete=models.CASCADE, related_name='payment_register')
    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='payment_register_entries')
    payroll_entry = models.ForeignKey(
        PayrollEntry, on_delete=models.CASCADE, related_name='payment_register')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_mode = models.CharField(
        max_length=20, choices=PAYMENT_MODE_CHOICES, default='bank_transfer')
    bank_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    failure_reason = models.TextField(blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    reconciled_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reconciled_payments')

    class Meta:
        ordering = ['-payroll_period__year', '-payroll_period__month']

    def __str__(self):
        return f"{self.employee} - {self.amount} ({self.get_status_display()})"


class Reimbursement(TenantAwareModel, TimeStampedModel):
    """Employee reimbursement claims."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    CATEGORY_CHOICES = [
        ('lta', 'Leave Travel Allowance'),
        ('medical', 'Medical Reimbursement'),
        ('fuel', 'Fuel / Conveyance'),
        ('mobile', 'Mobile / Internet'),
        ('food', 'Food / Meal'),
        ('books', 'Books / Periodicals'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(
        'employees.Employee', on_delete=models.CASCADE, related_name='reimbursements')
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    claim_date = models.DateField()
    receipt_date = models.DateField(null=True, blank=True)
    receipt = models.FileField(upload_to='payroll/reimbursements/', blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    payroll_period = models.ForeignKey(
        PayrollPeriod, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reimbursements',
        help_text='Payroll period in which this was paid')
    approved_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_reimbursements')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-claim_date']

    def __str__(self):
        return f"{self.employee} - {self.get_category_display()} ({self.amount})"
