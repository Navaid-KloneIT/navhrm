from django import forms
from apps.employees.models import Employee
from .models import (
    GoalPeriod, Goal, GoalUpdate,
    ReviewCycle, PerformanceReview, ReviewGoalRating,
    PeerReviewer, PeerFeedback,
    Feedback, OneOnOneMeeting, MeetingActionItem,
    PIP, PIPCheckpoint, WarningLetter, CoachingNote,
)


# ===========================================================================
# Goal Setting Forms
# ===========================================================================

class GoalPeriodForm(forms.ModelForm):
    class Meta:
        model = GoalPeriod
        fields = ['name', 'period_type', 'start_date', 'end_date', 'status', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            'period', 'employee', 'parent_goal', 'title', 'description',
            'goal_type', 'weight', 'target_value', 'current_value',
            'progress', 'status', 'visibility', 'start_date', 'due_date',
        ]
        widgets = {
            'period': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'parent_goal': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goal_type': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01'}),
            'target_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 100%, 50 units'}),
            'current_value': forms.TextInput(attrs={'class': 'form-control'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['period'].queryset = GoalPeriod.all_objects.filter(tenant=tenant)
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['parent_goal'].queryset = Goal.all_objects.filter(tenant=tenant)
            self.fields['parent_goal'].required = False


class GoalUpdateForm(forms.ModelForm):
    class Meta:
        model = GoalUpdate
        fields = ['progress', 'current_value', 'note']
        widgets = {
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'current_value': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ===========================================================================
# Performance Review Forms
# ===========================================================================

class ReviewCycleForm(forms.ModelForm):
    class Meta:
        model = ReviewCycle
        fields = [
            'name', 'cycle_type', 'period', 'status', 'start_date', 'end_date',
            'self_assessment_deadline', 'manager_review_deadline',
            'peer_review_deadline', 'calibration_deadline', 'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cycle_type': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'self_assessment_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'manager_review_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'peer_review_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'calibration_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['period'].queryset = GoalPeriod.all_objects.filter(tenant=tenant)
            self.fields['period'].required = False


class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['cycle', 'employee', 'reviewer']
        widgets = {
            'cycle': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'reviewer': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['cycle'].queryset = ReviewCycle.all_objects.filter(tenant=tenant)
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['reviewer'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['reviewer'].required = False


class SelfAssessmentForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['self_rating', 'self_comments', 'strengths', 'areas_of_improvement']
        widgets = {
            'self_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'step': '0.1'}),
            'self_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'areas_of_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ManagerReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['manager_rating', 'manager_comments']
        widgets = {
            'manager_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'step': '0.1'}),
            'manager_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class PeerReviewerForm(forms.ModelForm):
    class Meta:
        model = PeerReviewer
        fields = ['reviewer']
        widgets = {
            'reviewer': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['reviewer'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class PeerFeedbackForm(forms.ModelForm):
    class Meta:
        model = PeerFeedback
        fields = ['rating', 'strengths', 'areas_of_improvement', 'comments']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'step': '0.1'}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'areas_of_improvement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CalibrationForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['final_rating', 'final_comments']
        widgets = {
            'final_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'step': '0.1'}),
            'final_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


# ===========================================================================
# Continuous Feedback Forms
# ===========================================================================

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['to_employee', 'feedback_type', 'visibility', 'subject', 'message', 'is_anonymous']
        widgets = {
            'to_employee': forms.Select(attrs={'class': 'form-select'}),
            'feedback_type': forms.Select(attrs={'class': 'form-select'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['to_employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class MeetingForm(forms.ModelForm):
    class Meta:
        model = OneOnOneMeeting
        fields = [
            'manager', 'employee', 'title', 'scheduled_date', 'scheduled_time',
            'duration_minutes', 'location', 'status', 'notes', 'manager_notes', 'employee_notes',
        ]
        widgets = {
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'employee_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['manager'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class MeetingActionItemForm(forms.ModelForm):
    class Meta:
        model = MeetingActionItem
        fields = ['description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['assigned_to'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['assigned_to'].required = False


# ===========================================================================
# Performance Improvement Forms
# ===========================================================================

class PIPForm(forms.ModelForm):
    class Meta:
        model = PIP
        fields = [
            'employee', 'initiated_by', 'title', 'reason', 'goals',
            'support_provided', 'start_date', 'end_date', 'status', 'outcome_notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'initiated_by': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'support_provided': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'outcome_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['initiated_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['initiated_by'].required = False


class PIPCheckpointForm(forms.ModelForm):
    class Meta:
        model = PIPCheckpoint
        fields = ['title', 'description', 'due_date', 'review_date', 'status', 'manager_notes', 'employee_notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'manager_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'employee_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class WarningLetterForm(forms.ModelForm):
    class Meta:
        model = WarningLetter
        fields = [
            'employee', 'issued_by', 'warning_type', 'subject', 'description',
            'issue_date', 'status', 'acknowledged_date', 'employee_response',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'issued_by': forms.Select(attrs={'class': 'form-select'}),
            'warning_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'acknowledged_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employee_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)
            self.fields['issued_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['issued_by'].required = False


class CoachingNoteForm(forms.ModelForm):
    class Meta:
        model = CoachingNote
        fields = ['employee', 'coach', 'session_date', 'topic', 'notes', 'action_items', 'follow_up_date']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'coach': forms.Select(attrs={'class': 'form-select'}),
            'session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'action_items': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['coach'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['coach'].required = False
