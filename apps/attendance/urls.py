from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Attendance Dashboard
    path('', views.AttendanceDashboardView.as_view(), name='dashboard'),

    # Check-In/Check-Out
    path('punch/', views.CheckInOutView.as_view(), name='punch'),

    # Attendance Records
    path('records/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('calendar/', views.AttendanceCalendarView.as_view(), name='attendance_calendar'),

    # Regularization
    path('regularization/', views.RegularizationListView.as_view(), name='regularization_list'),
    path('regularization/create/', views.RegularizationCreateView.as_view(), name='regularization_create'),
    path('regularization/<int:pk>/', views.RegularizationDetailView.as_view(), name='regularization_detail'),
    path('regularization/<int:pk>/approve/', views.RegularizationApproveView.as_view(), name='regularization_approve'),

    # Shifts
    path('shifts/', views.ShiftListView.as_view(), name='shift_list'),
    path('shifts/create/', views.ShiftCreateView.as_view(), name='shift_create'),
    path('shifts/<int:pk>/edit/', views.ShiftUpdateView.as_view(), name='shift_edit'),

    # Shift Assignments
    path('shift-assignments/', views.ShiftAssignmentListView.as_view(), name='shift_assignment_list'),
    path('shift-assignments/create/', views.ShiftAssignmentCreateView.as_view(), name='shift_assignment_create'),

    # Leave Types
    path('leave-types/', views.LeaveTypeListView.as_view(), name='leave_type_list'),
    path('leave-types/create/', views.LeaveTypeCreateView.as_view(), name='leave_type_create'),
    path('leave-types/<int:pk>/edit/', views.LeaveTypeUpdateView.as_view(), name='leave_type_edit'),

    # Leave Policies
    path('leave-policies/', views.LeavePolicyListView.as_view(), name='leave_policy_list'),
    path('leave-policies/create/', views.LeavePolicyCreateView.as_view(), name='leave_policy_create'),
    path('leave-policies/<int:pk>/edit/', views.LeavePolicyUpdateView.as_view(), name='leave_policy_edit'),

    # Leave Balances
    path('leave-balances/', views.LeaveBalanceListView.as_view(), name='leave_balance_list'),

    # Leave Applications
    path('leaves/', views.LeaveApplicationListView.as_view(), name='leave_list'),
    path('leaves/apply/', views.LeaveApplicationCreateView.as_view(), name='leave_apply'),
    path('leaves/<int:pk>/', views.LeaveApplicationDetailView.as_view(), name='leave_detail'),
    path('leaves/<int:pk>/approve/', views.LeaveApproveView.as_view(), name='leave_approve'),
    path('leaves/<int:pk>/cancel/', views.LeaveCancelView.as_view(), name='leave_cancel'),
    path('leave-calendar/', views.LeaveCalendarView.as_view(), name='leave_calendar'),

    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),

    # Tasks
    path('projects/<int:project_pk>/tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('projects/<int:project_pk>/tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),

    # Timesheets
    path('timesheets/', views.TimesheetListView.as_view(), name='timesheet_list'),
    path('timesheets/create/', views.TimesheetCreateView.as_view(), name='timesheet_create'),
    path('timesheets/<int:pk>/', views.TimesheetDetailView.as_view(), name='timesheet_detail'),
    path('timesheets/<int:pk>/submit/', views.TimesheetSubmitView.as_view(), name='timesheet_submit'),
    path('timesheets/<int:pk>/approve/', views.TimesheetApproveView.as_view(), name='timesheet_approve'),

    # Time Entries
    path('timesheets/<int:ts_pk>/entries/create/', views.TimeEntryCreateView.as_view(), name='time_entry_create'),
    path('timesheets/<int:ts_pk>/entries/<int:pk>/delete/', views.TimeEntryDeleteView.as_view(), name='time_entry_delete'),

    # Overtime
    path('overtime/', views.OvertimeListView.as_view(), name='overtime_list'),
    path('overtime/create/', views.OvertimeCreateView.as_view(), name='overtime_create'),
    path('overtime/<int:pk>/', views.OvertimeDetailView.as_view(), name='overtime_detail'),
    path('overtime/<int:pk>/approve/', views.OvertimeApproveView.as_view(), name='overtime_approve'),

    # Holidays
    path('holidays/', views.HolidayListView.as_view(), name='holiday_list'),
    path('holidays/create/', views.HolidayCreateView.as_view(), name='holiday_create'),
    path('holidays/<int:pk>/edit/', views.HolidayUpdateView.as_view(), name='holiday_edit'),
    path('holiday-calendar/', views.HolidayCalendarView.as_view(), name='holiday_calendar'),

    # Floating Holidays
    path('floating-holidays/', views.FloatingHolidayListView.as_view(), name='floating_holiday_list'),
    path('floating-holidays/select/', views.FloatingHolidaySelectView.as_view(), name='floating_holiday_select'),

    # Holiday Policies
    path('holiday-policies/', views.HolidayPolicyListView.as_view(), name='holiday_policy_list'),
    path('holiday-policies/create/', views.HolidayPolicyCreateView.as_view(), name='holiday_policy_create'),
    path('holiday-policies/<int:pk>/edit/', views.HolidayPolicyUpdateView.as_view(), name='holiday_policy_edit'),
]
