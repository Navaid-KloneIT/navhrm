from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, TemplateView
from django.utils import timezone
from django.db.models import Q, Sum
import calendar
from datetime import date, datetime, timedelta

from .models import (
    Shift, ShiftAssignment, Attendance, AttendanceRegularization,
    LeaveType, LeavePolicy, LeaveBalance, LeaveApplication,
    Project, Task, Timesheet, TimeEntry, OvertimeRequest,
    Holiday, FloatingHoliday, HolidayPolicy,
)
from .forms import (
    ShiftForm, ShiftAssignmentForm, AttendanceRegularizationForm,
    RegularizationReviewForm, LeaveTypeForm, LeavePolicyForm,
    LeaveBalanceAdjustmentForm, LeaveApplicationForm, LeaveApprovalForm,
    ProjectForm, TaskForm, TimesheetForm, TimeEntryForm,
    TimesheetApprovalForm, OvertimeRequestForm, OvertimeApprovalForm,
    HolidayForm, FloatingHolidayForm, HolidayPolicyForm,
)
from apps.employees.models import Employee


# ==========================================================================
# ATTENDANCE DASHBOARD
# ==========================================================================

class AttendanceDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/attendance_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = timezone.now().date()

        total_employees = Employee.all_objects.filter(
            tenant=tenant, status='active'
        ).count()

        today_attendance = Attendance.all_objects.filter(
            tenant=tenant, date=today
        )
        present_count = today_attendance.filter(status='present').count()
        absent_count = today_attendance.filter(status='absent').count()
        on_leave_count = today_attendance.filter(status='on_leave').count()
        late_count = today_attendance.filter(is_late=True).count()

        pending_regularizations = AttendanceRegularization.all_objects.filter(
            tenant=tenant, status='pending'
        ).count()

        pending_leave_requests = LeaveApplication.all_objects.filter(
            tenant=tenant, status='pending'
        ).count()

        recent_attendance = Attendance.all_objects.filter(
            tenant=tenant
        ).select_related('employee').order_by('-date', '-check_in')[:5]

        context.update({
            'today': today,
            'total_employees': total_employees,
            'present_count': present_count,
            'absent_count': absent_count,
            'on_leave_count': on_leave_count,
            'late_count': late_count,
            'pending_regularizations': pending_regularizations,
            'pending_leave_requests': pending_leave_requests,
            'recent_attendance': recent_attendance,
        })
        return context


# ==========================================================================
# CHECK-IN / CHECK-OUT
# ==========================================================================

class CheckInOutView(LoginRequiredMixin, View):
    template_name = 'attendance/check_in_out.html'

    def get(self, request):
        employee = Employee.all_objects.filter(
            tenant=request.tenant, user=request.user
        ).first()

        if not employee:
            messages.warning(request, 'No employee record is linked to your account.')
            return render(request, self.template_name, {'employee': None})

        today = timezone.now().date()
        attendance = Attendance.all_objects.filter(
            tenant=request.tenant, employee=employee, date=today
        ).first()

        return render(request, self.template_name, {
            'employee': employee,
            'attendance': attendance,
            'today': today,
        })

    def post(self, request):
        employee = Employee.all_objects.filter(
            tenant=request.tenant, user=request.user
        ).first()

        if not employee:
            messages.error(request, 'No employee record is linked to your account.')
            return redirect('attendance:punch')

        today = timezone.now().date()
        now = timezone.now()
        action = request.POST.get('action')

        if action == 'check_in':
            attendance, created = Attendance.all_objects.get_or_create(
                tenant=request.tenant,
                employee=employee,
                date=today,
                defaults={
                    'check_in': now,
                    'status': 'present',
                    'source': 'web',
                },
            )
            if not created and not attendance.check_in:
                attendance.check_in = now
                attendance.status = 'present'
                attendance.save()
            elif not created:
                messages.info(request, 'You have already checked in today.')
                return redirect('attendance:punch')
            messages.success(request, 'Checked in successfully.')

        elif action == 'check_out':
            attendance = Attendance.all_objects.filter(
                tenant=request.tenant, employee=employee, date=today
            ).first()
            if not attendance or not attendance.check_in:
                messages.error(request, 'You must check in before checking out.')
                return redirect('attendance:punch')
            if attendance.check_out:
                messages.info(request, 'You have already checked out today.')
                return redirect('attendance:punch')
            attendance.check_out = now
            attendance.total_hours = attendance.calculate_hours()
            attendance.save()
            messages.success(request, 'Checked out successfully.')

        return redirect('attendance:punch')


# ==========================================================================
# ATTENDANCE RECORDS
# ==========================================================================

