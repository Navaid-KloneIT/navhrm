from django import forms
from apps.employees.models import Employee
from .models import (
    EngagementSurvey, EngagementSurveyQuestion, EngagementSurveyQuestionOption, EngagementActionPlan,
    WellbeingProgram, WellbeingResource, WellnessChallenge, ChallengeParticipant,
    FlexibleWorkArrangement, RemoteWorkPolicy, WorkLifeBalanceAssessment,
    EAPProgram, CounselingSession, EAPUtilization,
    CompanyValue, CultureAssessment, CultureAssessmentResponse, ValueNomination,
    TeamEvent, EventParticipant, InterestGroup, InterestGroupMember,
    VolunteerActivity, VolunteerParticipant,
)


# =============================================================================
# SUB-MODULE 1: ENGAGEMENT SURVEYS
# =============================================================================

class SurveyForm(forms.ModelForm):
    class Meta:
        model = EngagementSurvey
        fields = [
            'title', 'description', 'survey_type', 'status',
            'start_date', 'end_date', 'is_anonymous', 'target_audience',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'survey_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class SurveyQuestionForm(forms.ModelForm):
    class Meta:
        model = EngagementSurveyQuestion
        fields = ['question_text', 'question_type', 'order', 'is_required']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class SurveyQuestionOptionForm(forms.ModelForm):
    class Meta:
        model = EngagementSurveyQuestionOption
        fields = ['option_text', 'order']
        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class SurveyActionPlanForm(forms.ModelForm):
    class Meta:
        model = EngagementActionPlan
        fields = [
            'title', 'description', 'assigned_to',
            'priority', 'status', 'due_date',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['assigned_to'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
        self.fields['assigned_to'].required = False


# =============================================================================
# SUB-MODULE 2: WELLBEING PROGRAMS
# =============================================================================

class WellbeingProgramForm(forms.ModelForm):
    class Meta:
        model = WellbeingProgram
        fields = [
            'name', 'description', 'category', 'status',
            'start_date', 'end_date', 'max_participants',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class WellbeingResourceForm(forms.ModelForm):
    class Meta:
        model = WellbeingResource
        fields = [
            'title', 'description', 'resource_type', 'category',
            'url', 'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resource_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class WellnessChallengeForm(forms.ModelForm):
    class Meta:
        model = WellnessChallenge
        fields = [
            'title', 'description', 'challenge_type',
            'start_date', 'end_date', 'goal_target', 'goal_unit', 'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'challenge_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'goal_target': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'goal_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. steps, minutes, glasses'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class ChallengeParticipantForm(forms.ModelForm):
    class Meta:
        model = ChallengeParticipant
        fields = ['employee', 'progress']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )


# =============================================================================
# SUB-MODULE 3: WORK-LIFE BALANCE
# =============================================================================

class FlexibleWorkArrangementForm(forms.ModelForm):
    class Meta:
        model = FlexibleWorkArrangement
        fields = [
            'employee', 'arrangement_type', 'status',
            'start_date', 'end_date', 'days_per_week', 'approved_by', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'arrangement_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'days_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 7}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
            self.fields['approved_by'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
        self.fields['approved_by'].required = False
        self.fields['end_date'].required = False


class RemoteWorkPolicyForm(forms.ModelForm):
    class Meta:
        model = RemoteWorkPolicy
        fields = [
            'name', 'description', 'eligibility_criteria',
            'equipment_provided', 'communication_expectations', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'eligibility_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'equipment_provided': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'communication_expectations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class WorkLifeBalanceAssessmentForm(forms.ModelForm):
    class Meta:
        model = WorkLifeBalanceAssessment
        fields = [
            'employee', 'assessment_date',
            'work_satisfaction', 'life_satisfaction', 'stress_level', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'assessment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'work_satisfaction': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'life_satisfaction': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'stress_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )


# =============================================================================
# SUB-MODULE 4: EMPLOYEE ASSISTANCE
# =============================================================================

class EAPProgramForm(forms.ModelForm):
    class Meta:
        model = EAPProgram
        fields = [
            'name', 'description', 'provider',
            'contact_info', 'service_type', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'provider': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class CounselingSessionForm(forms.ModelForm):
    class Meta:
        model = CounselingSession
        fields = [
            'employee', 'program', 'session_type', 'session_date',
            'duration_minutes', 'status', 'counselor_name',
            'is_confidential', 'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'program': forms.Select(attrs={'class': 'form-select'}),
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'session_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'counselor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
            self.fields['program'].queryset = EAPProgram.all_objects.filter(
                tenant=tenant, is_active=True
            )


class EAPUtilizationForm(forms.ModelForm):
    class Meta:
        model = EAPUtilization
        fields = [
            'period_start', 'period_end',
            'total_sessions', 'total_participants', 'satisfaction_score',
        ]
        widgets = {
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_sessions': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'satisfaction_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5, 'step': '0.1'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['satisfaction_score'].required = False


# =============================================================================
# SUB-MODULE 5: CULTURE & VALUES
# =============================================================================

class CompanyValueForm(forms.ModelForm):
    class Meta:
        model = CompanyValue
        fields = ['name', 'description', 'icon', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ri-heart-line'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class CultureAssessmentForm(forms.ModelForm):
    class Meta:
        model = CultureAssessment
        fields = ['title', 'description', 'assessment_date', 'status', 'created_by']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assessment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'created_by': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['created_by'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
        self.fields['created_by'].required = False


class CultureAssessmentResponseForm(forms.ModelForm):
    class Meta:
        model = CultureAssessmentResponse
        fields = ['alignment_score', 'comments']
        widgets = {
            'alignment_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)


class ValueNominationForm(forms.ModelForm):
    class Meta:
        model = ValueNomination
        fields = ['value', 'nominee', 'nominated_by', 'reason', 'status', 'is_featured']
        widgets = {
            'value': forms.Select(attrs={'class': 'form-select'}),
            'nominee': forms.Select(attrs={'class': 'form-select'}),
            'nominated_by': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['value'].queryset = CompanyValue.all_objects.filter(
                tenant=tenant, is_active=True
            )
            self.fields['nominee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
            self.fields['nominated_by'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )


# =============================================================================
# SUB-MODULE 6: SOCIAL CONNECT
# =============================================================================

class TeamEventForm(forms.ModelForm):
    class Meta:
        model = TeamEvent
        fields = [
            'title', 'description', 'event_type', 'date',
            'location', 'organizer', 'max_participants', 'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'organizer': forms.Select(attrs={'class': 'form-select'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['organizer'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
        self.fields['organizer'].required = False


class EventParticipantForm(forms.ModelForm):
    class Meta:
        model = EventParticipant
        fields = ['employee', 'rsvp_status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'rsvp_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )


class InterestGroupForm(forms.ModelForm):
    class Meta:
        model = InterestGroup
        fields = ['name', 'description', 'category', 'created_by', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'created_by': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['created_by'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
        self.fields['created_by'].required = False


class InterestGroupMemberForm(forms.ModelForm):
    class Meta:
        model = InterestGroupMember
        fields = ['employee', 'role']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )


class VolunteerActivityForm(forms.ModelForm):
    class Meta:
        model = VolunteerActivity
        fields = [
            'title', 'description', 'activity_date', 'location',
            'hours_required', 'max_volunteers', 'organizer', 'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activity_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'hours_required': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.5'}),
            'max_volunteers': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'organizer': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['organizer'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
        self.fields['organizer'].required = False


class VolunteerParticipantForm(forms.ModelForm):
    class Meta:
        model = VolunteerParticipant
        fields = ['employee', 'hours_contributed', 'feedback']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'hours_contributed': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.5'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(
                tenant=tenant, status='active'
            )
