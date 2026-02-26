from django import forms
from datetime import date

from apps.organization.models import Department


MONTH_CHOICES = [
    ('', 'All Months'),
    (1, 'January'), (2, 'February'), (3, 'March'),
    (4, 'April'), (5, 'May'), (6, 'June'),
    (7, 'July'), (8, 'August'), (9, 'September'),
    (10, 'October'), (11, 'November'), (12, 'December'),
]

EMPLOYEE_STATUS_CHOICES = [
    ('', 'All Statuses'),
    ('active', 'Active'),
    ('on_leave', 'On Leave'),
    ('suspended', 'Suspended'),
    ('terminated', 'Terminated'),
    ('resigned', 'Resigned'),
    ('retired', 'Retired'),
]

EMPLOYMENT_TYPE_CHOICES = [
    ('', 'All Types'),
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('intern', 'Intern'),
    ('freelance', 'Freelance'),
]


class DateRangeFilterForm(forms.Form):
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )


class MonthYearFilterForm(forms.Form):
    month = forms.TypedChoiceField(
        choices=MONTH_CHOICES,
        required=False,
        coerce=int,
        empty_value='',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    year = forms.TypedChoiceField(
        choices=[],
        required=False,
        coerce=int,
        empty_value='',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date.today().year
        year_choices = [('', 'All Years')] + [
            (y, str(y)) for y in range(current_year, current_year - 6, -1)
        ]
        self.fields['year'].choices = year_choices


class DepartmentFilterForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['department'].queryset = (
                Department.all_objects.filter(tenant=tenant, is_active=True)
                .order_by('name')
            )


class ReportFilterForm(DateRangeFilterForm, DepartmentFilterForm):
    employee_status = forms.ChoiceField(
        choices=EMPLOYEE_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    employment_type = forms.ChoiceField(
        choices=EMPLOYMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
