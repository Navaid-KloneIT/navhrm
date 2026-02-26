from django.urls import path
from . import views

app_name = 'ess'

urlpatterns = [
    # Dashboard
    path('', views.EssDashboardView.as_view(), name='dashboard'),

    # ======================================================================
    # 7.1 Personal Information
    # ======================================================================

    # Profile
    path('profile/', views.MyProfileView.as_view(), name='profile'),
    path('profile/personal/', views.ProfilePersonalEditView.as_view(), name='profile_personal_edit'),
    path('profile/contact/', views.ProfileContactEditView.as_view(), name='profile_contact_edit'),
    path('profile/bank/', views.ProfileBankEditView.as_view(), name='profile_bank_edit'),
    path('profile/avatar/', views.ProfileAvatarEditView.as_view(), name='profile_avatar_edit'),

    # Emergency Contacts
    path('emergency-contacts/', views.EmergencyContactListView.as_view(), name='emergency_contact_list'),
    path('emergency-contacts/create/', views.EmergencyContactCreateView.as_view(), name='emergency_contact_create'),
    path('emergency-contacts/<int:pk>/edit/', views.EmergencyContactEditView.as_view(), name='emergency_contact_edit'),
    path('emergency-contacts/<int:pk>/delete/', views.EmergencyContactDeleteView.as_view(), name='emergency_contact_delete'),

    # Family Members
    path('family/', views.FamilyMemberListView.as_view(), name='family_list'),
    path('family/create/', views.FamilyMemberCreateView.as_view(), name='family_create'),
    path('family/<int:pk>/edit/', views.FamilyMemberEditView.as_view(), name='family_edit'),
    path('family/<int:pk>/delete/', views.FamilyMemberDeleteView.as_view(), name='family_delete'),

    # My Documents
    path('documents/', views.MyDocumentsView.as_view(), name='my_documents'),

    # ======================================================================
    # 7.2 Request Management
    # ======================================================================

    # Leave Requests
    path('leaves/', views.MyLeaveListView.as_view(), name='leave_list'),
    path('leaves/apply/', views.MyLeaveApplyView.as_view(), name='leave_apply'),
    path('leaves/<int:pk>/', views.MyLeaveDetailView.as_view(), name='leave_detail'),
    path('leaves/<int:pk>/cancel/', views.MyLeaveCancelView.as_view(), name='leave_cancel'),

    # Attendance Regularization
    path('regularization/', views.MyRegularizationListView.as_view(), name='regularization_list'),
    path('regularization/create/', views.MyRegularizationCreateView.as_view(), name='regularization_create'),
    path('regularization/<int:pk>/', views.MyRegularizationDetailView.as_view(), name='regularization_detail'),

    # Document Requests
    path('document-requests/', views.DocumentRequestListView.as_view(), name='document_request_list'),
    path('document-requests/create/', views.DocumentRequestCreateView.as_view(), name='document_request_create'),
    path('document-requests/<int:pk>/', views.DocumentRequestDetailView.as_view(), name='document_request_detail'),
    path('document-requests/<int:pk>/cancel/', views.DocumentRequestCancelView.as_view(), name='document_request_cancel'),

    # ID Card Requests
    path('idcard-requests/', views.IDCardRequestListView.as_view(), name='idcard_request_list'),
    path('idcard-requests/create/', views.IDCardRequestCreateView.as_view(), name='idcard_request_create'),
    path('idcard-requests/<int:pk>/', views.IDCardRequestDetailView.as_view(), name='idcard_request_detail'),

    # Asset Requests
    path('asset-requests/', views.AssetRequestListView.as_view(), name='asset_request_list'),
    path('asset-requests/create/', views.AssetRequestCreateView.as_view(), name='asset_request_create'),
    path('asset-requests/<int:pk>/', views.AssetRequestDetailView.as_view(), name='asset_request_detail'),
    path('asset-requests/<int:pk>/cancel/', views.AssetRequestCancelView.as_view(), name='asset_request_cancel'),

    # ======================================================================
    # 7.3 Communication Hub
    # ======================================================================

    # Announcements
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcements/<int:pk>/', views.AnnouncementDetailView.as_view(), name='announcement_detail'),

    # Celebrations (Birthday / Work Anniversary)
    path('celebrations/', views.CelebrationListView.as_view(), name='celebration_list'),
    path('celebrations/<int:pk>/wish/', views.SendWishView.as_view(), name='send_wish'),

    # Surveys
    path('surveys/', views.SurveyListView.as_view(), name='survey_list'),
    path('surveys/create/', views.SurveyCreateView.as_view(), name='survey_create'),
    path('surveys/<int:pk>/', views.SurveyDetailView.as_view(), name='survey_detail'),
    path('surveys/<int:pk>/respond/', views.SurveyRespondView.as_view(), name='survey_respond'),

    # Suggestions
    path('suggestions/', views.SuggestionListView.as_view(), name='suggestion_list'),
    path('suggestions/create/', views.SuggestionCreateView.as_view(), name='suggestion_create'),
    path('suggestions/<int:pk>/', views.SuggestionDetailView.as_view(), name='suggestion_detail'),

    # Help Desk
    path('helpdesk/', views.TicketListView.as_view(), name='ticket_list'),
    path('helpdesk/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('helpdesk/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('helpdesk/<int:pk>/comment/', views.TicketCommentView.as_view(), name='ticket_comment'),
    path('helpdesk/<int:pk>/close/', views.TicketCloseView.as_view(), name='ticket_close'),
]
