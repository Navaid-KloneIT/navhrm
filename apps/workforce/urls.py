from django.urls import path
from . import views

app_name = 'workforce'

urlpatterns = [
    # === Demand Forecasting ===
    path('forecasts/', views.DemandForecastListView.as_view(), name='forecast_list'),
    path('forecasts/create/', views.DemandForecastCreateView.as_view(), name='forecast_create'),
    path('forecasts/<int:pk>/', views.DemandForecastDetailView.as_view(), name='forecast_detail'),
    path('forecasts/<int:pk>/edit/', views.DemandForecastUpdateView.as_view(), name='forecast_edit'),
    path('forecasts/<int:pk>/delete/', views.DemandForecastDeleteView.as_view(), name='forecast_delete'),

    # === Supply Analysis - Skills ===
    path('skills/', views.SkillInventoryListView.as_view(), name='skill_list'),
    path('skills/create/', views.SkillInventoryCreateView.as_view(), name='skill_create'),
    path('skills/<int:pk>/', views.SkillInventoryDetailView.as_view(), name='skill_detail'),
    path('skills/<int:pk>/edit/', views.SkillInventoryUpdateView.as_view(), name='skill_edit'),
    path('skills/<int:pk>/delete/', views.SkillInventoryDeleteView.as_view(), name='skill_delete'),

    # === Supply Analysis - Talent Availability ===
    path('availability/', views.TalentAvailabilityListView.as_view(), name='availability_list'),
    path('availability/create/', views.TalentAvailabilityCreateView.as_view(), name='availability_create'),
    path('availability/<int:pk>/', views.TalentAvailabilityDetailView.as_view(), name='availability_detail'),
    path('availability/<int:pk>/edit/', views.TalentAvailabilityUpdateView.as_view(), name='availability_edit'),
    path('availability/<int:pk>/delete/', views.TalentAvailabilityDeleteView.as_view(), name='availability_delete'),

    # === Gap Analysis ===
    path('gaps/', views.WorkforceGapListView.as_view(), name='gap_list'),
    path('gaps/create/', views.WorkforceGapCreateView.as_view(), name='gap_create'),
    path('gaps/<int:pk>/', views.WorkforceGapDetailView.as_view(), name='gap_detail'),
    path('gaps/<int:pk>/edit/', views.WorkforceGapUpdateView.as_view(), name='gap_edit'),
    path('gaps/<int:pk>/delete/', views.WorkforceGapDeleteView.as_view(), name='gap_delete'),

    # === Budget Planning - Hiring Budget ===
    path('hiring-budgets/', views.HiringBudgetListView.as_view(), name='hiring_budget_list'),
    path('hiring-budgets/create/', views.HiringBudgetCreateView.as_view(), name='hiring_budget_create'),
    path('hiring-budgets/<int:pk>/', views.HiringBudgetDetailView.as_view(), name='hiring_budget_detail'),
    path('hiring-budgets/<int:pk>/edit/', views.HiringBudgetUpdateView.as_view(), name='hiring_budget_edit'),
    path('hiring-budgets/<int:pk>/delete/', views.HiringBudgetDeleteView.as_view(), name='hiring_budget_delete'),

    # === Budget Planning - Salary Forecast ===
    path('salary-forecasts/', views.SalaryForecastListView.as_view(), name='salary_forecast_list'),
    path('salary-forecasts/create/', views.SalaryForecastCreateView.as_view(), name='salary_forecast_create'),
    path('salary-forecasts/<int:pk>/', views.SalaryForecastDetailView.as_view(), name='salary_forecast_detail'),
    path('salary-forecasts/<int:pk>/edit/', views.SalaryForecastUpdateView.as_view(), name='salary_forecast_edit'),
    path('salary-forecasts/<int:pk>/delete/', views.SalaryForecastDeleteView.as_view(), name='salary_forecast_delete'),

    # === Scenario Planning ===
    path('scenarios/', views.WorkforceScenarioListView.as_view(), name='scenario_list'),
    path('scenarios/create/', views.WorkforceScenarioCreateView.as_view(), name='scenario_create'),
    path('scenarios/<int:pk>/', views.WorkforceScenarioDetailView.as_view(), name='scenario_detail'),
    path('scenarios/<int:pk>/edit/', views.WorkforceScenarioUpdateView.as_view(), name='scenario_edit'),
    path('scenarios/<int:pk>/delete/', views.WorkforceScenarioDeleteView.as_view(), name='scenario_delete'),
    path('scenarios/<int:scenario_pk>/add-detail/', views.ScenarioDetailCreateView.as_view(), name='scenario_detail_create'),
    path('scenario-details/<int:pk>/edit/', views.ScenarioDetailUpdateView.as_view(), name='scenario_detail_edit'),
    path('scenario-details/<int:pk>/delete/', views.ScenarioDetailDeleteView.as_view(), name='scenario_detail_delete'),

    # === Workforce Analytics - Productivity ===
    path('productivity/', views.ProductivityMetricListView.as_view(), name='productivity_list'),
    path('productivity/create/', views.ProductivityMetricCreateView.as_view(), name='productivity_create'),
    path('productivity/<int:pk>/', views.ProductivityMetricDetailView.as_view(), name='productivity_detail'),
    path('productivity/<int:pk>/edit/', views.ProductivityMetricUpdateView.as_view(), name='productivity_edit'),
    path('productivity/<int:pk>/delete/', views.ProductivityMetricDeleteView.as_view(), name='productivity_delete'),

    # === Workforce Analytics - Utilization ===
    path('utilization/', views.UtilizationRateListView.as_view(), name='utilization_list'),
    path('utilization/create/', views.UtilizationRateCreateView.as_view(), name='utilization_create'),
    path('utilization/<int:pk>/', views.UtilizationRateDetailView.as_view(), name='utilization_detail'),
    path('utilization/<int:pk>/edit/', views.UtilizationRateUpdateView.as_view(), name='utilization_edit'),
    path('utilization/<int:pk>/delete/', views.UtilizationRateDeleteView.as_view(), name='utilization_delete'),
]
