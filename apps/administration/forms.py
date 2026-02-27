from django import forms
from apps.accounts.models import User
from .models import (
    Role, ApprovalWorkflow, ApprovalStep, EmailTemplate,
    NotificationSetting, EscalationRule, SystemSetting,
    FinancialYear, FinancialPeriod, WorkingHoursPolicy,
    IntegrationSetting, DataRetentionPolicy, BackupConfiguration,
)


# =============================================================================
# 9.1 User Management Forms
# =============================================================================

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserRoleAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['user'].queryset = User.objects.filter(tenant=tenant, is_active=True)
            self.fields['role'].queryset = Role.all_objects.filter(tenant=tenant, is_active=True)


# =============================================================================
# 9.2 Workflow Configuration Forms
# =============================================================================

class ApprovalWorkflowForm(forms.ModelForm):
    class Meta:
        model = ApprovalWorkflow
        fields = ['name', 'module', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'module': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ApprovalStepForm(forms.ModelForm):
    class Meta:
        model = ApprovalStep
        fields = ['step_order', 'name', 'approver_type', 'specific_user', 'specific_role', 'can_skip', 'auto_approve_days']
        widgets = {
            'step_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'approver_type': forms.Select(attrs={'class': 'form-select'}),
            'specific_user': forms.Select(attrs={'class': 'form-select'}),
            'specific_role': forms.Select(attrs={'class': 'form-select'}),
            'auto_approve_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['specific_user'].queryset = User.objects.filter(tenant=tenant, is_active=True)
            self.fields['specific_role'].queryset = Role.all_objects.filter(tenant=tenant, is_active=True)
        self.fields['specific_user'].required = False
        self.fields['specific_role'].required = False


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'event', 'subject', 'body', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }


class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ['event', 'channel', 'recipients', 'is_enabled']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'channel': forms.Select(attrs={'class': 'form-select'}),
            'recipients': forms.Select(attrs={'class': 'form-select'}),
        }


class EscalationRuleForm(forms.ModelForm):
    class Meta:
        model = EscalationRule
        fields = ['workflow', 'trigger_after_days', 'action', 'notify_user', 'max_reminders', 'is_active']
        widgets = {
            'workflow': forms.Select(attrs={'class': 'form-select'}),
            'trigger_after_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'action': forms.Select(attrs={'class': 'form-select'}),
            'notify_user': forms.Select(attrs={'class': 'form-select'}),
            'max_reminders': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['workflow'].queryset = ApprovalWorkflow.all_objects.filter(tenant=tenant, is_active=True)
            self.fields['notify_user'].queryset = User.objects.filter(tenant=tenant, is_active=True)
        self.fields['notify_user'].required = False


# =============================================================================
# 9.3 System Configuration Forms
# =============================================================================

class CompanySettingsForm(forms.Form):
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    company_logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    timezone = forms.ChoiceField(
        choices=[
            ('UTC', 'UTC'),
            ('Asia/Kolkata', 'Asia/Kolkata (IST)'),
            ('America/New_York', 'America/New York (EST)'),
            ('America/Chicago', 'America/Chicago (CST)'),
            ('America/Los_Angeles', 'America/Los Angeles (PST)'),
            ('Europe/London', 'Europe/London (GMT)'),
            ('Europe/Berlin', 'Europe/Berlin (CET)'),
            ('Asia/Dubai', 'Asia/Dubai (GST)'),
            ('Asia/Singapore', 'Asia/Singapore (SGT)'),
            ('Australia/Sydney', 'Australia/Sydney (AEST)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_format = forms.ChoiceField(
        choices=[
            ('DD/MM/YYYY', 'DD/MM/YYYY'),
            ('MM/DD/YYYY', 'MM/DD/YYYY'),
            ('YYYY-MM-DD', 'YYYY-MM-DD'),
            ('DD-MM-YYYY', 'DD-MM-YYYY'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    currency = forms.ChoiceField(
        choices=[
            ('INR', 'INR - Indian Rupee'),
            ('USD', 'USD - US Dollar'),
            ('EUR', 'EUR - Euro'),
            ('GBP', 'GBP - British Pound'),
            ('AED', 'AED - UAE Dirham'),
            ('SGD', 'SGD - Singapore Dollar'),
            ('AUD', 'AUD - Australian Dollar'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fiscal_year_start = forms.ChoiceField(
        choices=[
            ('1', 'January'), ('2', 'February'), ('3', 'March'),
            ('4', 'April'), ('5', 'May'), ('6', 'June'),
            ('7', 'July'), ('8', 'August'), ('9', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class FinancialYearForm(forms.ModelForm):
    class Meta:
        model = FinancialYear
        fields = ['name', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class FinancialPeriodForm(forms.ModelForm):
    class Meta:
        model = FinancialPeriod
        fields = ['name', 'period_number', 'start_date', 'end_date', 'is_locked']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class WorkingHoursPolicyForm(forms.ModelForm):
    class Meta:
        model = WorkingHoursPolicy
        fields = [
            'name', 'work_start_time', 'work_end_time', 'break_duration',
            'total_hours', 'grace_late_minutes', 'grace_early_minutes',
            'overtime_threshold', 'working_days', 'is_default', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'work_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'work_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'break_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': 0}),
            'grace_late_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'grace_early_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'overtime_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': 0}),
        }

    WORKING_DAYS_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]

    working_days = forms.MultipleChoiceField(
        choices=WORKING_DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )

    def clean_working_days(self):
        return [int(d) for d in self.cleaned_data.get('working_days', [])]


class IntegrationSettingForm(forms.ModelForm):
    class Meta:
        model = IntegrationSetting
        fields = ['name', 'provider', 'api_key', 'api_secret', 'base_url', 'config_json', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'provider': forms.Select(attrs={'class': 'form-select'}),
            'api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'api_secret': forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
            'base_url': forms.URLInput(attrs={'class': 'form-control'}),
            'config_json': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


# =============================================================================
# 9.4 Audit & Compliance Forms
# =============================================================================

class DataRetentionPolicyForm(forms.ModelForm):
    class Meta:
        model = DataRetentionPolicy
        fields = ['data_type', 'retention_days', 'action', 'is_active', 'description']
        widgets = {
            'data_type': forms.Select(attrs={'class': 'form-select'}),
            'retention_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'action': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BackupConfigurationForm(forms.ModelForm):
    class Meta:
        model = BackupConfiguration
        fields = ['backup_type', 'frequency', 'retention_count', 'include_media', 'is_active']
        widgets = {
            'backup_type': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'retention_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
