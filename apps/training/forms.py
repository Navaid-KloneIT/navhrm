from django import forms
from apps.employees.models import Employee
from apps.organization.models import Department
from .models import (
    TrainingCategory, TrainingVendor, Training, TrainingSession,
    Course, CourseContent, LearningPath, LearningPathCourse, CourseEnrollment,
    Assessment, AssessmentQuestion, Badge, EmployeeBadge,
    TrainingNomination, TrainingAttendance, TrainingFeedback,
    TrainingCertificate, TrainingBudget,
)


# ===========================================================================
# Training Management Forms
# ===========================================================================

class TrainingCategoryForm(forms.ModelForm):
    class Meta:
        model = TrainingCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TrainingVendorForm(forms.ModelForm):
    class Meta:
        model = TrainingVendor
        fields = ['name', 'contact_person', 'email', 'phone', 'website', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = [
            'title', 'description', 'category', 'training_type', 'vendor',
            'instructor_name', 'instructor_email', 'duration_hours',
            'max_participants', 'cost_per_person', 'currency',
            'prerequisites', 'objectives', 'status', 'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'training_type': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'instructor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'instructor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.1'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cost_per_person': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'prerequisites': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['category'].queryset = TrainingCategory.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['vendor'].queryset = TrainingVendor.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['category'].required = False
            self.fields['vendor'].required = False


class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = [
            'training', 'title', 'session_date', 'start_time', 'end_time',
            'venue', 'meeting_link', 'instructor', 'max_participants', 'status', 'notes',
        ]
        widgets = {
            'training': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['training'].queryset = Training.all_objects.filter(tenant=tenant)
            self.fields['instructor'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['instructor'].required = False


# ===========================================================================
# Learning Management Forms
# ===========================================================================

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category', 'course_type',
            'difficulty_level', 'duration_hours', 'is_mandatory', 'is_published', 'thumbnail',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'course_type': forms.Select(attrs={'class': 'form-select'}),
            'difficulty_level': forms.Select(attrs={'class': 'form-select'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.1'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['category'].queryset = TrainingCategory.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['category'].required = False


class CourseContentForm(forms.ModelForm):
    class Meta:
        model = CourseContent
        fields = ['title', 'content_type', 'content_url', 'content_file', 'description', 'order', 'duration_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'content_url': forms.URLInput(attrs={'class': 'form-control'}),
            'content_file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class LearningPathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ['title', 'description', 'target_role', 'target_department', 'is_mandatory', 'is_published', 'estimated_hours']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_role': forms.TextInput(attrs={'class': 'form-control'}),
            'target_department': forms.Select(attrs={'class': 'form-select'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.1'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['target_department'].queryset = Department.objects.filter(tenant=tenant)
            self.fields['target_department'].required = False


class LearningPathCourseForm(forms.ModelForm):
    class Meta:
        model = LearningPathCourse
        fields = ['course', 'order', 'is_mandatory']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['course'].queryset = Course.all_objects.filter(tenant=tenant, is_published=True)


class CourseEnrollmentForm(forms.ModelForm):
    class Meta:
        model = CourseEnrollment
        fields = ['course', 'employee', 'status', 'progress', 'score']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['course'].queryset = Course.all_objects.filter(tenant=tenant, is_published=True)
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['course', 'title', 'description', 'assessment_type', 'passing_score', 'time_limit_minutes', 'max_attempts', 'is_published']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assessment_type': forms.Select(attrs={'class': 'form-select'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['course'].queryset = Course.all_objects.filter(tenant=tenant)
            self.fields['course'].required = False


class AssessmentQuestionForm(forms.ModelForm):
    class Meta:
        model = AssessmentQuestion
        fields = ['question_text', 'question_type', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'points', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ['name', 'description', 'icon', 'criteria', 'badge_type', 'points_value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ri-medal-line'}),
            'criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'badge_type': forms.Select(attrs={'class': 'form-select'}),
            'points_value': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


# ===========================================================================
# Training Administration Forms
# ===========================================================================

class TrainingNominationForm(forms.ModelForm):
    class Meta:
        model = TrainingNomination
        fields = ['training', 'employee', 'nominated_by', 'reason', 'status']
        widgets = {
            'training': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'nominated_by': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['training'].queryset = Training.all_objects.filter(tenant=tenant, status='published')
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['nominated_by'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')
            self.fields['nominated_by'].required = False


class TrainingAttendanceForm(forms.ModelForm):
    class Meta:
        model = TrainingAttendance
        fields = ['employee', 'status', 'check_in_time', 'check_out_time', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class TrainingFeedbackForm(forms.ModelForm):
    class Meta:
        model = TrainingFeedback
        fields = [
            'training', 'employee', 'overall_rating', 'content_rating',
            'instructor_rating', 'relevance_rating', 'comments', 'suggestions', 'would_recommend',
        ]
        widgets = {
            'training': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'content_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'instructor_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'relevance_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'suggestions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['training'].queryset = Training.all_objects.filter(tenant=tenant)
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class TrainingCertificateForm(forms.ModelForm):
    class Meta:
        model = TrainingCertificate
        fields = ['training', 'course', 'employee', 'certificate_number', 'issue_date', 'expiry_date', 'status']
        widgets = {
            'training': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'certificate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['training'].queryset = Training.all_objects.filter(tenant=tenant)
            self.fields['training'].required = False
            self.fields['course'].queryset = Course.all_objects.filter(tenant=tenant)
            self.fields['course'].required = False
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant, status='active')


class TrainingBudgetForm(forms.ModelForm):
    class Meta:
        model = TrainingBudget
        fields = ['department', 'fiscal_year', 'allocated_amount', 'utilized_amount', 'currency', 'description', 'status']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'fiscal_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2025-2026'}),
            'allocated_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'utilized_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = Department.objects.filter(tenant=tenant)
            self.fields['department'].required = False
