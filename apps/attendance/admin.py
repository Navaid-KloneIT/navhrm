from django.contrib import admin
from .models import (
    Shift, ShiftAssignment,
    Attendance, AttendanceRegularization,
    LeaveType, LeavePolicy, LeaveBalance, LeaveApplication,
    Project, Task, Timesheet, TimeEntry,
    OvertimeRequest,
    Holiday, FloatingHoliday, HolidayPolicy,
)


# ==========================================================================
# SHIFT MANAGEMENT
# ==========================================================================

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'shift', 'effective_from', 'effective_to', 'is_active']
    list_filter = ['is_active']
    search_fields = ['employee__first_name', 'employee__last_name']


# ==========================================================================
# ATTENDANCE MANAGEMENT
# ==========================================================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'check_in', 'check_out', 'total_hours']
    list_filter = ['status', 'date', 'source']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(AttendanceRegularization)
class AttendanceRegularizationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'reason', 'status']
    list_filter = ['status', 'reason']
    search_fields = ['employee__first_name', 'employee__last_name']


# ==========================================================================
# LEAVE MANAGEMENT
# ==========================================================================

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'is_paid', 'max_days_per_year', 'is_active']
    list_filter = ['category', 'is_paid', 'is_active']
    search_fields = ['name', 'code']


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'leave_type', 'accrual_frequency', 'is_active']
    list_filter = ['accrual_frequency', 'is_active']
    search_fields = ['name']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'allocated', 'used']
    list_filter = ['year']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'from_date', 'to_date', 'total_days', 'status']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__first_name', 'employee__last_name']


# ==========================================================================
# TIME TRACKING
# ==========================================================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'client_name', 'status', 'is_billable']
    list_filter = ['status', 'is_billable']
    search_fields = ['name', 'code', 'client_name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'assigned_to', 'status']
    list_filter = ['status']
    search_fields = ['name', 'project__name']


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ['employee', 'week_start_date', 'total_hours', 'status']
    list_filter = ['status']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'project', 'date', 'hours', 'is_billable']
    list_filter = ['is_billable']
    search_fields = ['employee__first_name', 'employee__last_name', 'project__name']


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'ot_type', 'planned_hours', 'actual_hours', 'status']
    list_filter = ['status', 'ot_type']
    search_fields = ['employee__first_name', 'employee__last_name']


# ==========================================================================
# HOLIDAY MANAGEMENT
# ==========================================================================

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'holiday_type', 'year', 'is_active']
    list_filter = ['holiday_type', 'year', 'is_active']
    search_fields = ['name']


@admin.register(FloatingHoliday)
class FloatingHolidayAdmin(admin.ModelAdmin):
    list_display = ['employee', 'holiday', 'status']
    list_filter = ['status']
    search_fields = ['employee__first_name', 'employee__last_name', 'holiday__name']


@admin.register(HolidayPolicy)
class HolidayPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'max_floating_holidays', 'is_active']
    list_filter = ['year', 'is_active']
    search_fields = ['name']
