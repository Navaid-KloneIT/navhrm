from django import forms
from apps.employees.models import Employee, EmergencyContact
from apps.attendance.models import LeaveApplication, LeaveType, AttendanceRegularization, Attendance
from .models import (
    FamilyMember, DocumentRequest, IDCardRequest, AssetRequest,
    Announcement, BirthdayWish, Survey, SurveyQuestion,
    Suggestion, HelpDeskTicket, TicketComment,
)


# ===========================================================================
# 7.1 Personal Information — Profile Forms (subset of Employee fields)
# ===========================================================================

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender',
                  'marital_status', 'blood_group', 'nationality', 'personal_email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['phone', 'personal_email', 'address_line1', 'address_line2',
                  'city', 'state', 'country', 'zip_code']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BankDetailsForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['bank_name', 'bank_account', 'ifsc_code']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ===========================================================================
# 7.1 Emergency Contacts & Family
# ===========================================================================

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone', 'email', 'address', 'is_primary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['name', 'relationship', 'date_of_birth', 'gender', 'occupation',
                  'phone', 'is_dependent', 'is_nominee', 'nominee_percentage',
                  'covered_under_insurance', 'insurance_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_dependent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_nominee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nominee_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01'}),
            'covered_under_insurance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'insurance_id': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ===========================================================================
# 7.2 Request Management — Leave & Regularization
# ===========================================================================

class EssLeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'from_date', 'to_date', 'from_day_type',
                  'to_day_type', 'reason', 'document']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'from_day_type': forms.Select(attrs={'class': 'form-select'}),
            'to_day_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['leave_type'].queryset = LeaveType.all_objects.filter(tenant=tenant)

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        if from_date and to_date and to_date < from_date:
            raise forms.ValidationError('End date must be on or after the start date.')


class EssRegularizationForm(forms.ModelForm):
    class Meta:
        model = AttendanceRegularization
        fields = ['date', 'requested_check_in', 'requested_check_out',
                  'requested_status', 'reason', 'reason_detail']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'requested_check_in': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'requested_check_out': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'requested_status': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'reason_detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ===========================================================================
# 7.2 Request Management — Document, ID Card, Asset
# ===========================================================================

class DocumentRequestForm(forms.ModelForm):
    class Meta:
        model = DocumentRequest
        fields = ['document_type', 'purpose', 'additional_notes',
                  'copies_needed', 'delivery_method']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'additional_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'copies_needed': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'delivery_method': forms.Select(attrs={'class': 'form-select'}),
        }


class IDCardRequestForm(forms.ModelForm):
    class Meta:
        model = IDCardRequest
        fields = ['request_type', 'reason', 'photo']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AssetRequestForm(forms.ModelForm):
    class Meta:
        model = AssetRequest
        fields = ['asset_type', 'asset_name', 'quantity', 'reason',
                  'priority', 'expected_date', 'notes']
        widgets = {
            'asset_type': forms.Select(attrs={'class': 'form-select'}),
            'asset_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'expected_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ===========================================================================
# 7.3 Communication Hub
# ===========================================================================

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'category', 'priority', 'publish_date',
                  'expiry_date', 'is_pinned', 'target_departments', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'publish_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_departments': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            from apps.organization.models import Department
            self.fields['target_departments'].queryset = Department.objects.filter(tenant=tenant)
        self.fields['target_departments'].required = False
        self.fields['expiry_date'].required = False
        self.fields['target_departments'].help_text = 'Leave empty for company-wide. Hold Ctrl to select multiple.'


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'start_date', 'end_date',
                  'is_anonymous', 'target_departments']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_departments': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            from apps.organization.models import Department
            self.fields['target_departments'].queryset = Department.objects.filter(tenant=tenant)
        self.fields['target_departments'].required = False
        self.fields['target_departments'].help_text = 'Leave empty for all departments. Hold Ctrl to select multiple.'

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date must be on or after the start date.')


class SurveyQuestionForm(forms.ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = ['question_text', 'question_type', 'choices', 'is_required', 'order']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'choices': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option1|Option2|Option3'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class BirthdayWishForm(forms.ModelForm):
    class Meta:
        model = BirthdayWish
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                             'placeholder': 'Write your wish...'}),
        }


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['title', 'category', 'description', 'is_anonymous', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = HelpDeskTicket
        fields = ['subject', 'category', 'description', 'priority', 'attachment']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                             'placeholder': 'Write your reply...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
