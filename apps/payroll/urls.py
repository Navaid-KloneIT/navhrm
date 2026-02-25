from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    # Dashboard
    path('', views.PayrollDashboardView.as_view(), name='dashboard'),

    # Pay Components
    path('components/', views.PayComponentListView.as_view(), name='component_list'),
    path('components/create/', views.PayComponentCreateView.as_view(), name='component_create'),
    path('components/<int:pk>/edit/', views.PayComponentUpdateView.as_view(), name='component_edit'),

    # Salary Structures
    path('structures/', views.SalaryStructureListView.as_view(), name='structure_list'),
    path('structures/create/', views.SalaryStructureCreateView.as_view(), name='structure_create'),
    path('structures/<int:pk>/', views.SalaryStructureDetailView.as_view(), name='structure_detail'),
    path('structures/<int:pk>/edit/', views.SalaryStructureUpdateView.as_view(), name='structure_edit'),

    # Employee Salary Structures
    path('employee-salary/', views.EmployeeSalaryListView.as_view(), name='employee_salary_list'),
    path('employee-salary/assign/', views.EmployeeSalaryCreateView.as_view(), name='employee_salary_create'),
    path('employee-salary/<int:pk>/', views.EmployeeSalaryDetailView.as_view(), name='employee_salary_detail'),
    path('employee-salary/<int:pk>/edit/', views.EmployeeSalaryUpdateView.as_view(), name='employee_salary_edit'),

    # Payroll Periods
    path('periods/', views.PayrollPeriodListView.as_view(), name='period_list'),
    path('periods/create/', views.PayrollPeriodCreateView.as_view(), name='period_create'),
    path('periods/<int:pk>/', views.PayrollPeriodDetailView.as_view(), name='period_detail'),
    path('periods/<int:pk>/process/', views.PayrollProcessView.as_view(), name='period_process'),
    path('periods/<int:pk>/approve/', views.PayrollApproveView.as_view(), name='period_approve'),

    # Payroll Entries
    path('entries/<int:pk>/', views.PayrollEntryDetailView.as_view(), name='entry_detail'),
    path('entries/<int:pk>/hold/', views.PayrollEntryHoldView.as_view(), name='entry_hold'),

    # Salary Holds
    path('holds/', views.SalaryHoldListView.as_view(), name='hold_list'),
    path('holds/create/', views.SalaryHoldCreateView.as_view(), name='hold_create'),
    path('holds/<int:pk>/release/', views.SalaryHoldReleaseView.as_view(), name='hold_release'),

    # Salary Revisions
    path('revisions/', views.SalaryRevisionListView.as_view(), name='revision_list'),
    path('revisions/create/', views.SalaryRevisionCreateView.as_view(), name='revision_create'),
    path('revisions/<int:pk>/', views.SalaryRevisionDetailView.as_view(), name='revision_detail'),
    path('revisions/<int:pk>/approve/', views.SalaryRevisionApproveView.as_view(), name='revision_approve'),

    # Statutory - PF
    path('statutory/pf/', views.PFConfigListView.as_view(), name='pf_config_list'),
    path('statutory/pf/create/', views.PFConfigCreateView.as_view(), name='pf_config_create'),
    path('statutory/pf/<int:pk>/edit/', views.PFConfigUpdateView.as_view(), name='pf_config_edit'),

    # Statutory - ESI
    path('statutory/esi/', views.ESIConfigListView.as_view(), name='esi_config_list'),
    path('statutory/esi/create/', views.ESIConfigCreateView.as_view(), name='esi_config_create'),
    path('statutory/esi/<int:pk>/edit/', views.ESIConfigUpdateView.as_view(), name='esi_config_edit'),

    # Statutory - Professional Tax
    path('statutory/pt/', views.PTSlabListView.as_view(), name='pt_slab_list'),
    path('statutory/pt/create/', views.PTSlabCreateView.as_view(), name='pt_slab_create'),
    path('statutory/pt/<int:pk>/edit/', views.PTSlabUpdateView.as_view(), name='pt_slab_edit'),

    # Statutory - LWF
    path('statutory/lwf/', views.LWFConfigListView.as_view(), name='lwf_config_list'),
    path('statutory/lwf/create/', views.LWFConfigCreateView.as_view(), name='lwf_config_create'),
    path('statutory/lwf/<int:pk>/edit/', views.LWFConfigUpdateView.as_view(), name='lwf_config_edit'),

    # Statutory Contributions
    path('statutory/contributions/', views.StatutoryContributionListView.as_view(), name='statutory_contribution_list'),

    # Tax Regime
    path('tax/regime/', views.TaxRegimeListView.as_view(), name='tax_regime_list'),
    path('tax/regime/set/', views.TaxRegimeSetView.as_view(), name='tax_regime_set'),

    # Investment Declarations
    path('tax/declarations/', views.InvestmentDeclarationListView.as_view(), name='declaration_list'),
    path('tax/declarations/create/', views.InvestmentDeclarationCreateView.as_view(), name='declaration_create'),
    path('tax/declarations/<int:pk>/', views.InvestmentDeclarationDetailView.as_view(), name='declaration_detail'),
    path('tax/declarations/<int:pk>/verify/', views.InvestmentDeclarationVerifyView.as_view(), name='declaration_verify'),

    # Investment Proofs
    path('tax/declarations/<int:dec_pk>/proofs/upload/', views.InvestmentProofUploadView.as_view(), name='proof_upload'),

    # Tax Computation
    path('tax/computation/', views.TaxComputationListView.as_view(), name='tax_computation_list'),
    path('tax/computation/<int:pk>/', views.TaxComputationDetailView.as_view(), name='tax_computation_detail'),
    path('tax/computation/recalculate/', views.TaxComputationRecalculateView.as_view(), name='tax_computation_recalculate'),

    # Bank Files
    path('bank-files/', views.BankFileListView.as_view(), name='bank_file_list'),
    path('bank-files/generate/', views.BankFileGenerateView.as_view(), name='bank_file_generate'),
    path('bank-files/<int:pk>/', views.BankFileDetailView.as_view(), name='bank_file_detail'),

    # Payslips
    path('payslips/', views.PayslipListView.as_view(), name='payslip_list'),
    path('payslips/<int:pk>/', views.PayslipDetailView.as_view(), name='payslip_detail'),
    path('payslips/<int:pk>/download/', views.PayslipDownloadView.as_view(), name='payslip_download'),
    path('payslips/bulk-generate/', views.PayslipBulkGenerateView.as_view(), name='payslip_bulk_generate'),

    # Payment Register
    path('payment-register/', views.PaymentRegisterListView.as_view(), name='payment_register_list'),
    path('payment-register/<int:pk>/reconcile/', views.PaymentReconcileView.as_view(), name='payment_reconcile'),

    # Reimbursements
    path('reimbursements/', views.ReimbursementListView.as_view(), name='reimbursement_list'),
    path('reimbursements/create/', views.ReimbursementCreateView.as_view(), name='reimbursement_create'),
    path('reimbursements/<int:pk>/', views.ReimbursementDetailView.as_view(), name='reimbursement_detail'),
    path('reimbursements/<int:pk>/approve/', views.ReimbursementApproveView.as_view(), name='reimbursement_approve'),
]
