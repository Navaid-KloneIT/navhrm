from django import forms
from apps.employees.models import Employee
from apps.organization.models import Department
from .models import (
    LaborLaw, LaborLawCompliance,
    EmploymentContract, ContractAmendment,
    CompliancePolicy, PolicyVersion, PolicyAcknowledgment,
    DisciplinaryIncident, WarningRecord, DisciplinaryAppeal,
    Grievance, GrievanceInvestigation,
    MusterRoll, WageRegister, InspectionReport,
)


# ===========================================================================
# Labor Law Compliance Forms
# ===========================================================================

class LaborLawForm(forms.ModelForm):
    class Meta:
        model = LaborLaw
        fields = [
            'name', 'jurisdiction', 'category', 'description',
            'effective_date', 'expiry_date', 'status',
            'compliance_requirements', 'penalties', 'reference_url', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jurisdiction': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'compliance_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'penalties': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reference_url': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expiry_date'].required = False
        self.fields['reference_url'].required = False


class LaborLawComplianceForm(forms.ModelForm):
    class Meta:
        model = LaborLawCompliance
        fields = [
            'labor_law', 'department', 'compliance_status',
            'review_date', 'next_review_date', 'responsible_person',
            'compliance_notes', 'action_required',
        ]
        widgets = {
            'labor_law': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'compliance_status': forms.Select(attrs={'class': 'form-select'}),
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsible_person': forms.Select(attrs={'class': 'form-select'}),
            'compliance_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'action_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['labor_law'].queryset = LaborLaw.all_objects.filter(tenant=tenant)
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['responsible_person'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['department'].required = False
        self.fields['next_review_date'].required = False
        self.fields['responsible_person'].required = False


# ===========================================================================
# Contract Management Forms
# ===========================================================================

class EmploymentContractForm(forms.ModelForm):
    class Meta:
        model = EmploymentContract
        fields = [
            'employee', 'contract_type', 'contract_number',
            'start_date', 'end_date', 'terms', 'salary_details',
            'probation_period_months', 'notice_period_days',
            'status', 'signed_date', 'signed_by', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'salary_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'probation_period_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notice_period_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'signed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'signed_by': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['signed_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['end_date'].required = False
        self.fields['signed_date'].required = False
        self.fields['signed_by'].required = False
        self.fields['contract_number'].required = False


class ContractAmendmentForm(forms.ModelForm):
    class Meta:
        model = ContractAmendment
        fields = [
            'amendment_type', 'amendment_date', 'description',
            'old_value', 'new_value', 'effective_date',
            'approved_by', 'status', 'notes',
        ]
        widgets = {
            'amendment_type': forms.Select(attrs={'class': 'form-select'}),
            'amendment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'old_value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'new_value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['approved_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['approved_by'].required = False


# ===========================================================================
# Policy Management Forms
# ===========================================================================

class CompliancePolicyForm(forms.ModelForm):
    class Meta:
        model = CompliancePolicy
        fields = [
            'title', 'category', 'description', 'content',
            'version', 'effective_date', 'expiry_date',
            'status', 'approved_by', 'department',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['approved_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
        self.fields['expiry_date'].required = False
        self.fields['approved_by'].required = False
        self.fields['department'].required = False


class PolicyVersionForm(forms.ModelForm):
    class Meta:
        model = PolicyVersion
        fields = [
            'version_number', 'changes_summary', 'content',
            'created_by', 'effective_date',
        ]
        widgets = {
            'version_number': forms.TextInput(attrs={'class': 'form-control'}),
            'changes_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'created_by': forms.Select(attrs={'class': 'form-select'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['created_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['created_by'].required = False


class PolicyAcknowledgmentForm(forms.ModelForm):
    class Meta:
        model = PolicyAcknowledgment
        fields = ['employee', 'is_acknowledged', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


# ===========================================================================
# Disciplinary Actions Forms
# ===========================================================================

class DisciplinaryIncidentForm(forms.ModelForm):
    class Meta:
        model = DisciplinaryIncident
        fields = [
            'employee', 'incident_date', 'reported_by',
            'incident_type', 'severity', 'description',
            'witness', 'location', 'status', 'resolution_notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'incident_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reported_by': forms.Select(attrs={'class': 'form-select'}),
            'incident_type': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'witness': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['reported_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['reported_by'].required = False


class WarningRecordForm(forms.ModelForm):
    class Meta:
        model = WarningRecord
        fields = [
            'employee', 'warning_type', 'issued_date',
            'issued_by', 'reason', 'action_required',
            'deadline', 'status', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'warning_type': forms.Select(attrs={'class': 'form-select'}),
            'issued_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'issued_by': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'action_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['issued_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['issued_by'].required = False
        self.fields['deadline'].required = False


class DisciplinaryAppealForm(forms.ModelForm):
    class Meta:
        model = DisciplinaryAppeal
        fields = [
            'employee', 'appeal_date', 'grounds',
            'supporting_documents', 'reviewed_by',
            'review_date', 'decision', 'decision_notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'appeal_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'grounds': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supporting_documents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reviewed_by': forms.Select(attrs={'class': 'form-select'}),
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'decision': forms.Select(attrs={'class': 'form-select'}),
            'decision_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['reviewed_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['reviewed_by'].required = False
        self.fields['review_date'].required = False


# ===========================================================================
# Grievance Handling Forms
# ===========================================================================

class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = [
            'employee', 'grievance_date', 'category', 'subject',
            'description', 'priority', 'status', 'assigned_to',
            'resolution_date', 'resolution_summary', 'is_anonymous',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'grievance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'resolution_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resolution_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['assigned_to'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['assigned_to'].required = False
        self.fields['resolution_date'].required = False


class GrievanceInvestigationForm(forms.ModelForm):
    class Meta:
        model = GrievanceInvestigation
        fields = [
            'investigator', 'start_date', 'end_date',
            'findings', 'evidence', 'recommendation', 'status',
        ]
        widgets = {
            'investigator': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'evidence': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['investigator'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['investigator'].required = False
        self.fields['end_date'].required = False


# ===========================================================================
# Statutory Registers Forms
# ===========================================================================

class MusterRollForm(forms.ModelForm):
    class Meta:
        model = MusterRoll
        fields = [
            'month', 'year', 'department', 'generated_date',
            'generated_by', 'total_employees', 'total_working_days',
            'notes', 'status',
        ]
        widgets = {
            'month': forms.Select(attrs={'class': 'form-select'}, choices=[
                (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
            ]),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2099}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'generated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'generated_by': forms.Select(attrs={'class': 'form-select'}),
            'total_employees': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_working_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['generated_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['department'].required = False
        self.fields['generated_by'].required = False


class WageRegisterForm(forms.ModelForm):
    class Meta:
        model = WageRegister
        fields = [
            'month', 'year', 'department', 'generated_date',
            'generated_by', 'total_gross', 'total_deductions',
            'total_net', 'notes', 'status',
        ]
        widgets = {
            'month': forms.Select(attrs={'class': 'form-select'}, choices=[
                (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
            ]),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2099}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'generated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'generated_by': forms.Select(attrs={'class': 'form-select'}),
            'total_gross': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'total_deductions': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'total_net': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['generated_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['department'].required = False
        self.fields['generated_by'].required = False


class InspectionReportForm(forms.ModelForm):
    class Meta:
        model = InspectionReport
        fields = [
            'inspection_date', 'inspector_name', 'inspector_designation',
            'inspection_type', 'department', 'areas_inspected',
            'findings', 'compliance_status', 'recommendations',
            'follow_up_date', 'status', 'notes',
        ]
        widgets = {
            'inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inspector_name': forms.TextInput(attrs={'class': 'form-control'}),
            'inspector_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'inspection_type': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'areas_inspected': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'compliance_status': forms.Select(attrs={'class': 'form-select'}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
        self.fields['department'].required = False
        self.fields['inspector_designation'].required = False
        self.fields['follow_up_date'].required = False
