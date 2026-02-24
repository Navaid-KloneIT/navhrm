from django import forms
from .models import (
    Shift, ShiftAssignment,
    Attendance, AttendanceRegularization,
    LeaveType, LeavePolicy, LeaveBalance, LeaveApplication,
    Project, Task, Timesheet, TimeEntry,
    OvertimeRequest,
    Holiday, FloatingHoliday, HolidayPolicy,
)
from apps.employees.models import Employee
from apps.organization.models import Location, Department


# ==========================================================================
# SHIFT MANAGEMENT
# ==========================================================================

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        exclude = ['tenant']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'grace_period_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'half_day_threshold_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'full_day_threshold_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_night_shift': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ShiftAssignmentForm(forms.ModelForm):
    class Meta:
        model = ShiftAssignment
        fields = ['employee', 'shift', 'effective_from', 'effective_to', 'is_active']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'effective_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)
            self.fields['shift'].queryset = Shift.all_objects.filter(tenant=tenant)


# ==========================================================================
# ATTENDANCE MANAGEMENT
# ==========================================================================

class AttendanceRegularizationForm(forms.ModelForm):
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


class RegularizationReviewForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    review_comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


# ==========================================================================
# LEAVE MANAGEMENT
# ==========================================================================

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        exclude = ['tenant']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_days_per_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_consecutive_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_document': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'document_after_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color_code': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class LeavePolicyForm(forms.ModelForm):
    class Meta:
        model = LeavePolicy
        exclude = ['tenant']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'accrual_frequency': forms.Select(attrs={'class': 'form-select'}),
            'accrual_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'allow_carry_forward': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_carry_forward_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'carry_forward_expiry_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'allow_encashment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_encashment_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'applicable_from_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'applicable_employment_types': forms.TextInput(attrs={'class': 'form-control'}),
            'prorate_for_joining': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['leave_type'].queryset = LeaveType.all_objects.filter(tenant=tenant)


class LeaveBalanceAdjustmentForm(forms.ModelForm):
    class Meta:
        model = LeaveBalance
        fields = ['employee', 'leave_type', 'year', 'allocated', 'adjustment']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'allocated': forms.NumberInput(attrs={'class': 'form-control'}),
            'adjustment': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['employee'].queryset = Employee.all_objects.filter(tenant=tenant)
            self.fields['leave_type'].queryset = LeaveType.all_objects.filter(tenant=tenant)


class LeaveApplicationForm(forms.ModelForm):
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
        return cleaned_data


class LeaveApprovalForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


# ==========================================================================
# TIME TRACKING
# ==========================================================================

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'code', 'description', 'client_name', 'manager',
                  'start_date', 'end_date', 'budget_hours', 'hourly_rate',
                  'status', 'is_billable']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'budget_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_billable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['manager'].queryset = Employee.all_objects.filter(tenant=tenant)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'name', 'description', 'assigned_to',
                  'estimated_hours', 'status', 'due_date']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['project'].queryset = Project.all_objects.filter(tenant=tenant)
            self.fields['assigned_to'].queryset = Employee.all_objects.filter(tenant=tenant)


class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['week_start_date', 'notes']
        widgets = {
            'week_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['project', 'task', 'date', 'hours', 'description', 'is_billable']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'task': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_billable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['project'].queryset = Project.all_objects.filter(tenant=tenant)
            self.fields['task'].queryset = Task.all_objects.filter(tenant=tenant)


class TimesheetApprovalForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


class OvertimeRequestForm(forms.ModelForm):
    class Meta:
        model = OvertimeRequest
        fields = ['date', 'ot_type', 'planned_hours', 'reason', 'project',
                  'generate_comp_off']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ot_type': forms.Select(attrs={'class': 'form-select'}),
            'planned_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'generate_comp_off': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['project'].queryset = Project.all_objects.filter(tenant=tenant)


class OvertimeApprovalForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approved'), ('rejected', 'Rejected')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    actual_hours = forms.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )


# ==========================================================================
# HOLIDAY MANAGEMENT
# ==========================================================================

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'holiday_type', 'description', 'location',
                  'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'holiday_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['location'].queryset = Location.all_objects.filter(tenant=tenant)


class FloatingHolidayForm(forms.ModelForm):
    class Meta:
        model = FloatingHoliday
        fields = ['holiday', 'selected_date', 'notes']
        widgets = {
            'holiday': forms.Select(attrs={'class': 'form-select'}),
            'selected_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['holiday'].queryset = Holiday.all_objects.filter(
                tenant=tenant, holiday_type='restricted')


class HolidayPolicyForm(forms.ModelForm):
    class Meta:
        model = HolidayPolicy
        fields = ['name', 'description', 'location', 'department',
                  'applicable_employment_types', 'max_floating_holidays',
                  'year', 'holidays', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'applicable_employment_types': forms.TextInput(attrs={'class': 'form-control'}),
            'max_floating_holidays': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'holidays': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['location'].queryset = Location.all_objects.filter(tenant=tenant)
            self.fields['department'].queryset = Department.all_objects.filter(tenant=tenant)
            self.fields['holidays'].queryset = Holiday.all_objects.filter(tenant=tenant)
