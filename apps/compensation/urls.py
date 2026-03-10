from django.urls import path
from . import views

app_name = 'compensation'

urlpatterns = [
    # === Salary Benchmarking ===
    path('benchmarks/', views.BenchmarkListView.as_view(), name='benchmark_list'),
    path('benchmarks/create/', views.BenchmarkCreateView.as_view(), name='benchmark_create'),
    path('benchmarks/<int:pk>/', views.BenchmarkDetailView.as_view(), name='benchmark_detail'),
    path('benchmarks/<int:pk>/edit/', views.BenchmarkUpdateView.as_view(), name='benchmark_edit'),
    path('benchmarks/<int:pk>/delete/', views.BenchmarkDeleteView.as_view(), name='benchmark_delete'),

    # === Benefits Administration ===
    path('benefits/plans/', views.BenefitPlanListView.as_view(), name='benefit_plan_list'),
    path('benefits/plans/create/', views.BenefitPlanCreateView.as_view(), name='benefit_plan_create'),
    path('benefits/plans/<int:pk>/', views.BenefitPlanDetailView.as_view(), name='benefit_plan_detail'),
    path('benefits/plans/<int:pk>/edit/', views.BenefitPlanUpdateView.as_view(), name='benefit_plan_edit'),
    path('benefits/plans/<int:pk>/delete/', views.BenefitPlanDeleteView.as_view(), name='benefit_plan_delete'),
    path('benefits/enrollments/', views.EmployeeBenefitListView.as_view(), name='employee_benefit_list'),
    path('benefits/enrollments/create/', views.EmployeeBenefitCreateView.as_view(), name='employee_benefit_create'),
    path('benefits/enrollments/<int:pk>/edit/', views.EmployeeBenefitUpdateView.as_view(), name='employee_benefit_edit'),
    path('benefits/enrollments/<int:pk>/delete/', views.EmployeeBenefitDeleteView.as_view(), name='employee_benefit_delete'),

    # === Flexible Benefits ===
    path('flex/plans/', views.FlexPlanListView.as_view(), name='flex_plan_list'),
    path('flex/plans/create/', views.FlexPlanCreateView.as_view(), name='flex_plan_create'),
    path('flex/plans/<int:pk>/', views.FlexPlanDetailView.as_view(), name='flex_plan_detail'),
    path('flex/plans/<int:pk>/edit/', views.FlexPlanUpdateView.as_view(), name='flex_plan_edit'),
    path('flex/plans/<int:pk>/delete/', views.FlexPlanDeleteView.as_view(), name='flex_plan_delete'),
    path('flex/plans/<int:pk>/options/create/', views.FlexOptionCreateView.as_view(), name='flex_option_create'),
    path('flex/options/<int:pk>/edit/', views.FlexOptionUpdateView.as_view(), name='flex_option_edit'),
    path('flex/options/<int:pk>/delete/', views.FlexOptionDeleteView.as_view(), name='flex_option_delete'),
    path('flex/selections/', views.FlexSelectionListView.as_view(), name='flex_selection_list'),
    path('flex/selections/create/', views.FlexSelectionCreateView.as_view(), name='flex_selection_create'),
    path('flex/selections/<int:pk>/edit/', views.FlexSelectionUpdateView.as_view(), name='flex_selection_edit'),

    # === Stock/ESOP Management ===
    path('equity/grants/', views.EquityGrantListView.as_view(), name='equity_grant_list'),
    path('equity/grants/create/', views.EquityGrantCreateView.as_view(), name='equity_grant_create'),
    path('equity/grants/<int:pk>/', views.EquityGrantDetailView.as_view(), name='equity_grant_detail'),
    path('equity/grants/<int:pk>/edit/', views.EquityGrantUpdateView.as_view(), name='equity_grant_edit'),
    path('equity/grants/<int:pk>/delete/', views.EquityGrantDeleteView.as_view(), name='equity_grant_delete'),
    path('equity/grants/<int:pk>/vesting/create/', views.VestingEventCreateView.as_view(), name='vesting_event_create'),
    path('equity/grants/<int:pk>/exercise/create/', views.ExerciseRecordCreateView.as_view(), name='exercise_record_create'),

    # === Compensation Planning ===
    path('plans/', views.CompensationPlanListView.as_view(), name='compensation_plan_list'),
    path('plans/create/', views.CompensationPlanCreateView.as_view(), name='compensation_plan_create'),
    path('plans/<int:pk>/', views.CompensationPlanDetailView.as_view(), name='compensation_plan_detail'),
    path('plans/<int:pk>/edit/', views.CompensationPlanUpdateView.as_view(), name='compensation_plan_edit'),
    path('plans/<int:pk>/delete/', views.CompensationPlanDeleteView.as_view(), name='compensation_plan_delete'),
    path('plans/<int:pk>/approve/', views.CompensationPlanApproveView.as_view(), name='compensation_plan_approve'),
    path('recommendations/', views.RecommendationListView.as_view(), name='recommendation_list'),
    path('recommendations/create/', views.RecommendationCreateView.as_view(), name='recommendation_create'),
    path('recommendations/<int:pk>/edit/', views.RecommendationUpdateView.as_view(), name='recommendation_edit'),
    path('recommendations/<int:pk>/delete/', views.RecommendationDeleteView.as_view(), name='recommendation_delete'),
    path('recommendations/<int:pk>/approve/', views.RecommendationApproveView.as_view(), name='recommendation_approve'),
    path('recommendations/<int:pk>/reject/', views.RecommendationRejectView.as_view(), name='recommendation_reject'),

    # === Rewards & Recognition ===
    path('rewards/programs/', views.RewardProgramListView.as_view(), name='reward_program_list'),
    path('rewards/programs/create/', views.RewardProgramCreateView.as_view(), name='reward_program_create'),
    path('rewards/programs/<int:pk>/', views.RewardProgramDetailView.as_view(), name='reward_program_detail'),
    path('rewards/programs/<int:pk>/edit/', views.RewardProgramUpdateView.as_view(), name='reward_program_edit'),
    path('rewards/programs/<int:pk>/delete/', views.RewardProgramDeleteView.as_view(), name='reward_program_delete'),
    path('rewards/recognitions/', views.RecognitionListView.as_view(), name='recognition_list'),
    path('rewards/recognitions/create/', views.RecognitionCreateView.as_view(), name='recognition_create'),
    path('rewards/recognitions/<int:pk>/', views.RecognitionDetailView.as_view(), name='recognition_detail'),
    path('rewards/recognitions/<int:pk>/edit/', views.RecognitionUpdateView.as_view(), name='recognition_edit'),
    path('rewards/recognitions/<int:pk>/approve/', views.RecognitionApproveView.as_view(), name='recognition_approve'),
    path('rewards/recognitions/<int:pk>/reject/', views.RecognitionRejectView.as_view(), name='recognition_reject'),
]
