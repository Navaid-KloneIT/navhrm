from django.urls import path
from . import views

app_name = 'additional'

urlpatterns = [
    # === Asset Management ===
    # Asset Categories
    path('assets/categories/', views.AssetCategoryListView.as_view(), name='asset_category_list'),
    path('assets/categories/create/', views.AssetCategoryCreateView.as_view(), name='asset_category_create'),
    path('assets/categories/<int:pk>/edit/', views.AssetCategoryUpdateView.as_view(), name='asset_category_edit'),
    path('assets/categories/<int:pk>/delete/', views.AssetCategoryDeleteView.as_view(), name='asset_category_delete'),

    # Assets
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('assets/<int:pk>/edit/', views.AssetUpdateView.as_view(), name='asset_edit'),
    path('assets/<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),

    # Asset Allocations
    path('assets/allocations/', views.AssetAllocationListView.as_view(), name='asset_allocation_list'),
    path('assets/allocations/create/', views.AssetAllocationCreateView.as_view(), name='asset_allocation_create'),
    path('assets/allocations/<int:pk>/return/', views.AssetReturnView.as_view(), name='asset_return'),

    # Asset Maintenance
    path('assets/maintenance/', views.AssetMaintenanceListView.as_view(), name='asset_maintenance_list'),
    path('assets/maintenance/create/', views.AssetMaintenanceCreateView.as_view(), name='asset_maintenance_create'),
    path('assets/maintenance/<int:pk>/edit/', views.AssetMaintenanceUpdateView.as_view(), name='asset_maintenance_edit'),

    # === Expense Management ===
    # Expense Categories
    path('expenses/categories/', views.ExpenseCategoryListView.as_view(), name='expense_category_list'),
    path('expenses/categories/create/', views.ExpenseCategoryCreateView.as_view(), name='expense_category_create'),
    path('expenses/categories/<int:pk>/edit/', views.ExpenseCategoryUpdateView.as_view(), name='expense_category_edit'),
    path('expenses/categories/<int:pk>/delete/', views.ExpenseCategoryDeleteView.as_view(), name='expense_category_delete'),

    # Expense Policies
    path('expenses/policies/', views.ExpensePolicyListView.as_view(), name='expense_policy_list'),
    path('expenses/policies/create/', views.ExpensePolicyCreateView.as_view(), name='expense_policy_create'),
    path('expenses/policies/<int:pk>/edit/', views.ExpensePolicyUpdateView.as_view(), name='expense_policy_edit'),
    path('expenses/policies/<int:pk>/delete/', views.ExpensePolicyDeleteView.as_view(), name='expense_policy_delete'),

    # Expense Claims
    path('expenses/claims/', views.ExpenseClaimListView.as_view(), name='expense_claim_list'),
    path('expenses/claims/create/', views.ExpenseClaimCreateView.as_view(), name='expense_claim_create'),
    path('expenses/claims/<int:pk>/', views.ExpenseClaimDetailView.as_view(), name='expense_claim_detail'),
    path('expenses/claims/<int:pk>/edit/', views.ExpenseClaimUpdateView.as_view(), name='expense_claim_edit'),
    path('expenses/claims/<int:pk>/delete/', views.ExpenseClaimDeleteView.as_view(), name='expense_claim_delete'),
    path('expenses/claims/<int:pk>/submit/', views.ExpenseClaimSubmitView.as_view(), name='expense_claim_submit'),
    path('expenses/claims/<int:pk>/approve/', views.ExpenseClaimApproveView.as_view(), name='expense_claim_approve'),
    path('expenses/claims/<int:pk>/reject/', views.ExpenseClaimRejectView.as_view(), name='expense_claim_reject'),

    # === Travel Management ===
    # Travel Policies
    path('travel/policies/', views.TravelPolicyListView.as_view(), name='travel_policy_list'),
    path('travel/policies/create/', views.TravelPolicyCreateView.as_view(), name='travel_policy_create'),
    path('travel/policies/<int:pk>/edit/', views.TravelPolicyUpdateView.as_view(), name='travel_policy_edit'),
    path('travel/policies/<int:pk>/delete/', views.TravelPolicyDeleteView.as_view(), name='travel_policy_delete'),

    # Travel Requests
    path('travel/requests/', views.TravelRequestListView.as_view(), name='travel_request_list'),
    path('travel/requests/create/', views.TravelRequestCreateView.as_view(), name='travel_request_create'),
    path('travel/requests/<int:pk>/', views.TravelRequestDetailView.as_view(), name='travel_request_detail'),
    path('travel/requests/<int:pk>/edit/', views.TravelRequestUpdateView.as_view(), name='travel_request_edit'),
    path('travel/requests/<int:pk>/delete/', views.TravelRequestDeleteView.as_view(), name='travel_request_delete'),
    path('travel/requests/<int:pk>/submit/', views.TravelRequestSubmitView.as_view(), name='travel_request_submit'),
    path('travel/requests/<int:pk>/approve/', views.TravelRequestApproveView.as_view(), name='travel_request_approve'),

    # Travel Expenses (inline)
    path('travel/requests/<int:pk>/expense/create/', views.TravelExpenseCreateView.as_view(), name='travel_expense_create'),

    # Travel Settlement
    path('travel/requests/<int:pk>/settlement/', views.TravelSettlementCreateView.as_view(), name='travel_settlement_create'),
    path('travel/settlement/<int:pk>/edit/', views.TravelSettlementUpdateView.as_view(), name='travel_settlement_edit'),

    # === Helpdesk ===
    # Ticket Categories
    path('helpdesk/categories/', views.TicketCategoryListView.as_view(), name='ticket_category_list'),
    path('helpdesk/categories/create/', views.TicketCategoryCreateView.as_view(), name='ticket_category_create'),
    path('helpdesk/categories/<int:pk>/edit/', views.TicketCategoryUpdateView.as_view(), name='ticket_category_edit'),
    path('helpdesk/categories/<int:pk>/delete/', views.TicketCategoryDeleteView.as_view(), name='ticket_category_delete'),

    # Tickets
    path('helpdesk/tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('helpdesk/tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('helpdesk/tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('helpdesk/tickets/<int:pk>/edit/', views.TicketUpdateView.as_view(), name='ticket_edit'),
    path('helpdesk/tickets/<int:pk>/close/', views.TicketCloseView.as_view(), name='ticket_close'),
    path('helpdesk/tickets/<int:pk>/reopen/', views.TicketReopenView.as_view(), name='ticket_reopen'),

    # Ticket Comments (inline)
    path('helpdesk/tickets/<int:pk>/comment/', views.TicketCommentCreateView.as_view(), name='ticket_comment_create'),

    # Knowledge Base
    path('helpdesk/knowledge/', views.KnowledgeBaseListView.as_view(), name='knowledge_base_list'),
    path('helpdesk/knowledge/create/', views.KnowledgeBaseCreateView.as_view(), name='knowledge_base_create'),
    path('helpdesk/knowledge/<int:pk>/', views.KnowledgeBaseDetailView.as_view(), name='knowledge_base_detail'),
    path('helpdesk/knowledge/<int:pk>/edit/', views.KnowledgeBaseUpdateView.as_view(), name='knowledge_base_edit'),
    path('helpdesk/knowledge/<int:pk>/delete/', views.KnowledgeBaseDeleteView.as_view(), name='knowledge_base_delete'),
]
