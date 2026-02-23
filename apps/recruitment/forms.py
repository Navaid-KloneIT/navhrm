from django import forms
from apps.organization.models import Department, Designation
from apps.employees.models import Employee
from .models import (
    JobTemplate, JobRequisition, RequisitionApproval,
    Candidate, JobApplication,
    InterviewRound, Interview, InterviewFeedback,
    OfferLetter,
)


# ---------------------------------------------------------------------------
# Job Requisition Forms
# ---------------------------------------------------------------------------

class JobTemplateForm(forms.ModelForm):
    class Meta:
        model = JobTemplate
        fields = ['title', 'description', 'requirements', 'responsibilities', 'benefits', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class JobRequisitionForm(forms.ModelForm):
    class Meta:
        model = JobRequisition
        fields = [
            'title', 'code', 'department', 'designation', 'location',
            'employment_type', 'experience_min', 'experience_max',
            'salary_min', 'salary_max', 'description', 'requirements',
            'responsibilities', 'benefits', 'positions', 'status', 'priority',
            'requested_by', 'publish_date', 'closing_date', 'is_published',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., JR-2024-001'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'experience_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'positions': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'requested_by': forms.Select(attrs={'class': 'form-select'}),
            'publish_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['designation'].queryset = Designation.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['requested_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class RequisitionApprovalForm(forms.ModelForm):
    class Meta:
        model = RequisitionApproval
        fields = ['approver', 'level', 'status', 'comments']
        widgets = {
            'approver': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['approver'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


# ---------------------------------------------------------------------------
# Candidate Forms
# ---------------------------------------------------------------------------

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'resume', 'photo',
            'current_company', 'current_designation', 'experience_years',
            'current_salary', 'expected_salary', 'skills', 'location',
            'linkedin_url', 'source', 'notes', 'is_active',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control'}),
            'current_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': 0}),
            'current_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Python, Django, JavaScript'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['job', 'candidate', 'cover_letter', 'resume', 'status', 'source', 'notes', 'rating']
        widgets = {
            'job': forms.Select(attrs={'class': 'form-select'}),
            'candidate': forms.Select(attrs={'class': 'form-select'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['job'].queryset = JobRequisition.all_objects.filter(tenant=tenant)
            self.fields['candidate'].queryset = Candidate.all_objects.filter(tenant=tenant, is_active=True)


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status', 'notes', 'rating']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }


# ---------------------------------------------------------------------------
# Interview Forms
# ---------------------------------------------------------------------------

class InterviewRoundForm(forms.ModelForm):
    class Meta:
        model = InterviewRound
        fields = ['name', 'round_number', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'round_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'application', 'round', 'round_name', 'scheduled_date',
            'scheduled_time', 'duration_minutes', 'location', 'mode',
            'status', 'notes', 'result',
        ]
        widgets = {
            'application': forms.Select(attrs={'class': 'form-select'}),
            'round': forms.Select(attrs={'class': 'form-select'}),
            'round_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Technical Round 1'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room / Meeting link'}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'result': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['application'].queryset = JobApplication.all_objects.filter(tenant=tenant)
            self.fields['round'].queryset = InterviewRound.all_objects.filter(tenant=tenant, is_active=True)


class InterviewFeedbackForm(forms.ModelForm):
    class Meta:
        model = InterviewFeedback
        fields = [
            'technical_rating', 'communication_rating', 'cultural_fit_rating',
            'overall_rating', 'strengths', 'weaknesses', 'comments', 'recommendation',
        ]
        widgets = {
            'technical_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'communication_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'cultural_fit_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendation': forms.Select(attrs={'class': 'form-select'}),
        }


# ---------------------------------------------------------------------------
# Offer Forms
# ---------------------------------------------------------------------------

class OfferLetterForm(forms.ModelForm):
    class Meta:
        model = OfferLetter
        fields = [
            'application', 'offered_designation', 'offered_department',
            'offered_salary', 'salary_currency', 'joining_date', 'expiry_date',
            'probation_months', 'benefits', 'terms_conditions', 'status', 'remarks',
        ]
        widgets = {
            'application': forms.Select(attrs={'class': 'form-select'}),
            'offered_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'offered_department': forms.Select(attrs={'class': 'form-select'}),
            'offered_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_currency': forms.TextInput(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'probation_months': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['application'].queryset = JobApplication.all_objects.filter(tenant=tenant)
            self.fields['offered_department'].queryset = Department.all_objects.filter(tenant=tenant, is_active=True)


# ---------------------------------------------------------------------------
# Public Career Page Form
# ---------------------------------------------------------------------------

class CareerApplicationForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    resume = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    cover_letter = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    current_company = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    experience_years = forms.DecimalField(max_digits=4, decimal_places=1, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': 0}))
    expected_salary = forms.DecimalField(max_digits=12, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    linkedin_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
