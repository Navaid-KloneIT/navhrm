from django import forms
from .models import (
    PayComponent, SalaryStructure, SalaryStructureComponent,
    EmployeeSalaryStructure, EmployeeSalaryComponent,
    PayrollPeriod, PayrollEntry, PayrollEntryComponent,
    SalaryHold, SalaryRevision,
    PFConfiguration, ESIConfiguration, ProfessionalTaxSlab,
    LWFConfiguration,
    TaxRegimeChoice, InvestmentDeclaration, InvestmentProof,
    BankFile, Payslip, PaymentRegister, Reimbursement,
)
from apps.employees.models import Employee


# ==========================================================================
# SECTION 1: SALARY STRUCTURE
# ==========================================================================

class PayComponentForm(forms.ModelForm):
    class Meta:
        model = PayComponent
        exclude = ['tenant']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'component_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'calculation_type': forms.Select(attrs={'class': 'form-select'}),
            'default_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_statutory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        exclude = ['tenant']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'job_grade': forms.Select(attrs={'class': 'form-select'}),
            'base_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            from apps.organization.models import JobGrade
            self.fields['job_grade'].queryset = JobGrade.all_objects.filter(tenant=tenant)


class SalaryStructureComponentForm(forms.ModelForm):
    class Meta:
        model = SalaryStructureComponent
        fields = ['pay_component', 'calculation_type', 'value']
        widgets = {
            'pay_component': forms.Select(attrs={'class': 'form-select'}),
            'calculation_type': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['pay_component'].queryset = PayComponent.all_objects.filter(
                tenant=tenant, is_active=True)


class EmployeeSalaryStructureForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalaryStructure
        fields = ['employee', 'salary_structure', 'ctc', 'effective_from',
                  'effective_to', 'status', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'salary_structure': forms.Select(attrs={'class': 'form-select'}),
            'ctc': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'effective_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active')
            self.fields['salary_structure'].queryset = SalaryStructure.all_objects.filter(
                tenant=tenant, is_active=True)


# ==========================================================================
# SECTION 2: PAYROLL PROCESSING
# ==========================================================================

class PayrollPeriodForm(forms.ModelForm):
    class Meta:
        model = PayrollPeriod
        fields = ['name', 'month', 'year', 'start_date', 'end_date',
                  'payment_date', 'remarks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('End date must be on or after the start date.')
        return cleaned_data


class SalaryHoldForm(forms.ModelForm):
    class Meta:
        model = SalaryHold
        fields = ['employee', 'payroll_period', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'payroll_period': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active')
            self.fields['payroll_period'].queryset = PayrollPeriod.all_objects.filter(
                tenant=tenant)


class SalaryHoldReleaseForm(forms.Form):
    release_remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class SalaryRevisionForm(forms.ModelForm):
    class Meta:
        model = SalaryRevision
        fields = ['employee', 'new_ctc', 'effective_from', 'revision_date',
                  'arrears_from', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'new_ctc': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'revision_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'arrears_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active')


class SalaryRevisionApprovalForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class PayrollApprovalForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class PayrollEntryHoldForm(forms.Form):
    hold_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


# ==========================================================================
# SECTION 3: STATUTORY COMPLIANCE
# ==========================================================================

class PFConfigurationForm(forms.ModelForm):
    class Meta:
        model = PFConfiguration
        exclude = ['tenant']
        widgets = {
            'pf_number': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_contribution_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'employer_contribution_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'eps_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'admin_charge_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'edli_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'pf_ceiling': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ESIConfigurationForm(forms.ModelForm):
    class Meta:
        model = ESIConfiguration
        exclude = ['tenant']
        widgets = {
            'esi_number': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'employer_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'wage_ceiling': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ProfessionalTaxSlabForm(forms.ModelForm):
    class Meta:
        model = ProfessionalTaxSlab
        exclude = ['tenant']
        widgets = {
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_from': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_to': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        salary_from = cleaned_data.get('salary_from')
        salary_to = cleaned_data.get('salary_to')
        if salary_from and salary_to and salary_to < salary_from:
            raise forms.ValidationError('Salary To must be greater than or equal to Salary From.')
        return cleaned_data


class LWFConfigurationForm(forms.ModelForm):
    class Meta:
        model = LWFConfiguration
        exclude = ['tenant']
        widgets = {
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_contribution': forms.NumberInput(attrs={'class': 'form-control'}),
            'employer_contribution': forms.NumberInput(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# ==========================================================================
# SECTION 4: TAX & INVESTMENT
# ==========================================================================

class TaxRegimeChoiceForm(forms.ModelForm):
    class Meta:
        model = TaxRegimeChoice
        fields = ['employee', 'financial_year', 'regime']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'financial_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-26'}),
            'regime': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active')


class InvestmentDeclarationForm(forms.ModelForm):
    class Meta:
        model = InvestmentDeclaration
        fields = ['employee', 'financial_year', 'section', 'description',
                  'declared_amount']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'financial_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-26'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'declared_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active')


class InvestmentDeclarationVerifyForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('verified', 'Verified'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    verified_amount = forms.DecimalField(
        max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class InvestmentProofForm(forms.ModelForm):
    class Meta:
        model = InvestmentProof
        fields = ['document_name', 'file', 'amount', 'remarks']
        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ==========================================================================
# SECTION 5: PAYOUT & REPORTS
# ==========================================================================

class BankFileGenerateForm(forms.Form):
    payroll_period = forms.ModelChoiceField(
        queryset=PayrollPeriod.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    bank_format = forms.ChoiceField(
        choices=BankFile.BANK_FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['payroll_period'].queryset = PayrollPeriod.all_objects.filter(
                tenant=tenant, status__in=['approved', 'paid'])


class PaymentReconcileForm(forms.Form):
    transaction_reference = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    status = forms.ChoiceField(
        choices=[('reconciled', 'Reconciled'), ('failed', 'Failed')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    failure_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class ReimbursementForm(forms.ModelForm):
    class Meta:
        model = Reimbursement
        fields = ['employee', 'category', 'description', 'amount',
                  'claim_date', 'receipt_date', 'receipt']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'claim_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active')


class ReimbursementApprovalForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    approved_amount = forms.DecimalField(
        max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
