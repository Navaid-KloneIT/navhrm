from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.tenant:
            return redirect('accounts:login')

        from apps.employees.models import Employee
        from apps.organization.models import Department
        from apps.onboarding.models import OnboardingProcess
        from apps.offboarding.models import Resignation

        today = timezone.now().date()

        total_employees = Employee.all_objects.filter(
            tenant=request.tenant, status='active'
        ).count()
        new_this_month = Employee.all_objects.filter(
            tenant=request.tenant,
            date_of_joining__year=today.year,
            date_of_joining__month=today.month
        ).count()
        on_leave = Employee.all_objects.filter(
            tenant=request.tenant, status='on_leave'
        ).count()

        departments = Department.all_objects.filter(
            tenant=request.tenant, is_active=True
        ).annotate(
            emp_count=Count('employees', filter=Q(employees__status='active'))
        ).values('name', 'emp_count').order_by('-emp_count')[:10]

        active_onboarding = OnboardingProcess.all_objects.filter(
            tenant=request.tenant,
            status__in=['pending', 'in_progress']
        ).count()

        pending_resignations = Resignation.all_objects.filter(
            tenant=request.tenant,
            status__in=['submitted', 'under_review']
        ).count()

        recent_employees = Employee.all_objects.filter(
            tenant=request.tenant
        ).select_related('department', 'designation').order_by('-created_at')[:5]

        upcoming_birthdays = Employee.all_objects.filter(
            tenant=request.tenant,
            status='active',
            date_of_birth__isnull=False
        ).order_by('date_of_birth__month', 'date_of_birth__day')[:5]

        dept_labels = [d['name'] for d in departments]
        dept_data = [d['emp_count'] for d in departments]

        context = {
            'total_employees': total_employees,
            'new_this_month': new_this_month,
            'on_leave': on_leave,
            'active_onboarding': active_onboarding,
            'pending_resignations': pending_resignations,
            'recent_employees': recent_employees,
            'upcoming_birthdays': upcoming_birthdays,
            'dept_labels': dept_labels,
            'dept_data': dept_data,
        }
        return render(request, 'dashboard/index.html', context)
