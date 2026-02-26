from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Reports Home
    path('', views.ReportsDashboardView.as_view(), name='reports_dashboard'),

    # HR Reports
    path('hr/headcount/', views.HeadcountReportView.as_view(), name='hr_headcount'),
    path('hr/attrition/', views.AttritionReportView.as_view(), name='hr_attrition'),
    path('hr/diversity/', views.DiversityReportView.as_view(), name='hr_diversity'),
    path('hr/cost/', views.CostReportView.as_view(), name='hr_cost'),
    path('hr/hiring/', views.HiringReportView.as_view(), name='hr_hiring'),

    # Attendance Reports
    path('attendance/summary/', views.AttendanceSummaryView.as_view(), name='attendance_summary'),
    path('attendance/lateness/', views.LatenessReportView.as_view(), name='attendance_lateness'),
    path('attendance/absenteeism/', views.AbsenteeismReportView.as_view(), name='attendance_absenteeism'),
    path('attendance/overtime/', views.OvertimeReportView.as_view(), name='attendance_overtime'),
    path('attendance/utilization/', views.UtilizationReportView.as_view(), name='attendance_utilization'),

    # Leave Reports
    path('leave/register/', views.LeaveRegisterView.as_view(), name='leave_register'),
    path('leave/liability/', views.LeaveLiabilityView.as_view(), name='leave_liability'),
    path('leave/compoff/', views.CompOffReportView.as_view(), name='leave_compoff'),
    path('leave/trend/', views.LeaveTrendView.as_view(), name='leave_trend'),

    # Payroll Reports
    path('payroll/register/', views.SalaryRegisterView.as_view(), name='payroll_register'),
    path('payroll/tax/', views.TaxReportView.as_view(), name='payroll_tax'),
    path('payroll/statutory/', views.StatutoryReportView.as_view(), name='payroll_statutory'),
    path('payroll/cost/', views.PayrollCostView.as_view(), name='payroll_cost'),

    # Analytics Dashboard
    path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
]
