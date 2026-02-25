from django.contrib import admin
from .models import (
    PayComponent, SalaryStructure, SalaryStructureComponent,
    EmployeeSalaryStructure, EmployeeSalaryComponent,
    PayrollPeriod, PayrollEntry, PayrollEntryComponent,
    SalaryHold, SalaryRevision,
    PFConfiguration, ESIConfiguration, ProfessionalTaxSlab,
    LWFConfiguration, StatutoryContribution,
    TaxRegimeChoice, InvestmentDeclaration, InvestmentProof, TaxComputation,
    BankFile, Payslip, PaymentRegister, Reimbursement,
)


# Section 1: Salary Structure

@admin.register(PayComponent)
class PayComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'component_type', 'category', 'calculation_type', 'is_active']
    list_filter = ['component_type', 'category', 'is_statutory', 'is_active']
    search_fields = ['name', 'code']


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'job_grade', 'base_amount', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(SalaryStructureComponent)
class SalaryStructureComponentAdmin(admin.ModelAdmin):
    list_display = ['salary_structure', 'pay_component', 'calculation_type', 'value']
    list_filter = ['calculation_type']
    search_fields = ['salary_structure__name', 'pay_component__name']


@admin.register(EmployeeSalaryStructure)
class EmployeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['employee', 'salary_structure', 'ctc', 'effective_from', 'status']
    list_filter = ['status']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(EmployeeSalaryComponent)
class EmployeeSalaryComponentAdmin(admin.ModelAdmin):
    list_display = ['employee_salary', 'pay_component', 'monthly_amount', 'annual_amount']
    search_fields = ['pay_component__name']


# Section 2: Payroll Processing

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'month', 'year', 'status', 'total_net', 'employee_count']
    list_filter = ['status', 'year']
    search_fields = ['name']


@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'gross_earnings', 'total_deductions', 'net_pay', 'status']
    list_filter = ['status']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(PayrollEntryComponent)
class PayrollEntryComponentAdmin(admin.ModelAdmin):
    list_display = ['payroll_entry', 'pay_component', 'amount', 'is_arrear']
    list_filter = ['is_arrear']


@admin.register(SalaryHold)
class SalaryHoldAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'status']
    list_filter = ['status']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(SalaryRevision)
class SalaryRevisionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'old_ctc', 'new_ctc', 'effective_from', 'status']
    list_filter = ['status']
    search_fields = ['employee__first_name', 'employee__last_name']


# Section 3: Statutory Compliance

@admin.register(PFConfiguration)
class PFConfigurationAdmin(admin.ModelAdmin):
    list_display = ['pf_number', 'employee_contribution_rate', 'employer_contribution_rate', 'pf_ceiling', 'is_active']
    list_filter = ['is_active']


@admin.register(ESIConfiguration)
class ESIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['esi_number', 'employee_rate', 'employer_rate', 'wage_ceiling', 'is_active']
    list_filter = ['is_active']


@admin.register(ProfessionalTaxSlab)
class ProfessionalTaxSlabAdmin(admin.ModelAdmin):
    list_display = ['state', 'salary_from', 'salary_to', 'tax_amount', 'is_active']
    list_filter = ['state', 'is_active']
    search_fields = ['state']


@admin.register(LWFConfiguration)
class LWFConfigurationAdmin(admin.ModelAdmin):
    list_display = ['state', 'employee_contribution', 'employer_contribution', 'frequency', 'is_active']
    list_filter = ['state', 'is_active']


@admin.register(StatutoryContribution)
class StatutoryContributionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'contribution_type', 'amount']
    list_filter = ['contribution_type']
    search_fields = ['employee__first_name', 'employee__last_name']


# Section 4: Tax & Investment

@admin.register(TaxRegimeChoice)
class TaxRegimeChoiceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'financial_year', 'regime', 'locked']
    list_filter = ['regime', 'financial_year']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(InvestmentDeclaration)
class InvestmentDeclarationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'financial_year', 'section', 'declared_amount', 'verified_amount', 'status']
    list_filter = ['status', 'section', 'financial_year']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(InvestmentProof)
class InvestmentProofAdmin(admin.ModelAdmin):
    list_display = ['declaration', 'document_name', 'amount', 'status']
    list_filter = ['status']


@admin.register(TaxComputation)
class TaxComputationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'financial_year', 'regime', 'total_income', 'taxable_income', 'total_tax_liability']
    list_filter = ['financial_year', 'regime']
    search_fields = ['employee__first_name', 'employee__last_name']


# Section 5: Payout & Reports

@admin.register(BankFile)
class BankFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'payroll_period', 'bank_format', 'total_amount', 'employee_count', 'status']
    list_filter = ['status', 'bank_format']


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'is_emailed', 'is_viewed']
    list_filter = ['is_emailed', 'is_viewed']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(PaymentRegister)
class PaymentRegisterAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'amount', 'payment_mode', 'status']
    list_filter = ['status', 'payment_mode']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):
    list_display = ['employee', 'category', 'amount', 'approved_amount', 'claim_date', 'status']
    list_filter = ['status', 'category']
    search_fields = ['employee__first_name', 'employee__last_name']