class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendance_list'
    paginate_by = 20

    def get_queryset(self):
        qs = Attendance.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'shift')

        employee_id = self.request.GET.get('employee', '')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        date_from = self.request.GET.get('date_from', '')
        if date_from:
            qs = qs.filter(date__gte=date_from)

        date_to = self.request.GET.get('date_to', '')
        if date_to:
            qs = qs.filter(date__lte=date_to)

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.all_objects.filter(
            tenant=self.request.tenant, status='active'
        ).order_by('first_name', 'last_name')
        context['current_employee'] = self.request.GET.get('employee', '')
        context['current_date_from'] = self.request.GET.get('date_from', '')
        context['current_date_to'] = self.request.GET.get('date_to', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = Attendance.STATUS_CHOICES
        return context


# ==========================================================================
# ATTENDANCE CALENDAR
# ==========================================================================

class AttendanceCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/attendance_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = timezone.now().date()

        month = int(self.request.GET.get('month', today.month))
        year = int(self.request.GET.get('year', today.year))
        employee_id = self.request.GET.get('employee_id', '')

        # Build calendar data
        days_in_month = calendar.monthrange(year, month)[1]
        first_day_weekday = calendar.monthrange(year, month)[0]  # 0=Monday

        calendar_data = {}
        status_colors = {
            'present': '#22c55e',
            'absent': '#ef4444',
            'half_day': '#f59e0b',
            'on_leave': '#3b82f6',
            'holiday': '#8b5cf6',
            'weekend': '#6b7280',
            'not_marked': '#d1d5db',
        }

        if employee_id:
            attendance_records = Attendance.all_objects.filter(
                tenant=tenant,
                employee_id=employee_id,
                date__year=year,
                date__month=month,
            )
            for record in attendance_records:
                calendar_data[record.date.day] = {
                    'status': record.status,
                    'color': status_colors.get(record.status, '#d1d5db'),
                }

        employees = Employee.all_objects.filter(
            tenant=tenant, status='active'
        ).order_by('first_name', 'last_name')

        context.update({
            'calendar_data': calendar_data,
            'month': month,
            'year': year,
            'employees': employees,
            'selected_employee': employee_id,
            'month_name': calendar.month_name[month],
            'days_in_month': days_in_month,
            'first_day_weekday': first_day_weekday,
        })
        return context


# ==========================================================================
# REGULARIZATION
# ==========================================================================

class RegularizationListView(LoginRequiredMixin, ListView):
    model = AttendanceRegularization
    template_name = 'attendance/regularization_list.html'
    context_object_name = 'regularizations'
    paginate_by = 20

    def get_queryset(self):
        qs = AttendanceRegularization.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'reviewed_by')

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = AttendanceRegularization.STATUS_CHOICES
        return context


class RegularizationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = AttendanceRegularizationForm(tenant=request.tenant)
        return render(request, 'attendance/regularization_form.html', {
            'form': form,
            'title': 'Request Attendance Regularization',
        })

    def post(self, request):
        form = AttendanceRegularizationForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            regularization = form.save(commit=False)
            employee = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()
            if not employee:
                messages.error(request, 'No employee record is linked to your account.')
                return redirect('attendance:regularization_list')
            regularization.employee = employee
            regularization.tenant = request.tenant
            regularization.save()
            messages.success(request, 'Regularization request submitted successfully.')
            return redirect('attendance:regularization_list')
        return render(request, 'attendance/regularization_form.html', {
            'form': form,
            'title': 'Request Attendance Regularization',
        })


class RegularizationDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        regularization = get_object_or_404(
            AttendanceRegularization.all_objects.select_related(
                'employee', 'attendance', 'reviewed_by'
            ),
            pk=pk,
            tenant=request.tenant,
        )
        review_form = RegularizationReviewForm()
        return render(request, 'attendance/regularization_detail.html', {
            'regularization': regularization,
            'review_form': review_form,
        })


class RegularizationApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        regularization = get_object_or_404(
            AttendanceRegularization.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        form = RegularizationReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action', 'approved')
            reviewer = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()

            regularization.status = action
            regularization.reviewed_by = reviewer
            regularization.reviewed_at = timezone.now()
            regularization.review_comments = form.cleaned_data.get('review_comments', '')
            regularization.save()

            # If approved, update the related attendance record
            if action == 'approved':
                attendance, created = Attendance.all_objects.get_or_create(
                    tenant=request.tenant,
                    employee=regularization.employee,
                    date=regularization.date,
                    defaults={'source': 'regularized'},
                )
                if regularization.requested_check_in:
                    attendance.check_in = regularization.requested_check_in
                if regularization.requested_check_out:
                    attendance.check_out = regularization.requested_check_out
                attendance.status = regularization.requested_status
                attendance.source = 'regularized'
                if attendance.check_in and attendance.check_out:
                    attendance.total_hours = attendance.calculate_hours()
                attendance.save()
                regularization.attendance = attendance
                regularization.save()

            messages.success(
                request,
                f'Regularization request {regularization.get_status_display().lower()}.'
            )
        return redirect('attendance:regularization_detail', pk=pk)


# ==========================================================================
# SHIFTS
# ==========================================================================

class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = 'attendance/shift_list.html'
    context_object_name = 'shifts'
    paginate_by = 20

    def get_queryset(self):
        qs = Shift.all_objects.filter(tenant=self.request.tenant)

        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))

        is_active = self.request.GET.get('is_active', '')
        if is_active == '1':
            qs = qs.filter(is_active=True)
        elif is_active == '0':
            qs = qs.filter(is_active=False)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')
        return context


class ShiftCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ShiftForm(tenant=request.tenant)
        return render(request, 'attendance/shift_form.html', {
            'form': form,
            'title': 'Create Shift',
        })

    def post(self, request):
        form = ShiftForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.tenant = request.tenant
            shift.save()
            messages.success(request, f'Shift "{shift.name}" created successfully.')
            return redirect('attendance:shift_list')
        return render(request, 'attendance/shift_form.html', {
            'form': form,
            'title': 'Create Shift',
        })


class ShiftUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        shift = get_object_or_404(Shift.all_objects, pk=pk, tenant=request.tenant)
        form = ShiftForm(instance=shift, tenant=request.tenant)
        return render(request, 'attendance/shift_form.html', {
            'form': form,
            'shift': shift,
            'title': 'Edit Shift',
        })

    def post(self, request, pk):
        shift = get_object_or_404(Shift.all_objects, pk=pk, tenant=request.tenant)
        form = ShiftForm(request.POST, instance=shift, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Shift "{shift.name}" updated successfully.')
            return redirect('attendance:shift_list')
        return render(request, 'attendance/shift_form.html', {
            'form': form,
            'shift': shift,
            'title': 'Edit Shift',
        })


# ==========================================================================
# SHIFT ASSIGNMENTS
# ==========================================================================

class ShiftAssignmentListView(LoginRequiredMixin, ListView):
    model = ShiftAssignment
    template_name = 'attendance/shift_assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 20

    def get_queryset(self):
        qs = ShiftAssignment.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'shift')

        employee_id = self.request.GET.get('employee', '')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        shift_id = self.request.GET.get('shift', '')
        if shift_id:
            qs = qs.filter(shift_id=shift_id)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.all_objects.filter(
            tenant=self.request.tenant, status='active'
        ).order_by('first_name', 'last_name')
        context['shifts'] = Shift.all_objects.filter(
            tenant=self.request.tenant, is_active=True
        )
        context['current_employee'] = self.request.GET.get('employee', '')
        context['current_shift'] = self.request.GET.get('shift', '')
        return context


class ShiftAssignmentCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ShiftAssignmentForm(tenant=request.tenant)
        return render(request, 'attendance/shift_assignment_form.html', {
            'form': form,
            'title': 'Assign Shift',
        })

    def post(self, request):
        form = ShiftAssignmentForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.tenant = request.tenant
            assignment.save()
            messages.success(request, 'Shift assigned successfully.')
            return redirect('attendance:shift_assignment_list')
        return render(request, 'attendance/shift_assignment_form.html', {
            'form': form,
            'title': 'Assign Shift',
        })


# ==========================================================================
# LEAVE TYPES
# ==========================================================================

class LeaveTypeListView(LoginRequiredMixin, ListView):
    model = LeaveType
    template_name = 'attendance/leave_type_list.html'
    context_object_name = 'leave_types'
    paginate_by = 20

    def get_queryset(self):
        qs = LeaveType.all_objects.filter(tenant=self.request.tenant)

        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class LeaveTypeCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = LeaveTypeForm(tenant=request.tenant)
        return render(request, 'attendance/leave_type_form.html', {
            'form': form,
            'title': 'Create Leave Type',
        })

    def post(self, request):
        form = LeaveTypeForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            leave_type = form.save(commit=False)
            leave_type.tenant = request.tenant
            leave_type.save()
            messages.success(request, f'Leave type "{leave_type.name}" created successfully.')
            return redirect('attendance:leave_type_list')
        return render(request, 'attendance/leave_type_form.html', {
            'form': form,
            'title': 'Create Leave Type',
        })


class LeaveTypeUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        leave_type = get_object_or_404(
            LeaveType.all_objects, pk=pk, tenant=request.tenant
        )
        form = LeaveTypeForm(instance=leave_type, tenant=request.tenant)
        return render(request, 'attendance/leave_type_form.html', {
            'form': form,
            'leave_type': leave_type,
            'title': 'Edit Leave Type',
        })

    def post(self, request, pk):
        leave_type = get_object_or_404(
            LeaveType.all_objects, pk=pk, tenant=request.tenant
        )
        form = LeaveTypeForm(request.POST, instance=leave_type, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Leave type "{leave_type.name}" updated successfully.')
            return redirect('attendance:leave_type_list')
        return render(request, 'attendance/leave_type_form.html', {
            'form': form,
            'leave_type': leave_type,
            'title': 'Edit Leave Type',
        })


# ==========================================================================
# LEAVE POLICIES
# ==========================================================================

class LeavePolicyListView(LoginRequiredMixin, ListView):
    model = LeavePolicy
    template_name = 'attendance/leave_policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        return LeavePolicy.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('leave_type')


class LeavePolicyCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = LeavePolicyForm(tenant=request.tenant)
        return render(request, 'attendance/leave_policy_form.html', {
            'form': form,
            'title': 'Create Leave Policy',
        })

    def post(self, request):
        form = LeavePolicyForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.tenant = request.tenant
            policy.save()
            messages.success(request, f'Leave policy "{policy.name}" created successfully.')
            return redirect('attendance:leave_policy_list')
        return render(request, 'attendance/leave_policy_form.html', {
            'form': form,
            'title': 'Create Leave Policy',
        })


class LeavePolicyUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        policy = get_object_or_404(
            LeavePolicy.all_objects, pk=pk, tenant=request.tenant
        )
        form = LeavePolicyForm(instance=policy, tenant=request.tenant)
        return render(request, 'attendance/leave_policy_form.html', {
            'form': form,
            'policy': policy,
            'title': 'Edit Leave Policy',
        })

    def post(self, request, pk):
        policy = get_object_or_404(
            LeavePolicy.all_objects, pk=pk, tenant=request.tenant
        )
        form = LeavePolicyForm(request.POST, instance=policy, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Leave policy "{policy.name}" updated successfully.')
            return redirect('attendance:leave_policy_list')
        return render(request, 'attendance/leave_policy_form.html', {
            'form': form,
            'policy': policy,
            'title': 'Edit Leave Policy',
        })


# ==========================================================================
# LEAVE BALANCES
# ==========================================================================

class LeaveBalanceListView(LoginRequiredMixin, ListView):
    model = LeaveBalance
    template_name = 'attendance/leave_balance_list.html'
    context_object_name = 'balances'
    paginate_by = 20

    def get_queryset(self):
        qs = LeaveBalance.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'leave_type')

        employee_id = self.request.GET.get('employee', '')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        leave_type_id = self.request.GET.get('leave_type', '')
        if leave_type_id:
            qs = qs.filter(leave_type_id=leave_type_id)

        year = self.request.GET.get('year', '')
        if year:
            qs = qs.filter(year=year)
        else:
            qs = qs.filter(year=timezone.now().year)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.all_objects.filter(
            tenant=self.request.tenant, status='active'
        ).order_by('first_name', 'last_name')
        context['leave_types'] = LeaveType.all_objects.filter(
            tenant=self.request.tenant, is_active=True
        )
        context['current_employee'] = self.request.GET.get('employee', '')
        context['current_leave_type'] = self.request.GET.get('leave_type', '')
        context['current_year'] = self.request.GET.get('year', str(timezone.now().year))
        return context


# ==========================================================================
# LEAVE APPLICATIONS
# ==========================================================================

class LeaveApplicationListView(LoginRequiredMixin, ListView):
    model = LeaveApplication
    template_name = 'attendance/leave_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        qs = LeaveApplication.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'leave_type', 'approved_by')

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        employee_id = self.request.GET.get('employee', '')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        leave_type_id = self.request.GET.get('leave_type', '')
        if leave_type_id:
            qs = qs.filter(leave_type_id=leave_type_id)

        date_from = self.request.GET.get('date_from', '')
        if date_from:
            qs = qs.filter(from_date__gte=date_from)

        date_to = self.request.GET.get('date_to', '')
        if date_to:
            qs = qs.filter(to_date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.all_objects.filter(
            tenant=self.request.tenant, status='active'
        ).order_by('first_name', 'last_name')
        context['leave_types'] = LeaveType.all_objects.filter(
            tenant=self.request.tenant, is_active=True
        )
        context['current_status'] = self.request.GET.get('status', '')
        context['current_employee'] = self.request.GET.get('employee', '')
        context['current_leave_type'] = self.request.GET.get('leave_type', '')
        context['current_date_from'] = self.request.GET.get('date_from', '')
        context['current_date_to'] = self.request.GET.get('date_to', '')
        context['status_choices'] = LeaveApplication.STATUS_CHOICES
        return context


class LeaveApplicationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = LeaveApplicationForm(tenant=request.tenant)
        return render(request, 'attendance/leave_form.html', {
            'form': form,
            'title': 'Apply for Leave',
        })

    def post(self, request):
        form = LeaveApplicationForm(request.POST, request.FILES, tenant=request.tenant)
        if form.is_valid():
            application = form.save(commit=False)
            employee = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()
            if not employee:
                messages.error(request, 'No employee record is linked to your account.')
                return redirect('attendance:leave_list')
            application.employee = employee
            application.tenant = request.tenant
            application.total_days = application.calculate_total_days()
            application.save()
            messages.success(request, 'Leave application submitted successfully.')
            return redirect('attendance:leave_detail', pk=application.pk)
        return render(request, 'attendance/leave_form.html', {
            'form': form,
            'title': 'Apply for Leave',
        })


class LeaveApplicationDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        application = get_object_or_404(
            LeaveApplication.all_objects.select_related(
                'employee', 'leave_type', 'approved_by'
            ),
            pk=pk,
            tenant=request.tenant,
        )
        approval_form = LeaveApprovalForm()
        return render(request, 'attendance/leave_detail.html', {
            'leave': application,
            'approval_form': approval_form,
        })


class LeaveApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(
            LeaveApplication.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        form = LeaveApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action', 'approved')
            approver = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()

            application.status = action
            application.approved_by = approver
            application.approved_at = timezone.now()

            if action == 'rejected':
                application.rejection_reason = form.cleaned_data.get(
                    'rejection_reason', ''
                )

            application.save()

            # If approved, update leave balance
            if action == 'approved':
                balance, created = LeaveBalance.all_objects.get_or_create(
                    tenant=request.tenant,
                    employee=application.employee,
                    leave_type=application.leave_type,
                    year=application.from_date.year,
                    defaults={'allocated': 0},
                )
                balance.used += application.total_days
                balance.save()

            messages.success(
                request,
                f'Leave application {application.get_status_display().lower()}.'
            )
        return redirect('attendance:leave_detail', pk=pk)


class LeaveCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(
            LeaveApplication.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        cancellation_reason = request.POST.get('cancellation_reason', '')
        was_approved = application.status == 'approved'

        application.status = 'cancelled'
        application.cancellation_reason = cancellation_reason
        application.cancelled_at = timezone.now()
        application.save()

        # If was approved, reverse the leave balance deduction
        if was_approved:
            try:
                balance = LeaveBalance.all_objects.get(
                    tenant=request.tenant,
                    employee=application.employee,
                    leave_type=application.leave_type,
                    year=application.from_date.year,
                )
                balance.used = max(0, balance.used - application.total_days)
                balance.save()
            except LeaveBalance.DoesNotExist:
                pass

        messages.success(request, 'Leave application cancelled successfully.')
        return redirect('attendance:leave_detail', pk=pk)


# ==========================================================================
# LEAVE CALENDAR
# ==========================================================================

class LeaveCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/leave_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = timezone.now().date()

        month = int(self.request.GET.get('month', today.month))
        year = int(self.request.GET.get('year', today.year))

        # Get approved leaves for the month
        month_start = date(year, month, 1)
        days_in_month = calendar.monthrange(year, month)[1]
        month_end = date(year, month, days_in_month)

        approved_leaves = LeaveApplication.all_objects.filter(
            tenant=tenant,
            status='approved',
            from_date__lte=month_end,
            to_date__gte=month_start,
        ).select_related('employee', 'leave_type').order_by('from_date')

        # Group by employee
        leave_by_employee = {}
        for leave in approved_leaves:
            emp_name = str(leave.employee)
            if emp_name not in leave_by_employee:
                leave_by_employee[emp_name] = []
            leave_by_employee[emp_name].append(leave)

        context.update({
            'leave_by_employee': leave_by_employee,
            'month': month,
            'year': year,
            'month_name': calendar.month_name[month],
            'days_in_month': days_in_month,
        })
        return context


# ==========================================================================
# PROJECTS
# ==========================================================================

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'attendance/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        qs = Project.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('manager')

        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(client_name__icontains=search)
            )

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = Project.STATUS_CHOICES
        return context


class ProjectCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProjectForm(tenant=request.tenant)
        return render(request, 'attendance/project_form.html', {
            'form': form,
            'title': 'Create Project',
        })

    def post(self, request):
        form = ProjectForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            project = form.save(commit=False)
            project.tenant = request.tenant
            project.save()
            form.save_m2m()
            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect('attendance:project_detail', pk=project.pk)
        return render(request, 'attendance/project_form.html', {
            'form': form,
            'title': 'Create Project',
        })


class ProjectDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(
            Project.all_objects.select_related('manager'),
            pk=pk,
            tenant=request.tenant,
        )
        tasks = Task.all_objects.filter(
            tenant=request.tenant, project=project
        ).select_related('assigned_to')
        time_entries = TimeEntry.all_objects.filter(
            tenant=request.tenant, project=project
        ).select_related('employee', 'task').order_by('-date')[:20]

        total_logged = project.time_entries.aggregate(
            total=Sum('hours')
        )['total'] or 0
        utilization = 0
        if project.budget_hours and project.budget_hours > 0:
            utilization = round((total_logged / float(project.budget_hours)) * 100, 1)

        return render(request, 'attendance/project_detail.html', {
            'project': project,
            'tasks': tasks,
            'time_entries': time_entries,
            'total_logged': total_logged,
            'utilization': utilization,
        })


class ProjectUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(
            Project.all_objects, pk=pk, tenant=request.tenant
        )
        form = ProjectForm(instance=project, tenant=request.tenant)
        return render(request, 'attendance/project_form.html', {
            'form': form,
            'project': project,
            'title': 'Edit Project',
        })

    def post(self, request, pk):
        project = get_object_or_404(
            Project.all_objects, pk=pk, tenant=request.tenant
        )
        form = ProjectForm(request.POST, instance=project, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully.')
            return redirect('attendance:project_detail', pk=project.pk)
        return render(request, 'attendance/project_form.html', {
            'form': form,
            'project': project,
            'title': 'Edit Project',
        })


# ==========================================================================
# TASKS
# ==========================================================================

class TaskCreateView(LoginRequiredMixin, View):
    def get(self, request, project_pk):
        project = get_object_or_404(
            Project.all_objects, pk=project_pk, tenant=request.tenant
        )
        form = TaskForm(tenant=request.tenant)
        return render(request, 'attendance/task_form.html', {
            'form': form,
            'project': project,
            'title': 'Create Task',
        })

    def post(self, request, project_pk):
        project = get_object_or_404(
            Project.all_objects, pk=project_pk, tenant=request.tenant
        )
        form = TaskForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.tenant = request.tenant
            task.save()
            messages.success(request, f'Task "{task.name}" created successfully.')
            return redirect('attendance:project_detail', pk=project.pk)
        return render(request, 'attendance/task_form.html', {
            'form': form,
            'project': project,
            'title': 'Create Task',
        })


class TaskUpdateView(LoginRequiredMixin, View):
    def get(self, request, project_pk, pk):
        project = get_object_or_404(
            Project.all_objects, pk=project_pk, tenant=request.tenant
        )
        task = get_object_or_404(
            Task.all_objects, pk=pk, project=project, tenant=request.tenant
        )
        form = TaskForm(instance=task, tenant=request.tenant)
        return render(request, 'attendance/task_form.html', {
            'form': form,
            'project': project,
            'task': task,
            'title': 'Edit Task',
        })

    def post(self, request, project_pk, pk):
        project = get_object_or_404(
            Project.all_objects, pk=project_pk, tenant=request.tenant
        )
        task = get_object_or_404(
            Task.all_objects, pk=pk, project=project, tenant=request.tenant
        )
        form = TaskForm(request.POST, instance=task, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.name}" updated successfully.')
            return redirect('attendance:project_detail', pk=project.pk)
        return render(request, 'attendance/task_form.html', {
            'form': form,
            'project': project,
            'task': task,
            'title': 'Edit Task',
        })


# ==========================================================================
# TIMESHEETS
# ==========================================================================

class TimesheetListView(LoginRequiredMixin, ListView):
    model = Timesheet
    template_name = 'attendance/timesheet_list.html'
    context_object_name = 'timesheets'
    paginate_by = 20

    def get_queryset(self):
        qs = Timesheet.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'approved_by')

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = Timesheet.STATUS_CHOICES
        return context


class TimesheetCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = TimesheetForm(tenant=request.tenant)
        return render(request, 'attendance/timesheet_form.html', {
            'form': form,
            'title': 'Create Timesheet',
        })

    def post(self, request):
        form = TimesheetForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            timesheet = form.save(commit=False)
            employee = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()
            if not employee:
                messages.error(request, 'No employee record is linked to your account.')
                return redirect('attendance:timesheet_list')
            timesheet.employee = employee
            timesheet.tenant = request.tenant
            # Calculate week_end_date as 6 days after week_start_date
            timesheet.week_end_date = (
                timesheet.week_start_date + timedelta(days=6)
            )
            timesheet.save()
            messages.success(request, 'Timesheet created successfully.')
            return redirect('attendance:timesheet_detail', pk=timesheet.pk)
        return render(request, 'attendance/timesheet_form.html', {
            'form': form,
            'title': 'Create Timesheet',
        })


class TimesheetDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        timesheet = get_object_or_404(
            Timesheet.all_objects.select_related('employee', 'approved_by'),
            pk=pk,
            tenant=request.tenant,
        )
        entries = TimeEntry.all_objects.filter(
            tenant=request.tenant, timesheet=timesheet
        ).select_related('project', 'task').order_by('date')

        entry_form = TimeEntryForm(tenant=request.tenant)

        return render(request, 'attendance/timesheet_detail.html', {
            'timesheet': timesheet,
            'entries': entries,
            'entry_form': entry_form,
        })


class TimesheetSubmitView(LoginRequiredMixin, View):
    def post(self, request, pk):
        timesheet = get_object_or_404(
            Timesheet.all_objects, pk=pk, tenant=request.tenant
        )
        if timesheet.status != 'draft':
            messages.error(request, 'Only draft timesheets can be submitted.')
            return redirect('attendance:timesheet_detail', pk=pk)

        timesheet.status = 'submitted'
        timesheet.submitted_at = timezone.now()
        timesheet.save()
        messages.success(request, 'Timesheet submitted for approval.')
        return redirect('attendance:timesheet_detail', pk=pk)


class TimesheetApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        timesheet = get_object_or_404(
            Timesheet.all_objects, pk=pk, tenant=request.tenant
        )
        form = TimesheetApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action', 'approved')
            approver = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()

            timesheet.status = action
            timesheet.approved_by = approver
            timesheet.approved_at = timezone.now()

            if action == 'rejected':
                timesheet.rejection_reason = form.cleaned_data.get(
                    'rejection_reason', ''
                )

            timesheet.save()
            messages.success(
                request,
                f'Timesheet {timesheet.get_status_display().lower()}.'
            )
        return redirect('attendance:timesheet_detail', pk=pk)


# ==========================================================================
# TIME ENTRIES
# ==========================================================================

class TimeEntryCreateView(LoginRequiredMixin, View):
    def post(self, request, ts_pk):
        timesheet = get_object_or_404(
            Timesheet.all_objects, pk=ts_pk, tenant=request.tenant
        )
        form = TimeEntryForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.timesheet = timesheet
            entry.employee = timesheet.employee
            entry.tenant = request.tenant
            entry.save()

            # Update timesheet totals
            timesheet.compute_totals()
            timesheet.save()

            messages.success(request, 'Time entry added successfully.')
        else:
            messages.error(request, 'Please correct the errors in the time entry form.')
        return redirect('attendance:timesheet_detail', pk=ts_pk)


class TimeEntryDeleteView(LoginRequiredMixin, View):
    def post(self, request, ts_pk, pk):
        timesheet = get_object_or_404(
            Timesheet.all_objects, pk=ts_pk, tenant=request.tenant
        )
        entry = get_object_or_404(
            TimeEntry.all_objects, pk=pk, timesheet=timesheet, tenant=request.tenant
        )
        entry.delete()

        # Update timesheet totals
        timesheet.compute_totals()
        timesheet.save()

        messages.success(request, 'Time entry deleted successfully.')
        return redirect('attendance:timesheet_detail', pk=ts_pk)


# ==========================================================================
# OVERTIME
# ==========================================================================

class OvertimeListView(LoginRequiredMixin, ListView):
    model = OvertimeRequest
    template_name = 'attendance/overtime_list.html'
    context_object_name = 'overtime_requests'
    paginate_by = 20

    def get_queryset(self):
        qs = OvertimeRequest.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'project', 'approved_by')

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = OvertimeRequest.STATUS_CHOICES
        return context


class OvertimeCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = OvertimeRequestForm(tenant=request.tenant)
        return render(request, 'attendance/overtime_form.html', {
            'form': form,
            'title': 'Request Overtime',
        })

    def post(self, request):
        form = OvertimeRequestForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            overtime = form.save(commit=False)
            employee = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()
            if not employee:
                messages.error(request, 'No employee record is linked to your account.')
                return redirect('attendance:overtime_list')
            overtime.employee = employee
            overtime.tenant = request.tenant
            overtime.save()
            messages.success(request, 'Overtime request submitted successfully.')
            return redirect('attendance:overtime_detail', pk=overtime.pk)
        return render(request, 'attendance/overtime_form.html', {
            'form': form,
            'title': 'Request Overtime',
        })


class OvertimeDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        overtime = get_object_or_404(
            OvertimeRequest.all_objects.select_related(
                'employee', 'project', 'approved_by'
            ),
            pk=pk,
            tenant=request.tenant,
        )
        approval_form = OvertimeApprovalForm()
        return render(request, 'attendance/overtime_detail.html', {
            'overtime': overtime,
            'approval_form': approval_form,
        })


class OvertimeApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        overtime = get_object_or_404(
            OvertimeRequest.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        form = OvertimeApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action', 'approved')
            approver = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()

            overtime.status = action
            overtime.approved_by = approver
            overtime.approved_at = timezone.now()

            if action == 'rejected':
                overtime.rejection_reason = form.cleaned_data.get(
                    'rejection_reason', ''
                )

            overtime.save()
            messages.success(
                request,
                f'Overtime request {overtime.get_status_display().lower()}.'
            )
        return redirect('attendance:overtime_detail', pk=pk)


# ==========================================================================
# HOLIDAYS
# ==========================================================================

class HolidayListView(LoginRequiredMixin, ListView):
    model = Holiday
    template_name = 'attendance/holiday_list.html'
    context_object_name = 'holidays'
    paginate_by = 20

    def get_queryset(self):
        qs = Holiday.all_objects.filter(tenant=self.request.tenant)

        year = self.request.GET.get('year', '')
        if year:
            qs = qs.filter(year=year)
        else:
            qs = qs.filter(year=timezone.now().year)

        holiday_type = self.request.GET.get('holiday_type', '')
        if holiday_type:
            qs = qs.filter(holiday_type=holiday_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = self.request.GET.get(
            'year', str(timezone.now().year)
        )
        context['current_holiday_type'] = self.request.GET.get('holiday_type', '')
        context['holiday_type_choices'] = Holiday.HOLIDAY_TYPE_CHOICES
        return context


class HolidayCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = HolidayForm(tenant=request.tenant)
        return render(request, 'attendance/holiday_form.html', {
            'form': form,
            'title': 'Create Holiday',
        })

    def post(self, request):
        form = HolidayForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            holiday = form.save(commit=False)
            holiday.tenant = request.tenant
            holiday.save()
            messages.success(request, f'Holiday "{holiday.name}" created successfully.')
            return redirect('attendance:holiday_list')
        return render(request, 'attendance/holiday_form.html', {
            'form': form,
            'title': 'Create Holiday',
        })


class HolidayUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        holiday = get_object_or_404(
            Holiday.all_objects, pk=pk, tenant=request.tenant
        )
        form = HolidayForm(instance=holiday, tenant=request.tenant)
        return render(request, 'attendance/holiday_form.html', {
            'form': form,
            'holiday': holiday,
            'title': 'Edit Holiday',
        })

    def post(self, request, pk):
        holiday = get_object_or_404(
            Holiday.all_objects, pk=pk, tenant=request.tenant
        )
        form = HolidayForm(request.POST, instance=holiday, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Holiday "{holiday.name}" updated successfully.')
            return redirect('attendance:holiday_list')
        return render(request, 'attendance/holiday_form.html', {
            'form': form,
            'holiday': holiday,
            'title': 'Edit Holiday',
        })


class HolidayCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/holiday_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = timezone.now().date()

        month = int(self.request.GET.get('month', today.month))
        year = int(self.request.GET.get('year', today.year))

        days_in_month = calendar.monthrange(year, month)[1]
        first_day_weekday = calendar.monthrange(year, month)[0]

        holidays = Holiday.all_objects.filter(
            tenant=tenant,
            date__year=year,
            date__month=month,
            is_active=True,
        )

        # Build a dict: {day_number: [list of holidays]}
        holiday_map = {}
        for h in holidays:
            day = h.date.day
            if day not in holiday_map:
                holiday_map[day] = []
            holiday_map[day].append({
                'name': h.name,
                'type': h.holiday_type,
                'type_display': h.get_holiday_type_display(),
            })

        context.update({
            'holiday_map': holiday_map,
            'month': month,
            'year': year,
            'month_name': calendar.month_name[month],
            'days_in_month': days_in_month,
            'first_day_weekday': first_day_weekday,
        })
        return context


# ==========================================================================
# FLOATING HOLIDAYS
# ==========================================================================

class FloatingHolidayListView(LoginRequiredMixin, ListView):
    model = FloatingHoliday
    template_name = 'attendance/floating_holiday_list.html'
    context_object_name = 'floating_holidays'
    paginate_by = 20

    def get_queryset(self):
        return FloatingHoliday.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('holiday', 'employee')


class FloatingHolidaySelectView(LoginRequiredMixin, View):
    def get(self, request):
        form = FloatingHolidayForm(tenant=request.tenant)
        return render(request, 'attendance/floating_holiday_form.html', {
            'form': form,
            'title': 'Select Floating Holiday',
        })

    def post(self, request):
        form = FloatingHolidayForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            floating = form.save(commit=False)
            employee = Employee.all_objects.filter(
                tenant=request.tenant, user=request.user
            ).first()
            if not employee:
                messages.error(request, 'No employee record is linked to your account.')
                return redirect('attendance:floating_holiday_list')
            floating.employee = employee
            floating.tenant = request.tenant
            floating.status = 'selected'
            floating.save()
            messages.success(request, 'Floating holiday selected successfully.')
            return redirect('attendance:floating_holiday_list')
        return render(request, 'attendance/floating_holiday_form.html', {
            'form': form,
            'title': 'Select Floating Holiday',
        })


# ==========================================================================
# HOLIDAY POLICIES
# ==========================================================================

class HolidayPolicyListView(LoginRequiredMixin, ListView):
    model = HolidayPolicy
    template_name = 'attendance/holiday_policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        qs = HolidayPolicy.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('location', 'department')

        year = self.request.GET.get('year', '')
        if year:
            qs = qs.filter(year=year)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = self.request.GET.get('year', '')
        return context


class HolidayPolicyCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = HolidayPolicyForm(tenant=request.tenant)
        return render(request, 'attendance/holiday_policy_form.html', {
            'form': form,
            'title': 'Create Holiday Policy',
        })

    def post(self, request):
        form = HolidayPolicyForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.tenant = request.tenant
            policy.save()
            form.save_m2m()
            messages.success(
                request, f'Holiday policy "{policy.name}" created successfully.'
            )
            return redirect('attendance:holiday_policy_list')
        return render(request, 'attendance/holiday_policy_form.html', {
            'form': form,
            'title': 'Create Holiday Policy',
        })


class HolidayPolicyUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        policy = get_object_or_404(
            HolidayPolicy.all_objects, pk=pk, tenant=request.tenant
        )
        form = HolidayPolicyForm(instance=policy, tenant=request.tenant)
        return render(request, 'attendance/holiday_policy_form.html', {
            'form': form,
            'policy': policy,
            'title': 'Edit Holiday Policy',
        })

    def post(self, request, pk):
        policy = get_object_or_404(
            HolidayPolicy.all_objects, pk=pk, tenant=request.tenant
        )
        form = HolidayPolicyForm(
            request.POST, instance=policy, tenant=request.tenant
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Holiday policy "{policy.name}" updated successfully.'
            )
            return redirect('attendance:holiday_policy_list')
        return render(request, 'attendance/holiday_policy_form.html', {
            'form': form,
            'policy': policy,
            'title': 'Edit Holiday Policy',
        })
