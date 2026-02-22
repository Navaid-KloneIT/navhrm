from django.urls import path
from . import views

app_name = 'organization'

urlpatterns = [
    # Company
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),
    path('companies/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    # Designations
    path('designations/', views.DesignationListView.as_view(), name='designation_list'),
    path('designations/create/', views.DesignationCreateView.as_view(), name='designation_create'),
    path('designations/<int:pk>/edit/', views.DesignationUpdateView.as_view(), name='designation_edit'),
    path('designations/<int:pk>/delete/', views.DesignationDeleteView.as_view(), name='designation_delete'),
    # Org Chart
    path('chart/', views.OrgChartView.as_view(), name='org_chart'),
    # Cost Centers
    path('cost-centers/', views.CostCenterListView.as_view(), name='costcenter_list'),
    path('cost-centers/create/', views.CostCenterCreateView.as_view(), name='costcenter_create'),
    path('cost-centers/<int:pk>/edit/', views.CostCenterUpdateView.as_view(), name='costcenter_edit'),
    path('cost-centers/<int:pk>/delete/', views.CostCenterDeleteView.as_view(), name='costcenter_delete'),
]
