from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # 9.1 User Management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/deactivate/', views.UserDeactivateView.as_view(), name='user_deactivate'),
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/create/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('roles/<int:pk>/edit/', views.RoleEditView.as_view(), name='role_edit'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('roles/assign/', views.RoleAssignmentView.as_view(), name='role_assign'),
    path('login-history/', views.LoginHistoryView.as_view(), name='login_history'),

    # 9.2 Workflow Configuration
    path('workflows/', views.WorkflowListView.as_view(), name='workflow_list'),
    path('workflows/create/', views.WorkflowCreateView.as_view(), name='workflow_create'),
    path('workflows/<int:pk>/', views.WorkflowDetailView.as_view(), name='workflow_detail'),
    path('workflows/<int:pk>/edit/', views.WorkflowEditView.as_view(), name='workflow_edit'),
    path('workflows/<int:pk>/delete/', views.WorkflowDeleteView.as_view(), name='workflow_delete'),
    path('email-templates/', views.EmailTemplateListView.as_view(), name='email_template_list'),
    path('email-templates/create/', views.EmailTemplateCreateView.as_view(), name='email_template_create'),
    path('email-templates/<int:pk>/edit/', views.EmailTemplateEditView.as_view(), name='email_template_edit'),
    path('email-templates/<int:pk>/delete/', views.EmailTemplateDeleteView.as_view(), name='email_template_delete'),
    path('email-templates/<int:pk>/preview/', views.EmailTemplatePreviewView.as_view(), name='email_template_preview'),
    path('notification-settings/', views.NotificationSettingsView.as_view(), name='notification_settings'),
    path('escalation-rules/', views.EscalationRuleListView.as_view(), name='escalation_list'),
    path('escalation-rules/create/', views.EscalationRuleCreateView.as_view(), name='escalation_create'),
    path('escalation-rules/<int:pk>/edit/', views.EscalationRuleEditView.as_view(), name='escalation_edit'),
    path('escalation-rules/<int:pk>/delete/', views.EscalationRuleDeleteView.as_view(), name='escalation_delete'),

    # 9.3 System Configuration
    path('company-settings/', views.CompanySettingsView.as_view(), name='company_settings'),
    path('financial-years/', views.FinancialYearListView.as_view(), name='financial_year_list'),
    path('financial-years/create/', views.FinancialYearCreateView.as_view(), name='financial_year_create'),
    path('financial-years/<int:pk>/edit/', views.FinancialYearEditView.as_view(), name='financial_year_edit'),
    path('financial-years/<int:pk>/delete/', views.FinancialYearDeleteView.as_view(), name='financial_year_delete'),
    path('financial-years/<int:pk>/periods/', views.FinancialPeriodListView.as_view(), name='financial_period_list'),
    path('financial-years/<int:pk>/generate-periods/', views.GeneratePeriodsView.as_view(), name='generate_periods'),
    path('working-hours/', views.WorkingHoursListView.as_view(), name='working_hours_list'),
    path('working-hours/create/', views.WorkingHoursCreateView.as_view(), name='working_hours_create'),
    path('working-hours/<int:pk>/edit/', views.WorkingHoursEditView.as_view(), name='working_hours_edit'),
    path('working-hours/<int:pk>/delete/', views.WorkingHoursDeleteView.as_view(), name='working_hours_delete'),
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/edit/', views.LocationEditView.as_view(), name='location_edit'),
    path('locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),
    path('integrations/', views.IntegrationListView.as_view(), name='integration_list'),
    path('integrations/create/', views.IntegrationCreateView.as_view(), name='integration_create'),
    path('integrations/<int:pk>/edit/', views.IntegrationEditView.as_view(), name='integration_edit'),
    path('integrations/<int:pk>/delete/', views.IntegrationDeleteView.as_view(), name='integration_delete'),
    path('integrations/<int:pk>/test/', views.IntegrationTestView.as_view(), name='integration_test'),

    # 9.4 Audit & Compliance
    path('audit-trail/', views.AuditTrailView.as_view(), name='audit_trail'),
    path('audit-trail/<int:pk>/', views.AuditDetailView.as_view(), name='audit_detail'),
    path('data-privacy/', views.DataPrivacyView.as_view(), name='data_privacy'),
    path('data-retention/', views.DataRetentionListView.as_view(), name='data_retention_list'),
    path('data-retention/create/', views.DataRetentionCreateView.as_view(), name='data_retention_create'),
    path('data-retention/<int:pk>/edit/', views.DataRetentionEditView.as_view(), name='data_retention_edit'),
    path('data-retention/<int:pk>/delete/', views.DataRetentionDeleteView.as_view(), name='data_retention_delete'),
    path('access-logs/', views.AccessLogsView.as_view(), name='access_logs'),
    path('backup/', views.BackupRecoveryView.as_view(), name='backup'),
    path('backup/run/', views.BackupNowView.as_view(), name='backup_run'),
    path('backup/<int:pk>/download/', views.BackupDownloadView.as_view(), name='backup_download'),
]
