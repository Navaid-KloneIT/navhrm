from django import forms
from apps.employees.models import Employee
from apps.organization.models import Department, Designation
from .models import (
    TalentAssessment,
    CriticalPosition, SuccessionCandidate,
    CareerPath, CareerPathStep, EmployeeCareerPlan,
    InternalJobPosting, TransferApplication,
    TalentReviewSession, TalentReviewParticipant,
    FlightRiskAssessment, RetentionPlan, RetentionAction,
)


# ===========================================================================
# Talent Pool Forms
# ===========================================================================

class TalentAssessmentForm(forms.ModelForm):
    class Meta:
        model = TalentAssessment
        fields = [
            'employee', 'performance_rating', 'potential_rating',
            'assessment_date', 'assessed_by', 'notes', 'is_active',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'performance_rating': forms.Select(attrs={'class': 'form-select'}),
            'potential_rating': forms.Select(attrs={'class': 'form-select'}),
            'assessment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assessed_by': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['assessed_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['assessed_by'].required = False


# ===========================================================================
# Succession Planning Forms
# ===========================================================================

class CriticalPositionForm(forms.ModelForm):
    class Meta:
        model = CriticalPosition
        fields = [
            'designation', 'department', 'criticality',
            'incumbent', 'reason', 'status',
        ]
        widgets = {
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'criticality': forms.Select(attrs={'class': 'form-select'}),
            'incumbent': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['incumbent'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['department'].required = False
        self.fields['incumbent'].required = False


class SuccessionCandidateForm(forms.ModelForm):
    class Meta:
        model = SuccessionCandidate
        fields = [
            'employee', 'readiness', 'status',
            'development_needs', 'strengths', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'readiness': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'development_needs': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


# ===========================================================================
# Career Pathing Forms
# ===========================================================================

class CareerPathForm(forms.ModelForm):
    class Meta:
        model = CareerPath
        fields = ['name', 'description', 'department', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
        self.fields['department'].required = False


class CareerPathStepForm(forms.ModelForm):
    class Meta:
        model = CareerPathStep
        fields = [
            'sequence', 'designation', 'required_experience_years',
            'required_skills', 'required_competencies', 'description',
        ]
        widgets = {
            'sequence': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'required_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'required_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'required_competencies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)


class EmployeeCareerPlanForm(forms.ModelForm):
    class Meta:
        model = EmployeeCareerPlan
        fields = [
            'employee', 'career_path', 'current_step',
            'target_step', 'target_date', 'status', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'career_path': forms.Select(attrs={'class': 'form-select'}),
            'current_step': forms.Select(attrs={'class': 'form-select'}),
            'target_step': forms.Select(attrs={'class': 'form-select'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['career_path'].queryset = CareerPath.all_objects.filter(tenant=tenant)
            self.fields['current_step'].queryset = CareerPathStep.all_objects.filter(tenant=tenant)
            self.fields['target_step'].queryset = CareerPathStep.all_objects.filter(tenant=tenant)
        self.fields['current_step'].required = False
        self.fields['target_step'].required = False


# ===========================================================================
# Internal Mobility Forms
# ===========================================================================

class InternalJobPostingForm(forms.ModelForm):
    class Meta:
        model = InternalJobPosting
        fields = [
            'title', 'department', 'designation', 'description',
            'requirements', 'positions', 'status', 'posted_by', 'closing_date',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'positions': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'posted_by': forms.Select(attrs={'class': 'form-select'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['posted_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['department'].required = False
        self.fields['designation'].required = False
        self.fields['posted_by'].required = False


class TransferApplicationForm(forms.ModelForm):
    class Meta:
        model = TransferApplication
        fields = [
            'posting', 'employee', 'current_department',
            'current_designation', 'reason',
        ]
        widgets = {
            'posting': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'current_department': forms.Select(attrs={'class': 'form-select'}),
            'current_designation': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['posting'].queryset = InternalJobPosting.all_objects.filter(tenant=tenant, status='open')
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['current_department'].queryset = Department.all_objects.filter(tenant=tenant)
            self.fields['current_designation'].queryset = Designation.all_objects.filter(tenant=tenant)
        self.fields['current_department'].required = False
        self.fields['current_designation'].required = False


class TransferApplicationReviewForm(forms.ModelForm):
    class Meta:
        model = TransferApplication
        fields = ['status', 'reviewed_by', 'review_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reviewed_by': forms.Select(attrs={'class': 'form-select'}),
            'review_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['reviewed_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['reviewed_by'].required = False


# ===========================================================================
# Talent Review Forms
# ===========================================================================

class TalentReviewSessionForm(forms.ModelForm):
    class Meta:
        model = TalentReviewSession
        fields = [
            'name', 'review_period_start', 'review_period_end',
            'session_date', 'status', 'facilitator', 'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'review_period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'review_period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'facilitator': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['facilitator'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['facilitator'].required = False
        self.fields['session_date'].required = False


class TalentReviewParticipantForm(forms.ModelForm):
    class Meta:
        model = TalentReviewParticipant
        fields = [
            'employee', 'initial_performance_rating', 'initial_potential_rating',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'initial_performance_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'initial_potential_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['initial_performance_rating'].required = False
        self.fields['initial_potential_rating'].required = False


class TalentReviewCalibrationForm(forms.ModelForm):
    class Meta:
        model = TalentReviewParticipant
        fields = [
            'calibrated_performance_rating', 'calibrated_potential_rating',
            'calibration_notes', 'development_recommendations',
        ]
        widgets = {
            'calibrated_performance_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'calibrated_potential_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'calibration_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'development_recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ===========================================================================
# Retention Strategy Forms
# ===========================================================================

class FlightRiskAssessmentForm(forms.ModelForm):
    class Meta:
        model = FlightRiskAssessment
        fields = [
            'employee', 'risk_level', 'risk_factors', 'impact_if_lost',
            'assessed_date', 'assessed_by', 'is_active', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'risk_factors': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'impact_if_lost': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assessed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assessed_by': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['assessed_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['assessed_by'].required = False


class RetentionPlanForm(forms.ModelForm):
    class Meta:
        model = RetentionPlan
        fields = [
            'employee', 'flight_risk', 'title', 'description',
            'responsible_person', 'target_date', 'status', 'outcome_notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'flight_risk': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsible_person': forms.Select(attrs={'class': 'form-select'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'outcome_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['flight_risk'].queryset = FlightRiskAssessment.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['responsible_person'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['flight_risk'].required = False
        self.fields['responsible_person'].required = False


class RetentionActionForm(forms.ModelForm):
    class Meta:
        model = RetentionAction
        fields = ['description', 'assigned_to', 'due_date', 'status', 'completion_notes']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'completion_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['assigned_to'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
        self.fields['assigned_to'].required = False
