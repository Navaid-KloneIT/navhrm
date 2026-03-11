from django.urls import path
from . import views

app_name = 'compliance'

urlpatterns = [
    # === Labor Law Compliance ===
    path('labor-laws/', views.LaborLawListView.as_view(), name='labor_law_list'),
    path('labor-laws/create/', views.LaborLawCreateView.as_view(), name='labor_law_create'),
    path('labor-laws/<int:pk>/', views.LaborLawDetailView.as_view(), name='labor_law_detail'),
    path('labor-laws/<int:pk>/edit/', views.LaborLawUpdateView.as_view(), name='labor_law_edit'),
    path('labor-laws/<int:pk>/delete/', views.LaborLawDeleteView.as_view(), name='labor_law_delete'),
    path('labor-laws/<int:pk>/add-compliance/', views.LaborLawComplianceCreateView.as_view(), name='law_compliance_create'),
    path('law-compliance/<int:pk>/edit/', views.LaborLawComplianceUpdateView.as_view(), name='law_compliance_edit'),
    path('law-compliance/<int:pk>/delete/', views.LaborLawComplianceDeleteView.as_view(), name='law_compliance_delete'),

    # === Contract Management ===
    path('contracts/', views.EmploymentContractListView.as_view(), name='contract_list'),
    path('contracts/create/', views.EmploymentContractCreateView.as_view(), name='contract_create'),
    path('contracts/<int:pk>/', views.EmploymentContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/edit/', views.EmploymentContractUpdateView.as_view(), name='contract_edit'),
    path('contracts/<int:pk>/delete/', views.EmploymentContractDeleteView.as_view(), name='contract_delete'),
    path('contracts/<int:pk>/add-amendment/', views.ContractAmendmentCreateView.as_view(), name='amendment_create'),
    path('amendments/<int:pk>/edit/', views.ContractAmendmentUpdateView.as_view(), name='amendment_edit'),
    path('amendments/<int:pk>/delete/', views.ContractAmendmentDeleteView.as_view(), name='amendment_delete'),

    # === Policy Management ===
    path('policies/', views.CompliancePolicyListView.as_view(), name='policy_list'),
    path('policies/create/', views.CompliancePolicyCreateView.as_view(), name='policy_create'),
    path('policies/<int:pk>/', views.CompliancePolicyDetailView.as_view(), name='policy_detail'),
    path('policies/<int:pk>/edit/', views.CompliancePolicyUpdateView.as_view(), name='policy_edit'),
    path('policies/<int:pk>/delete/', views.CompliancePolicyDeleteView.as_view(), name='policy_delete'),
    path('policies/<int:pk>/add-version/', views.PolicyVersionCreateView.as_view(), name='policy_version_create'),
    path('policy-versions/<int:pk>/delete/', views.PolicyVersionDeleteView.as_view(), name='policy_version_delete'),
    path('policies/<int:pk>/add-acknowledgment/', views.PolicyAcknowledgmentCreateView.as_view(), name='policy_acknowledgment_create'),

    # === Disciplinary Actions ===
    path('incidents/', views.DisciplinaryIncidentListView.as_view(), name='incident_list'),
    path('incidents/create/', views.DisciplinaryIncidentCreateView.as_view(), name='incident_create'),
    path('incidents/<int:pk>/', views.DisciplinaryIncidentDetailView.as_view(), name='incident_detail'),
    path('incidents/<int:pk>/edit/', views.DisciplinaryIncidentUpdateView.as_view(), name='incident_edit'),
    path('incidents/<int:pk>/delete/', views.DisciplinaryIncidentDeleteView.as_view(), name='incident_delete'),
    path('incidents/<int:pk>/add-warning/', views.WarningRecordCreateView.as_view(), name='warning_create'),
    path('warnings/<int:pk>/edit/', views.WarningRecordUpdateView.as_view(), name='warning_edit'),
    path('warnings/<int:pk>/delete/', views.WarningRecordDeleteView.as_view(), name='warning_delete'),
    path('warnings/<int:pk>/add-appeal/', views.DisciplinaryAppealCreateView.as_view(), name='appeal_create'),
    path('appeals/<int:pk>/edit/', views.DisciplinaryAppealUpdateView.as_view(), name='appeal_edit'),

    # === Grievance Handling ===
    path('grievances/', views.GrievanceListView.as_view(), name='grievance_list'),
    path('grievances/create/', views.GrievanceCreateView.as_view(), name='grievance_create'),
    path('grievances/<int:pk>/', views.GrievanceDetailView.as_view(), name='grievance_detail'),
    path('grievances/<int:pk>/edit/', views.GrievanceUpdateView.as_view(), name='grievance_edit'),
    path('grievances/<int:pk>/delete/', views.GrievanceDeleteView.as_view(), name='grievance_delete'),
    path('grievances/<int:pk>/add-investigation/', views.GrievanceInvestigationCreateView.as_view(), name='investigation_create'),
    path('investigations/<int:pk>/edit/', views.GrievanceInvestigationUpdateView.as_view(), name='investigation_edit'),
    path('investigations/<int:pk>/delete/', views.GrievanceInvestigationDeleteView.as_view(), name='investigation_delete'),

    # === Statutory Registers ===
    path('muster-rolls/', views.MusterRollListView.as_view(), name='muster_roll_list'),
    path('muster-rolls/create/', views.MusterRollCreateView.as_view(), name='muster_roll_create'),
    path('muster-rolls/<int:pk>/', views.MusterRollDetailView.as_view(), name='muster_roll_detail'),
    path('muster-rolls/<int:pk>/edit/', views.MusterRollUpdateView.as_view(), name='muster_roll_edit'),
    path('muster-rolls/<int:pk>/delete/', views.MusterRollDeleteView.as_view(), name='muster_roll_delete'),

    path('wage-registers/', views.WageRegisterListView.as_view(), name='wage_register_list'),
    path('wage-registers/create/', views.WageRegisterCreateView.as_view(), name='wage_register_create'),
    path('wage-registers/<int:pk>/', views.WageRegisterDetailView.as_view(), name='wage_register_detail'),
    path('wage-registers/<int:pk>/edit/', views.WageRegisterUpdateView.as_view(), name='wage_register_edit'),
    path('wage-registers/<int:pk>/delete/', views.WageRegisterDeleteView.as_view(), name='wage_register_delete'),

    path('inspections/', views.InspectionReportListView.as_view(), name='inspection_list'),
    path('inspections/create/', views.InspectionReportCreateView.as_view(), name='inspection_create'),
    path('inspections/<int:pk>/', views.InspectionReportDetailView.as_view(), name='inspection_detail'),
    path('inspections/<int:pk>/edit/', views.InspectionReportUpdateView.as_view(), name='inspection_edit'),
    path('inspections/<int:pk>/delete/', views.InspectionReportDeleteView.as_view(), name='inspection_delete'),
]
