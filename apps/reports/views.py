import json
from datetime import date, timedelta
from collections import defaultdict

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Avg, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView

from apps.employees.models import Employee, EmployeeLifecycleEvent
from apps.organization.models import Department, CostCenter
from apps.attendance.models import (
    Attendance, LeaveApplication, LeaveBalance, LeaveType,
    OvertimeRequest, Timesheet, TimeEntry,
)
from apps.payroll.models import (
    PayrollPeriod, PayrollEntry, PayrollEntryComponent,
    StatutoryContribution, TaxComputation, InvestmentDeclaration,
    EmployeeSalaryStructure,
)
from apps.recruitment.models import (
    JobRequisition, JobApplication, Candidate, OfferLetter,
)

from .forms import (
    DateRangeFilterForm, MonthYearFilterForm,
    DepartmentFilterForm, ReportFilterForm,
)
from .utils import (
    get_headcount, get_attrition_rate, get_monthly_headcount_trend,
    get_monthly_exits, get_department_breakdown, get_age_groups,
    get_tenure_groups, safe_division,
)


# ==========================================================================
# Reports Dashboard
# ==========================================================================

class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()

        ctx['total_employees'] = Employee.all_objects.filter(
            tenant=tenant, status='active'
        ).count()
        ctx['attrition_rate'] = get_attrition_rate(
            tenant,
            today - relativedelta(months=12),
            today,
        )
        ctx['open_positions'] = JobRequisition.all_objects.filter(
            tenant=tenant, status__in=['approved', 'published']
        ).aggregate(total=Sum('positions'))['total'] or 0
        ctx['pending_leaves'] = LeaveApplication.all_objects.filter(
            tenant=tenant, status='pending'
        ).count()
        return ctx


# ==========================================================================
# HR Reports
# ==========================================================================

class HeadcountReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/hr_headcount.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        employees = Employee.all_objects.filter(tenant=tenant, status='active')
        dept = self.request.GET.get('department')
        if dept:
            employees = employees.filter(department_id=dept)

        ctx['total_active'] = employees.count()
        ctx['new_this_month'] = employees.filter(
            date_of_joining__year=today.year,
            date_of_joining__month=today.month,
        ).count()
        ctx['exits_this_month'] = Employee.all_objects.filter(
            tenant=tenant,
            status__in=['resigned', 'terminated'],
            date_of_leaving__year=today.year,
            date_of_leaving__month=today.month,
        ).count()

        # By status
        status_data = Employee.all_objects.filter(tenant=tenant).values(
            'status'
        ).annotate(count=Count('id')).order_by('status')
        ctx['status_labels'] = json.dumps([s['status'].replace('_', ' ').title() for s in status_data])
        ctx['status_data'] = json.dumps([s['count'] for s in status_data])

        # By department
        dept_data = get_department_breakdown(tenant)
        ctx['dept_labels'] = json.dumps([d['name'] for d in dept_data[:10]])
        ctx['dept_data'] = json.dumps([d['emp_count'] for d in dept_data[:10]])

        # By employment type
        type_data = employees.values('employment_type').annotate(
            count=Count('id')
        ).order_by('employment_type')
        ctx['type_labels'] = json.dumps([t['employment_type'].replace('_', ' ').title() for t in type_data])
        ctx['type_data'] = json.dumps([t['count'] for t in type_data])

        # Monthly trend
        trend = get_monthly_headcount_trend(tenant, months=12)
        ctx['trend_labels'] = json.dumps([t['label'] for t in trend])
        ctx['trend_data'] = json.dumps([t['count'] for t in trend])

        # Table: department breakdown
        ctx['dept_table'] = dept_data
        return ctx


class AttritionReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/hr_attrition.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        start = today - relativedelta(months=12)

        exits = Employee.all_objects.filter(
            tenant=tenant,
            status__in=['resigned', 'terminated'],
            date_of_leaving__gte=start,
            date_of_leaving__lte=today,
        )
        dept = self.request.GET.get('department')
        if dept:
            exits = exits.filter(department_id=dept)

        ctx['total_exits'] = exits.count()
        ctx['attrition_rate'] = get_attrition_rate(tenant, start, today)
        ctx['resignations'] = exits.filter(status='resigned').count()
        ctx['terminations'] = exits.filter(status='terminated').count()

        # Monthly exit trend
        exit_trend = get_monthly_exits(tenant, months=12)
        ctx['trend_labels'] = json.dumps([e['label'] for e in exit_trend])
        ctx['trend_data'] = json.dumps([e['count'] for e in exit_trend])

        # By department
        dept_exits = exits.values('department__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        ctx['dept_labels'] = json.dumps([d['department__name'] or 'Unassigned' for d in dept_exits])
        ctx['dept_data'] = json.dumps([d['count'] for d in dept_exits])

        # By reason (lifecycle events)
        reason_data = EmployeeLifecycleEvent.all_objects.filter(
            tenant=tenant,
            event_type__in=['resigned', 'terminated'],
            event_date__gte=start,
        ).values('event_type').annotate(count=Count('id'))
        ctx['reason_labels'] = json.dumps([r['event_type'].replace('_', ' ').title() for r in reason_data])
        ctx['reason_data'] = json.dumps([r['count'] for r in reason_data])

        # Table: recent exits
        ctx['recent_exits'] = exits.select_related(
            'department', 'designation'
        ).order_by('-date_of_leaving')[:20]
        return ctx


class DiversityReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/hr_diversity.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        employees = Employee.all_objects.filter(tenant=tenant, status='active')
        dept = self.request.GET.get('department')
        if dept:
            employees = employees.filter(department_id=dept)

        ctx['total'] = employees.count()

        # Gender
        gender_data = employees.values('gender').annotate(count=Count('id')).order_by('gender')
        ctx['gender_labels'] = json.dumps([g['gender'].title() if g['gender'] else 'Not Specified' for g in gender_data])
        ctx['gender_data'] = json.dumps([g['count'] for g in gender_data])

        # Age groups
        age_groups = get_age_groups(employees)
        ctx['age_labels'] = json.dumps(list(age_groups.keys()))
        ctx['age_data'] = json.dumps(list(age_groups.values()))

        # Tenure
        tenure_groups = get_tenure_groups(employees)
        ctx['tenure_labels'] = json.dumps(list(tenure_groups.keys()))
        ctx['tenure_data'] = json.dumps(list(tenure_groups.values()))

        # Marital status
        marital_data = employees.exclude(
            marital_status__isnull=True
        ).exclude(marital_status='').values('marital_status').annotate(
            count=Count('id')
        ).order_by('marital_status')
        ctx['marital_labels'] = json.dumps([m['marital_status'].replace('_', ' ').title() for m in marital_data])
        ctx['marital_data'] = json.dumps([m['count'] for m in marital_data])

        return ctx


class CostReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/hr_cost.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        employees = Employee.all_objects.filter(tenant=tenant, status='active')
        dept = self.request.GET.get('department')
        if dept:
            employees = employees.filter(department_id=dept)

        salary_agg = employees.aggregate(
            total=Coalesce(Sum('salary'), 0, output_field=DecimalField()),
            avg=Coalesce(Avg('salary'), 0, output_field=DecimalField()),
        )
        ctx['total_salary'] = salary_agg['total']
        ctx['avg_salary'] = salary_agg['avg']
        ctx['employee_count'] = employees.count()

        # By department
        dept_cost = Department.all_objects.filter(
            tenant=tenant, is_active=True
        ).annotate(
            total_salary=Coalesce(
                Sum('employees__salary', filter=Q(employees__status='active')),
                0, output_field=DecimalField()
            ),
            emp_count=Count('employees', filter=Q(employees__status='active')),
        ).values('name', 'total_salary', 'emp_count').order_by('-total_salary')[:10]
        ctx['dept_labels'] = json.dumps([d['name'] for d in dept_cost])
        ctx['dept_data'] = json.dumps([float(d['total_salary']) for d in dept_cost])
        ctx['dept_table'] = list(dept_cost)

        # Monthly payroll trend
        periods = PayrollPeriod.all_objects.filter(
            tenant=tenant, status='paid'
        ).order_by('-year', '-month')[:12]
        periods = list(reversed(list(periods)))
        ctx['payroll_labels'] = json.dumps([str(p) for p in periods])
        ctx['payroll_data'] = json.dumps([float(p.total_net or 0) for p in periods])

        return ctx


class HiringReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/hr_hiring.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = DateRangeFilterForm(self.request.GET)
        ctx['form'] = form

        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        if not from_date:
            from_date = (today - relativedelta(months=12)).isoformat()
        if not to_date:
            to_date = today.isoformat()

        ctx['open_requisitions'] = JobRequisition.all_objects.filter(
            tenant=tenant, status__in=['approved', 'published']
        ).count()
        ctx['total_positions'] = JobRequisition.all_objects.filter(
            tenant=tenant, status__in=['approved', 'published']
        ).aggregate(total=Sum('positions'))['total'] or 0

        applications = JobApplication.all_objects.filter(
            tenant=tenant,
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
        )
        ctx['total_applications'] = applications.count()
        ctx['hired'] = applications.filter(status='hired').count()

        # Pipeline stages
        pipeline = applications.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        ctx['pipeline_labels'] = json.dumps([p['status'].replace('_', ' ').title() for p in pipeline])
        ctx['pipeline_data'] = json.dumps([p['count'] for p in pipeline])

        # Source effectiveness
        source_data = Candidate.all_objects.filter(
            tenant=tenant,
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
        ).values('source').annotate(count=Count('id')).order_by('-count')
        ctx['source_labels'] = json.dumps([s['source'].replace('_', ' ').title() for s in source_data])
        ctx['source_data'] = json.dumps([s['count'] for s in source_data])

        # Offers
        offers = OfferLetter.all_objects.filter(
            tenant=tenant,
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
        )
        ctx['total_offers'] = offers.count()
        ctx['accepted_offers'] = offers.filter(status='accepted').count()

        return ctx


# ==========================================================================
# Attendance Reports
# ==========================================================================

class AttendanceSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/attendance_summary.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        month = self.request.GET.get('month') or today.month
        year = self.request.GET.get('year') or today.year
        try:
            month, year = int(month), int(year)
        except (ValueError, TypeError):
            month, year = today.month, today.year

        records = Attendance.all_objects.filter(
            tenant=tenant, date__year=year, date__month=month,
        )

        ctx['total_records'] = records.count()
        ctx['present'] = records.filter(status='present').count()
        ctx['absent'] = records.filter(status='absent').count()
        ctx['half_day'] = records.filter(status='half_day').count()
        ctx['on_leave'] = records.filter(status='on_leave').count()

        total = ctx['total_records'] or 1
        ctx['present_pct'] = round(ctx['present'] / total * 100, 1)

        # Daily breakdown for the month
        daily = records.values('date', 'status').annotate(
            count=Count('id')
        ).order_by('date')
        daily_map = defaultdict(lambda: {'present': 0, 'absent': 0, 'half_day': 0, 'on_leave': 0})
        for d in daily:
            daily_map[d['date'].isoformat()][d['status']] = d['count']

        first_day = date(year, month, 1)
        last_day = first_day + relativedelta(months=1) - timedelta(days=1)
        labels = []
        present_data = []
        absent_data = []
        current = first_day
        while current <= min(last_day, today):
            key = current.isoformat()
            labels.append(current.strftime('%d'))
            present_data.append(daily_map[key]['present'])
            absent_data.append(daily_map[key]['absent'])
            current += timedelta(days=1)

        ctx['daily_labels'] = json.dumps(labels)
        ctx['daily_present'] = json.dumps(present_data)
        ctx['daily_absent'] = json.dumps(absent_data)
        ctx['selected_month'] = month
        ctx['selected_year'] = year

        return ctx


class LatenessReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/attendance_lateness.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        month = self.request.GET.get('month') or today.month
        year = self.request.GET.get('year') or today.year
        try:
            month, year = int(month), int(year)
        except (ValueError, TypeError):
            month, year = today.month, today.year

        records = Attendance.all_objects.filter(
            tenant=tenant, date__year=year, date__month=month,
        )

        late_records = records.filter(is_late=True)
        early_dep = records.filter(is_early_departure=True)

        ctx['total_late'] = late_records.count()
        ctx['total_early_dep'] = early_dep.count()
        ctx['avg_late_minutes'] = round(
            (late_records.aggregate(avg=Avg('late_minutes'))['avg'] or 0), 1
        )

        # Top latecomers
        top_late = late_records.values(
            'employee__first_name', 'employee__last_name',
            'employee__department__name', 'employee__employee_id',
        ).annotate(
            late_count=Count('id'),
            avg_minutes=Avg('late_minutes'),
        ).order_by('-late_count')[:10]
        ctx['top_latecomers'] = list(top_late)

        # Lateness by day of week (1=Sun, 2=Mon, ..., 7=Sat for MySQL)
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_data = [0] * 7
        for rec in late_records:
            wd = rec.date.weekday()  # 0=Mon
            day_data[wd] += 1
        ctx['day_labels'] = json.dumps(day_names)
        ctx['day_data'] = json.dumps(day_data)

        ctx['selected_month'] = month
        ctx['selected_year'] = year
        return ctx


class AbsenteeismReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/attendance_absenteeism.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        month = self.request.GET.get('month') or today.month
        year = self.request.GET.get('year') or today.year
        try:
            month, year = int(month), int(year)
        except (ValueError, TypeError):
            month, year = today.month, today.year

        records = Attendance.all_objects.filter(
            tenant=tenant, date__year=year, date__month=month,
        )
        absent = records.filter(status='absent')

        ctx['total_absent'] = absent.count()
        total_records = records.count() or 1
        ctx['absence_rate'] = round(absent.count() / total_records * 100, 1)

        # By department
        dept_absent = absent.values('employee__department__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        ctx['dept_labels'] = json.dumps([d['employee__department__name'] or 'Unassigned' for d in dept_absent])
        ctx['dept_data'] = json.dumps([d['count'] for d in dept_absent])

        # Frequent absentees
        freq_absent = absent.values(
            'employee__first_name', 'employee__last_name',
            'employee__department__name', 'employee__employee_id',
        ).annotate(
            absent_count=Count('id'),
        ).order_by('-absent_count')[:10]
        ctx['frequent_absentees'] = list(freq_absent)

        # Monthly trend (last 6 months)
        trend_labels = []
        trend_data = []
        for i in range(5, -1, -1):
            d = today - relativedelta(months=i)
            count = Attendance.all_objects.filter(
                tenant=tenant, date__year=d.year, date__month=d.month, status='absent'
            ).count()
            trend_labels.append(d.strftime('%b %Y'))
            trend_data.append(count)
        ctx['trend_labels'] = json.dumps(trend_labels)
        ctx['trend_data'] = json.dumps(trend_data)

        ctx['selected_month'] = month
        ctx['selected_year'] = year
        return ctx


class OvertimeReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/attendance_overtime.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        month = self.request.GET.get('month') or today.month
        year = self.request.GET.get('year') or today.year
        try:
            month, year = int(month), int(year)
        except (ValueError, TypeError):
            month, year = today.month, today.year

        records = Attendance.all_objects.filter(
            tenant=tenant, date__year=year, date__month=month,
            overtime_hours__gt=0,
        )

        ot_agg = records.aggregate(
            total_hours=Coalesce(Sum('overtime_hours'), 0, output_field=DecimalField()),
            avg_hours=Coalesce(Avg('overtime_hours'), 0, output_field=DecimalField()),
        )
        ctx['total_ot_hours'] = ot_agg['total_hours']
        ctx['avg_ot_hours'] = round(float(ot_agg['avg_hours']), 1)
        ctx['ot_employees'] = records.values('employee').distinct().count()

        # OT requests
        ot_requests = OvertimeRequest.all_objects.filter(
            tenant=tenant, date__year=year, date__month=month,
        )
        ctx['total_ot_requests'] = ot_requests.count()
        ctx['approved_ot'] = ot_requests.filter(status='approved').count()

        # By department
        dept_ot = records.values('employee__department__name').annotate(
            total=Sum('overtime_hours'),
        ).order_by('-total')[:10]
        ctx['dept_labels'] = json.dumps([d['employee__department__name'] or 'Unassigned' for d in dept_ot])
        ctx['dept_data'] = json.dumps([float(d['total'] or 0) for d in dept_ot])

        # Top OT employees
        top_ot = records.values(
            'employee__first_name', 'employee__last_name',
            'employee__department__name', 'employee__employee_id',
        ).annotate(
            total_hours=Sum('overtime_hours'),
        ).order_by('-total_hours')[:10]
        ctx['top_overtime'] = list(top_ot)

        ctx['selected_month'] = month
        ctx['selected_year'] = year
        return ctx


class UtilizationReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/attendance_utilization.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        month = self.request.GET.get('month') or today.month
        year = self.request.GET.get('year') or today.year
        try:
            month, year = int(month), int(year)
        except (ValueError, TypeError):
            month, year = today.month, today.year

        records = Attendance.all_objects.filter(
            tenant=tenant, date__year=year, date__month=month,
            status='present',
        )

        hours_agg = records.aggregate(
            total=Coalesce(Sum('total_hours'), 0, output_field=DecimalField()),
            avg=Coalesce(Avg('total_hours'), 0, output_field=DecimalField()),
        )
        ctx['total_hours'] = hours_agg['total']
        ctx['avg_hours'] = round(float(hours_agg['avg']), 1)
        ctx['total_present_days'] = records.count()

        # Standard hours (8h per day)
        standard_hours = records.count() * 8
        utilization = safe_division(float(hours_agg['total']), standard_hours, 0) * 100
        ctx['utilization_pct'] = round(utilization, 1)

        # By department
        dept_util = records.values('employee__department__name').annotate(
            total=Sum('total_hours'),
            days=Count('id'),
        ).order_by('-total')[:10]
        ctx['dept_labels'] = json.dumps([d['employee__department__name'] or 'Unassigned' for d in dept_util])
        ctx['dept_hours'] = json.dumps([float(d['total'] or 0) for d in dept_util])
        ctx['dept_utilization'] = json.dumps([
            round(safe_division(float(d['total'] or 0), d['days'] * 8, 0) * 100, 1)
            for d in dept_util
        ])

        # Timesheet data
        timesheets = Timesheet.all_objects.filter(
            tenant=tenant,
            week_start_date__year=year,
            week_start_date__month=month,
            status='approved',
        )
        ctx['approved_timesheets'] = timesheets.count()
        ts_agg = timesheets.aggregate(
            total=Coalesce(Sum('total_hours'), 0, output_field=DecimalField()),
            billable=Coalesce(Sum('billable_hours'), 0, output_field=DecimalField()),
        )
        ctx['timesheet_hours'] = ts_agg['total']
        ctx['billable_hours'] = ts_agg['billable']

        ctx['selected_month'] = month
        ctx['selected_year'] = year
        return ctx


# ==========================================================================
# Leave Reports
# ==========================================================================

class LeaveRegisterView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/leave_register.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        year = self.request.GET.get('year') or today.year
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = today.year

        leave_types = LeaveType.all_objects.filter(tenant=tenant, is_active=True)
        ctx['leave_types'] = leave_types

        # Balances
        balances = LeaveBalance.all_objects.filter(
            tenant=tenant, year=year,
        ).select_related('employee', 'leave_type', 'employee__department')

        dept = self.request.GET.get('department')
        if dept:
            balances = balances.filter(employee__department_id=dept)

        ctx['balances'] = balances.order_by(
            'employee__first_name', 'leave_type__name'
        )[:200]

        # Summary by type
        type_summary = LeaveApplication.all_objects.filter(
            tenant=tenant,
            status='approved',
            from_date__year=year,
        ).values('leave_type__name').annotate(
            total_days=Sum('total_days'),
            count=Count('id'),
        ).order_by('-total_days')
        ctx['type_labels'] = json.dumps([t['leave_type__name'] for t in type_summary])
        ctx['type_data'] = json.dumps([float(t['total_days'] or 0) for t in type_summary])
        ctx['type_summary'] = list(type_summary)

        ctx['total_approved'] = LeaveApplication.all_objects.filter(
            tenant=tenant, status='approved', from_date__year=year,
        ).count()
        ctx['total_days_taken'] = LeaveApplication.all_objects.filter(
            tenant=tenant, status='approved', from_date__year=year,
        ).aggregate(total=Sum('total_days'))['total'] or 0

        ctx['selected_year'] = year
        return ctx


class LeaveLiabilityView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/leave_liability.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        year = self.request.GET.get('year') or today.year
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = today.year

        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        # Get earned/privilege leave balances (paid leaves that can be encashed)
        balances = LeaveBalance.all_objects.filter(
            tenant=tenant,
            year=year,
            leave_type__is_paid=True,
        ).select_related('employee', 'leave_type')

        dept = self.request.GET.get('department')
        if dept:
            balances = balances.filter(employee__department_id=dept)

        total_liability = 0
        dept_liability = defaultdict(float)
        liability_rows = []

        for bal in balances:
            available = float(bal.allocated or 0) + float(bal.carried_forward or 0) - float(bal.used or 0)
            if available <= 0:
                continue
            daily_rate = float(bal.employee.salary or 0) / 30 if bal.employee.salary else 0
            liability = available * daily_rate
            total_liability += liability
            dept_name = bal.employee.department.name if bal.employee.department else 'Unassigned'
            dept_liability[dept_name] += liability
            liability_rows.append({
                'employee': bal.employee,
                'leave_type': bal.leave_type.name,
                'available': available,
                'daily_rate': round(daily_rate, 2),
                'liability': round(liability, 2),
            })

        ctx['total_liability'] = round(total_liability, 2)
        ctx['liability_rows'] = sorted(liability_rows, key=lambda x: -x['liability'])[:50]

        dept_items = sorted(dept_liability.items(), key=lambda x: -x[1])[:10]
        ctx['dept_labels'] = json.dumps([d[0] for d in dept_items])
        ctx['dept_data'] = json.dumps([round(d[1], 2) for d in dept_items])

        ctx['selected_year'] = year
        return ctx


class CompOffReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/leave_compoff.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        year = self.request.GET.get('year') or today.year
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = today.year

        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        comp_off_type = LeaveType.all_objects.filter(
            tenant=tenant, category='comp_off'
        ).first()

        if comp_off_type:
            balances = LeaveBalance.all_objects.filter(
                tenant=tenant,
                leave_type=comp_off_type,
                year=year,
            ).select_related('employee', 'employee__department')

            dept = self.request.GET.get('department')
            if dept:
                balances = balances.filter(employee__department_id=dept)

            total_earned = sum(float(b.allocated or 0) for b in balances)
            total_used = sum(float(b.used or 0) for b in balances)
            total_available = total_earned - total_used

            ctx['total_earned'] = total_earned
            ctx['total_used'] = total_used
            ctx['total_available'] = total_available
            ctx['balances'] = balances.order_by('employee__first_name')[:100]

            # By department
            dept_data = defaultdict(lambda: {'earned': 0, 'used': 0})
            for bal in balances:
                name = bal.employee.department.name if bal.employee.department else 'Unassigned'
                dept_data[name]['earned'] += float(bal.allocated or 0)
                dept_data[name]['used'] += float(bal.used or 0)

            dept_items = sorted(dept_data.items(), key=lambda x: -x[1]['earned'])[:10]
            ctx['dept_labels'] = json.dumps([d[0] for d in dept_items])
            ctx['dept_earned'] = json.dumps([d[1]['earned'] for d in dept_items])
            ctx['dept_used'] = json.dumps([d[1]['used'] for d in dept_items])
        else:
            ctx['total_earned'] = 0
            ctx['total_used'] = 0
            ctx['total_available'] = 0
            ctx['balances'] = []
            ctx['dept_labels'] = json.dumps([])
            ctx['dept_earned'] = json.dumps([])
            ctx['dept_used'] = json.dumps([])

        ctx['selected_year'] = year
        return ctx


class LeaveTrendView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/leave_trend.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        # Monthly trend for last 12 months
        trend_labels = []
        trend_data = []
        for i in range(11, -1, -1):
            d = today - relativedelta(months=i)
            count = LeaveApplication.all_objects.filter(
                tenant=tenant,
                status='approved',
                from_date__year=d.year,
                from_date__month=d.month,
            ).count()
            trend_labels.append(d.strftime('%b %Y'))
            trend_data.append(count)
        ctx['trend_labels'] = json.dumps(trend_labels)
        ctx['trend_data'] = json.dumps(trend_data)

        # By leave type (current year)
        year = today.year
        type_data = LeaveApplication.all_objects.filter(
            tenant=tenant, status='approved', from_date__year=year,
        ).values('leave_type__name').annotate(
            count=Count('id'),
            total_days=Sum('total_days'),
        ).order_by('-total_days')
        ctx['type_labels'] = json.dumps([t['leave_type__name'] for t in type_data])
        ctx['type_data'] = json.dumps([float(t['total_days'] or 0) for t in type_data])

        # Monthly heatmap data (leave count per month per type)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        heatmap = LeaveApplication.all_objects.filter(
            tenant=tenant, status='approved', from_date__year=year,
        ).values('from_date__month').annotate(
            count=Count('id'),
            total_days=Sum('total_days'),
        ).order_by('from_date__month')
        heatmap_dict = {h['from_date__month']: {
            'count': h['count'],
            'days': float(h['total_days'] or 0),
        } for h in heatmap}
        ctx['heatmap'] = [(months[m - 1], heatmap_dict.get(m, {'count': 0, 'days': 0})) for m in range(1, 13)]

        ctx['total_approved_year'] = sum(h.get('count', 0) for h in heatmap_dict.values())
        return ctx


# ==========================================================================
# Payroll Reports
# ==========================================================================

class SalaryRegisterView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/payroll_register.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        month = self.request.GET.get('month') or today.month
        year = self.request.GET.get('year') or today.year
        try:
            month, year = int(month), int(year)
        except (ValueError, TypeError):
            month, year = today.month, today.year

        period = PayrollPeriod.all_objects.filter(
            tenant=tenant, month=month, year=year,
        ).first()

        if period:
            entries = PayrollEntry.all_objects.filter(
                tenant=tenant, payroll_period=period,
            ).select_related('employee', 'employee__department').order_by(
                'employee__first_name'
            )
            agg = entries.aggregate(
                total_gross=Coalesce(Sum('gross_earnings'), 0, output_field=DecimalField()),
                total_deductions=Coalesce(Sum('total_deductions'), 0, output_field=DecimalField()),
                total_net=Coalesce(Sum('net_pay'), 0, output_field=DecimalField()),
            )
            ctx['entries'] = entries
            ctx['total_gross'] = agg['total_gross']
            ctx['total_deductions'] = agg['total_deductions']
            ctx['total_net'] = agg['total_net']
            ctx['employee_count'] = entries.count()
            ctx['period'] = period
        else:
            ctx['entries'] = []
            ctx['total_gross'] = 0
            ctx['total_deductions'] = 0
            ctx['total_net'] = 0
            ctx['employee_count'] = 0
            ctx['period'] = None

        ctx['selected_month'] = month
        ctx['selected_year'] = year
        return ctx


class TaxReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/payroll_tax.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()

        fy_start_year = today.year if today.month >= 4 else today.year - 1
        fy = f'{fy_start_year}-{fy_start_year + 1}'
        ctx['financial_year'] = fy

        # Tax computations
        computations = TaxComputation.all_objects.filter(
            tenant=tenant, financial_year=fy,
        ).select_related('employee', 'employee__department')

        agg = computations.aggregate(
            total_income=Coalesce(Sum('total_income'), 0, output_field=DecimalField()),
            total_tax=Coalesce(Sum('total_tax_liability'), 0, output_field=DecimalField()),
            total_tds=Coalesce(Sum('tds_deducted_ytd'), 0, output_field=DecimalField()),
        )
        ctx['total_income'] = agg['total_income']
        ctx['total_tax'] = agg['total_tax']
        ctx['total_tds'] = agg['total_tds']
        ctx['taxpayer_count'] = computations.count()

        # Regime split
        old_regime = computations.filter(regime='old').count()
        new_regime = computations.filter(regime='new').count()
        ctx['regime_labels'] = json.dumps(['Old Regime', 'New Regime'])
        ctx['regime_data'] = json.dumps([old_regime, new_regime])

        # Declarations by section
        declarations = InvestmentDeclaration.all_objects.filter(
            tenant=tenant, financial_year=fy,
        ).values('section').annotate(
            total=Sum('declared_amount'),
            count=Count('id'),
        ).order_by('-total')
        ctx['section_labels'] = json.dumps([d['section'].upper() for d in declarations])
        ctx['section_data'] = json.dumps([float(d['total'] or 0) for d in declarations])

        ctx['computations'] = computations.order_by('employee__first_name')[:50]
        return ctx


class StatutoryReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/payroll_statutory.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = MonthYearFilterForm(self.request.GET)
        ctx['form'] = form

        month = self.request.GET.get('month') or today.month
        year = self.request.GET.get('year') or today.year
        try:
            month, year = int(month), int(year)
        except (ValueError, TypeError):
            month, year = today.month, today.year

        period = PayrollPeriod.all_objects.filter(
            tenant=tenant, month=month, year=year,
        ).first()

        contributions = StatutoryContribution.all_objects.filter(
            tenant=tenant, payroll_period=period,
        ) if period else StatutoryContribution.objects.none()

        type_summary = contributions.values('contribution_type').annotate(
            total=Sum('amount'),
            count=Count('id'),
        ).order_by('contribution_type')

        ctx['type_summary'] = list(type_summary)

        # Group into PF, ESI, PT, LWF
        pf_total = contributions.filter(
            contribution_type__in=['pf_employee', 'pf_employer', 'eps']
        ).aggregate(total=Sum('amount'))['total'] or 0
        esi_total = contributions.filter(
            contribution_type__in=['esi_employee', 'esi_employer']
        ).aggregate(total=Sum('amount'))['total'] or 0
        pt_total = contributions.filter(
            contribution_type='pt'
        ).aggregate(total=Sum('amount'))['total'] or 0
        lwf_total = contributions.filter(
            contribution_type__in=['lwf_employee', 'lwf_employer']
        ).aggregate(total=Sum('amount'))['total'] or 0

        ctx['pf_total'] = pf_total
        ctx['esi_total'] = esi_total
        ctx['pt_total'] = pt_total
        ctx['lwf_total'] = lwf_total
        ctx['grand_total'] = pf_total + esi_total + pt_total + lwf_total

        ctx['chart_labels'] = json.dumps(['PF', 'ESI', 'PT', 'LWF'])
        ctx['chart_data'] = json.dumps([float(pf_total), float(esi_total), float(pt_total), float(lwf_total)])

        # Employee-wise for table
        if period:
            emp_contributions = contributions.values(
                'employee__first_name', 'employee__last_name',
                'employee__employee_id', 'contribution_type',
            ).annotate(total=Sum('amount')).order_by('employee__first_name')
            ctx['emp_contributions'] = list(emp_contributions)
        else:
            ctx['emp_contributions'] = []

        ctx['period'] = period
        ctx['selected_month'] = month
        ctx['selected_year'] = year
        return ctx


class PayrollCostView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/payroll_cost.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()
        form = DepartmentFilterForm(self.request.GET, tenant=tenant)
        ctx['form'] = form

        # Active salary structures
        structures = EmployeeSalaryStructure.all_objects.filter(
            tenant=tenant, status='active',
        ).select_related('employee', 'employee__department')

        dept = self.request.GET.get('department')
        if dept:
            structures = structures.filter(employee__department_id=dept)

        agg = structures.aggregate(
            total_ctc=Coalesce(Sum('ctc'), 0, output_field=DecimalField()),
            total_gross=Coalesce(Sum('gross_salary'), 0, output_field=DecimalField()),
            total_net=Coalesce(Sum('net_salary'), 0, output_field=DecimalField()),
            avg_ctc=Coalesce(Avg('ctc'), 0, output_field=DecimalField()),
        )
        ctx['total_ctc'] = agg['total_ctc']
        ctx['total_gross'] = agg['total_gross']
        ctx['total_net'] = agg['total_net']
        ctx['avg_ctc'] = agg['avg_ctc']
        ctx['employee_count'] = structures.count()

        # By department
        dept_cost = structures.values('employee__department__name').annotate(
            total_ctc=Sum('ctc'),
            count=Count('id'),
        ).order_by('-total_ctc')[:10]
        ctx['dept_labels'] = json.dumps([d['employee__department__name'] or 'Unassigned' for d in dept_cost])
        ctx['dept_data'] = json.dumps([float(d['total_ctc'] or 0) for d in dept_cost])
        ctx['dept_table'] = list(dept_cost)

        # CTC breakdown (gross vs deductions from latest period)
        latest_period = PayrollPeriod.all_objects.filter(
            tenant=tenant
        ).order_by('-year', '-month').first()
        if latest_period:
            period_agg = PayrollEntry.all_objects.filter(
                tenant=tenant, payroll_period=latest_period,
            ).aggregate(
                gross=Coalesce(Sum('gross_earnings'), 0, output_field=DecimalField()),
                deductions=Coalesce(Sum('total_deductions'), 0, output_field=DecimalField()),
            )
            ctx['breakdown_labels'] = json.dumps(['Gross Earnings', 'Total Deductions'])
            ctx['breakdown_data'] = json.dumps([float(period_agg['gross']), float(period_agg['deductions'])])
        else:
            ctx['breakdown_labels'] = json.dumps([])
            ctx['breakdown_data'] = json.dumps([])

        # Cost centers
        cost_centers = CostCenter.all_objects.filter(
            tenant=tenant, is_active=True,
        ).values('name', 'budget', 'spent').order_by('-budget')[:10]
        ctx['cost_centers'] = list(cost_centers)

        return ctx


# ==========================================================================
# Analytics Dashboard
# ==========================================================================

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/analytics_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = date.today()

        # Key metrics
        ctx['total_employees'] = Employee.all_objects.filter(
            tenant=tenant, status='active'
        ).count()
        ctx['attrition_rate'] = get_attrition_rate(
            tenant, today - relativedelta(months=12), today,
        )
        avg_salary = Employee.all_objects.filter(
            tenant=tenant, status='active', salary__gt=0,
        ).aggregate(avg=Avg('salary'))['avg'] or 0
        ctx['avg_salary'] = round(float(avg_salary), 0)

        ctx['open_positions'] = JobRequisition.all_objects.filter(
            tenant=tenant, status__in=['approved', 'published']
        ).aggregate(total=Sum('positions'))['total'] or 0

        # Attendance rate (this month)
        month_records = Attendance.all_objects.filter(
            tenant=tenant, date__year=today.year, date__month=today.month,
        )
        total_records = month_records.count() or 1
        present = month_records.filter(status='present').count()
        ctx['attendance_rate'] = round(present / total_records * 100, 1)

        ctx['pending_leaves'] = LeaveApplication.all_objects.filter(
            tenant=tenant, status='pending'
        ).count()

        # Headcount trend (12 months)
        trend = get_monthly_headcount_trend(tenant, months=12)
        ctx['hc_labels'] = json.dumps([t['label'] for t in trend])
        ctx['hc_data'] = json.dumps([t['count'] for t in trend])

        # Attrition trend (12 months)
        exit_trend = get_monthly_exits(tenant, months=12)
        ctx['attrition_labels'] = json.dumps([e['label'] for e in exit_trend])
        ctx['attrition_data'] = json.dumps([e['count'] for e in exit_trend])

        # Workforce composition
        type_data = Employee.all_objects.filter(
            tenant=tenant, status='active',
        ).values('employment_type').annotate(count=Count('id'))
        ctx['workforce_labels'] = json.dumps([t['employment_type'].replace('_', ' ').title() for t in type_data])
        ctx['workforce_data'] = json.dumps([t['count'] for t in type_data])

        # Department cost
        dept_cost = Department.all_objects.filter(
            tenant=tenant, is_active=True,
        ).annotate(
            total_salary=Coalesce(
                Sum('employees__salary', filter=Q(employees__status='active')),
                0, output_field=DecimalField()
            ),
        ).values('name', 'total_salary').order_by('-total_salary')[:8]
        ctx['dept_labels'] = json.dumps([d['name'] for d in dept_cost])
        ctx['dept_data'] = json.dumps([float(d['total_salary']) for d in dept_cost])

        # Gender split
        gender_data = Employee.all_objects.filter(
            tenant=tenant, status='active',
        ).values('gender').annotate(count=Count('id'))
        ctx['gender_labels'] = json.dumps([g['gender'].title() if g['gender'] else 'N/A' for g in gender_data])
        ctx['gender_data'] = json.dumps([g['count'] for g in gender_data])

        return ctx
