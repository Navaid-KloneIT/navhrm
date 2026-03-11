from django.urls import path
from . import views

app_name = 'talent'

urlpatterns = [
    # === Talent Pool ===
    path('assessments/', views.TalentAssessmentListView.as_view(), name='assessment_list'),
    path('assessments/create/', views.TalentAssessmentCreateView.as_view(), name='assessment_create'),
    path('assessments/<int:pk>/', views.TalentAssessmentDetailView.as_view(), name='assessment_detail'),
    path('assessments/<int:pk>/edit/', views.TalentAssessmentUpdateView.as_view(), name='assessment_edit'),
    path('assessments/<int:pk>/delete/', views.TalentAssessmentDeleteView.as_view(), name='assessment_delete'),
    path('nine-box-grid/', views.NineBoxGridView.as_view(), name='nine_box_grid'),

    # === Succession Planning ===
    path('critical-positions/', views.CriticalPositionListView.as_view(), name='critical_position_list'),
    path('critical-positions/create/', views.CriticalPositionCreateView.as_view(), name='critical_position_create'),
    path('critical-positions/<int:pk>/', views.CriticalPositionDetailView.as_view(), name='critical_position_detail'),
    path('critical-positions/<int:pk>/edit/', views.CriticalPositionUpdateView.as_view(), name='critical_position_edit'),
    path('critical-positions/<int:pk>/delete/', views.CriticalPositionDeleteView.as_view(), name='critical_position_delete'),
    path('critical-positions/<int:pk>/add-successor/', views.SuccessionCandidateCreateView.as_view(), name='successor_create'),
    path('successors/<int:pk>/edit/', views.SuccessionCandidateUpdateView.as_view(), name='successor_edit'),
    path('successors/<int:pk>/delete/', views.SuccessionCandidateDeleteView.as_view(), name='successor_delete'),

    # === Career Pathing ===
    path('career-paths/', views.CareerPathListView.as_view(), name='career_path_list'),
    path('career-paths/create/', views.CareerPathCreateView.as_view(), name='career_path_create'),
    path('career-paths/<int:pk>/', views.CareerPathDetailView.as_view(), name='career_path_detail'),
    path('career-paths/<int:pk>/edit/', views.CareerPathUpdateView.as_view(), name='career_path_edit'),
    path('career-paths/<int:pk>/delete/', views.CareerPathDeleteView.as_view(), name='career_path_delete'),
    path('career-paths/<int:pk>/add-step/', views.CareerPathStepCreateView.as_view(), name='career_path_step_create'),
    path('career-path-steps/<int:pk>/edit/', views.CareerPathStepUpdateView.as_view(), name='career_path_step_edit'),
    path('career-path-steps/<int:pk>/delete/', views.CareerPathStepDeleteView.as_view(), name='career_path_step_delete'),
    path('career-plans/', views.EmployeeCareerPlanListView.as_view(), name='career_plan_list'),
    path('career-plans/create/', views.EmployeeCareerPlanCreateView.as_view(), name='career_plan_create'),
    path('career-plans/<int:pk>/', views.EmployeeCareerPlanDetailView.as_view(), name='career_plan_detail'),
    path('career-plans/<int:pk>/edit/', views.EmployeeCareerPlanUpdateView.as_view(), name='career_plan_edit'),
    path('career-plans/<int:pk>/delete/', views.EmployeeCareerPlanDeleteView.as_view(), name='career_plan_delete'),

    # === Internal Mobility ===
    path('internal-postings/', views.InternalJobPostingListView.as_view(), name='internal_posting_list'),
    path('internal-postings/create/', views.InternalJobPostingCreateView.as_view(), name='internal_posting_create'),
    path('internal-postings/<int:pk>/', views.InternalJobPostingDetailView.as_view(), name='internal_posting_detail'),
    path('internal-postings/<int:pk>/edit/', views.InternalJobPostingUpdateView.as_view(), name='internal_posting_edit'),
    path('internal-postings/<int:pk>/delete/', views.InternalJobPostingDeleteView.as_view(), name='internal_posting_delete'),
    path('internal-postings/<int:pk>/apply/', views.TransferApplicationCreateView.as_view(), name='transfer_apply'),
    path('transfer-applications/', views.TransferApplicationListView.as_view(), name='transfer_application_list'),
    path('transfer-applications/<int:pk>/', views.TransferApplicationDetailView.as_view(), name='transfer_application_detail'),
    path('transfer-applications/<int:pk>/edit/', views.TransferApplicationUpdateView.as_view(), name='transfer_application_edit'),

    # === Talent Reviews ===
    path('review-sessions/', views.TalentReviewSessionListView.as_view(), name='review_session_list'),
    path('review-sessions/create/', views.TalentReviewSessionCreateView.as_view(), name='review_session_create'),
    path('review-sessions/<int:pk>/', views.TalentReviewSessionDetailView.as_view(), name='review_session_detail'),
    path('review-sessions/<int:pk>/edit/', views.TalentReviewSessionUpdateView.as_view(), name='review_session_edit'),
    path('review-sessions/<int:pk>/delete/', views.TalentReviewSessionDeleteView.as_view(), name='review_session_delete'),
    path('review-sessions/<int:pk>/add-participant/', views.TalentReviewParticipantCreateView.as_view(), name='review_participant_create'),
    path('review-participants/<int:pk>/edit/', views.TalentReviewParticipantUpdateView.as_view(), name='review_participant_edit'),
    path('review-participants/<int:pk>/delete/', views.TalentReviewParticipantDeleteView.as_view(), name='review_participant_delete'),

    # === Retention Strategies ===
    path('flight-risks/', views.FlightRiskAssessmentListView.as_view(), name='flight_risk_list'),
    path('flight-risks/create/', views.FlightRiskAssessmentCreateView.as_view(), name='flight_risk_create'),
    path('flight-risks/<int:pk>/', views.FlightRiskAssessmentDetailView.as_view(), name='flight_risk_detail'),
    path('flight-risks/<int:pk>/edit/', views.FlightRiskAssessmentUpdateView.as_view(), name='flight_risk_edit'),
    path('flight-risks/<int:pk>/delete/', views.FlightRiskAssessmentDeleteView.as_view(), name='flight_risk_delete'),
    path('retention-plans/', views.RetentionPlanListView.as_view(), name='retention_plan_list'),
    path('retention-plans/create/', views.RetentionPlanCreateView.as_view(), name='retention_plan_create'),
    path('retention-plans/<int:pk>/', views.RetentionPlanDetailView.as_view(), name='retention_plan_detail'),
    path('retention-plans/<int:pk>/edit/', views.RetentionPlanUpdateView.as_view(), name='retention_plan_edit'),
    path('retention-plans/<int:pk>/delete/', views.RetentionPlanDeleteView.as_view(), name='retention_plan_delete'),
    path('retention-plans/<int:pk>/add-action/', views.RetentionActionCreateView.as_view(), name='retention_action_create'),
    path('retention-actions/<int:pk>/edit/', views.RetentionActionUpdateView.as_view(), name='retention_action_edit'),
]
