from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.utils import timezone


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.tenant:
            return redirect('accounts:login')

        from apps.employees.models import Employee
        from apps.organization.models import Department
        from apps.onboarding.models import OnboardingProcess
        from apps.offboarding.models import Resignation
        from apps.attendance.models import (
            Attendance, LeaveApplication, AttendanceRegularization,
            OvertimeRequest
        )
        from apps.recruitment.models import (
            JobRequisition, JobApplication, Interview, OfferLetter
        )
        from apps.payroll.models import (
            PayrollPeriod, PayrollEntry, Reimbursement, SalaryHold
        )

        today = timezone.now().date()
        tenant = request.tenant

        # ── Core HR ──────────────────────────────────────────────────
        total_employees = Employee.all_objects.filter(
            tenant=tenant, status='active'
        ).count()
        new_this_month = Employee.all_objects.filter(
            tenant=tenant,
            date_of_joining__year=today.year,
            date_of_joining__month=today.month
        ).count()
        on_leave = Employee.all_objects.filter(
            tenant=tenant, status='on_leave'
        ).count()

        departments = Department.all_objects.filter(
            tenant=tenant, is_active=True
        ).annotate(
            emp_count=Count('employees', filter=Q(employees__status='active'))
        ).values('name', 'emp_count').order_by('-emp_count')[:10]

        active_onboarding = OnboardingProcess.all_objects.filter(
            tenant=tenant,
            status__in=['pending', 'in_progress']
        ).count()

        pending_resignations = Resignation.all_objects.filter(
            tenant=tenant,
            status__in=['submitted', 'under_review']
        ).count()

        recent_employees = Employee.all_objects.filter(
            tenant=tenant
        ).select_related('department', 'designation').order_by('-created_at')[:5]

        upcoming_birthdays = Employee.all_objects.filter(
            tenant=tenant,
            status='active',
            date_of_birth__isnull=False
        ).order_by('date_of_birth__month', 'date_of_birth__day')[:5]

        dept_labels = [d['name'] for d in departments]
        dept_data = [d['emp_count'] for d in departments]

        # ── Attendance & Leave ───────────────────────────────────────
        today_present = Attendance.all_objects.filter(
            tenant=tenant, date=today, status='present'
        ).count()
        today_absent = Attendance.all_objects.filter(
            tenant=tenant, date=today, status='absent'
        ).count()
        pending_leaves = LeaveApplication.all_objects.filter(
            tenant=tenant, status='pending'
        ).count()
        pending_regularizations = AttendanceRegularization.all_objects.filter(
            tenant=tenant, status='pending'
        ).count()
        pending_overtime = OvertimeRequest.all_objects.filter(
            tenant=tenant, status='pending'
        ).count()
        recent_leaves = LeaveApplication.all_objects.filter(
            tenant=tenant
        ).select_related('employee', 'leave_type').order_by('-created_at')[:5]

        # ── Recruitment ──────────────────────────────────────────────
        open_positions = JobRequisition.all_objects.filter(
            tenant=tenant, status__in=['approved', 'published']
        ).aggregate(total=Sum('positions'))['total'] or 0
        active_applications = JobApplication.all_objects.filter(
            tenant=tenant,
            status__in=['applied', 'screening', 'shortlisted', 'interview']
        ).count()
        upcoming_interviews = Interview.all_objects.filter(
            tenant=tenant,
            status='scheduled',
            scheduled_date__gte=today
        ).count()
        pending_offers = OfferLetter.all_objects.filter(
            tenant=tenant,
            status__in=['draft', 'pending_approval', 'sent']
        ).count()
        recent_applications = JobApplication.all_objects.filter(
            tenant=tenant
        ).select_related(
            'candidate', 'job'
        ).order_by('-created_at')[:5]

        # ── Payroll ──────────────────────────────────────────────────
        latest_period = PayrollPeriod.all_objects.filter(
            tenant=tenant
        ).order_by('-year', '-month').first()

        last_payroll_net = 0
        last_payroll_employees = 0
        last_payroll_label = ''
        if latest_period:
            last_payroll_net = latest_period.total_net or 0
            last_payroll_employees = latest_period.employee_count or 0
            last_payroll_label = str(latest_period)

        pending_reimbursements = Reimbursement.all_objects.filter(
            tenant=tenant, status__in=['submitted', 'pending']
        ).count()
        active_holds = SalaryHold.all_objects.filter(
            tenant=tenant, status='active'
        ).count()

        # Payroll period status distribution for chart
        payroll_periods = PayrollPeriod.all_objects.filter(
            tenant=tenant
        ).order_by('-year', '-month')[:6]

        context = {
            # Core HR
            'total_employees': total_employees,
            'new_this_month': new_this_month,
            'on_leave': on_leave,
            'active_onboarding': active_onboarding,
            'pending_resignations': pending_resignations,
            'recent_employees': recent_employees,
            'upcoming_birthdays': upcoming_birthdays,
            'dept_labels': dept_labels,
            'dept_data': dept_data,
            # Attendance & Leave
            'today_present': today_present,
            'today_absent': today_absent,
            'pending_leaves': pending_leaves,
            'pending_regularizations': pending_regularizations,
            'pending_overtime': pending_overtime,
            'recent_leaves': recent_leaves,
            # Recruitment
            'open_positions': open_positions,
            'active_applications': active_applications,
            'upcoming_interviews': upcoming_interviews,
            'pending_offers': pending_offers,
            'recent_applications': recent_applications,
            # Payroll
            'last_payroll_net': last_payroll_net,
            'last_payroll_employees': last_payroll_employees,
            'last_payroll_label': last_payroll_label,
            'pending_reimbursements': pending_reimbursements,
            'active_holds': active_holds,
            'payroll_periods': payroll_periods,
        }
        return render(request, 'dashboard/index.html', context)
