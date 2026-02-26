from django.urls import path
from . import views

app_name = 'performance'

urlpatterns = [
    # Goal Periods
    path('periods/', views.GoalPeriodListView.as_view(), name='period_list'),
    path('periods/create/', views.GoalPeriodCreateView.as_view(), name='period_create'),
    path('periods/<int:pk>/edit/', views.GoalPeriodUpdateView.as_view(), name='period_edit'),
    path('periods/<int:pk>/delete/', views.GoalPeriodDeleteView.as_view(), name='period_delete'),

    # Goals
    path('goals/', views.GoalListView.as_view(), name='goal_list'),
    path('goals/create/', views.GoalCreateView.as_view(), name='goal_create'),
    path('goals/<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('goals/<int:pk>/edit/', views.GoalUpdateView.as_view(), name='goal_edit'),
    path('goals/<int:pk>/delete/', views.GoalDeleteView.as_view(), name='goal_delete'),
    path('goals/<int:pk>/update/', views.GoalUpdateCreateView.as_view(), name='goal_update_create'),

    # Review Cycles
    path('cycles/', views.ReviewCycleListView.as_view(), name='cycle_list'),
    path('cycles/create/', views.ReviewCycleCreateView.as_view(), name='cycle_create'),
    path('cycles/<int:pk>/', views.ReviewCycleDetailView.as_view(), name='cycle_detail'),
    path('cycles/<int:pk>/edit/', views.ReviewCycleUpdateView.as_view(), name='cycle_edit'),
    path('cycles/<int:pk>/delete/', views.ReviewCycleDeleteView.as_view(), name='cycle_delete'),

    # Performance Reviews
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('reviews/<int:pk>/self-assessment/', views.SelfAssessmentView.as_view(), name='self_assessment'),
    path('reviews/<int:pk>/manager-review/', views.ManagerReviewView.as_view(), name='manager_review'),
    path('reviews/<int:pk>/assign-peers/', views.PeerReviewerAssignView.as_view(), name='assign_peers'),
    path('reviews/<int:pk>/calibrate/', views.CalibrationView.as_view(), name='calibrate'),

    # Peer Feedback
    path('peer-feedback/<int:pk>/submit/', views.PeerFeedbackCreateView.as_view(), name='peer_feedback_create'),

    # Continuous Feedback
    path('feedback/', views.FeedbackListView.as_view(), name='feedback_list'),
    path('feedback/give/', views.FeedbackCreateView.as_view(), name='feedback_create'),
    path('feedback/<int:pk>/', views.FeedbackDetailView.as_view(), name='feedback_detail'),
    path('feedback/<int:pk>/delete/', views.FeedbackDeleteView.as_view(), name='feedback_delete'),

    # 1:1 Meetings
    path('meetings/', views.MeetingListView.as_view(), name='meeting_list'),
    path('meetings/create/', views.MeetingCreateView.as_view(), name='meeting_create'),
    path('meetings/<int:pk>/', views.MeetingDetailView.as_view(), name='meeting_detail'),
    path('meetings/<int:pk>/edit/', views.MeetingUpdateView.as_view(), name='meeting_edit'),
    path('meetings/<int:pk>/delete/', views.MeetingDeleteView.as_view(), name='meeting_delete'),
    path('meetings/<int:pk>/action-item/', views.ActionItemCreateView.as_view(), name='action_item_create'),
    path('meetings/action-item/<int:pk>/edit/', views.ActionItemUpdateView.as_view(), name='action_item_edit'),

    # PIP
    path('pip/', views.PIPListView.as_view(), name='pip_list'),
    path('pip/create/', views.PIPCreateView.as_view(), name='pip_create'),
    path('pip/<int:pk>/', views.PIPDetailView.as_view(), name='pip_detail'),
    path('pip/<int:pk>/edit/', views.PIPUpdateView.as_view(), name='pip_edit'),
    path('pip/<int:pk>/delete/', views.PIPDeleteView.as_view(), name='pip_delete'),
    path('pip/<int:pk>/checkpoint/', views.PIPCheckpointCreateView.as_view(), name='pip_checkpoint_create'),
    path('pip/checkpoint/<int:pk>/edit/', views.PIPCheckpointUpdateView.as_view(), name='pip_checkpoint_edit'),

    # Warning Letters
    path('warnings/', views.WarningLetterListView.as_view(), name='warning_list'),
    path('warnings/create/', views.WarningLetterCreateView.as_view(), name='warning_create'),
    path('warnings/<int:pk>/', views.WarningLetterDetailView.as_view(), name='warning_detail'),
    path('warnings/<int:pk>/edit/', views.WarningLetterUpdateView.as_view(), name='warning_edit'),
    path('warnings/<int:pk>/delete/', views.WarningLetterDeleteView.as_view(), name='warning_delete'),

    # Coaching Notes
    path('coaching/', views.CoachingNoteListView.as_view(), name='coaching_list'),
    path('coaching/create/', views.CoachingNoteCreateView.as_view(), name='coaching_create'),
    path('coaching/<int:pk>/edit/', views.CoachingNoteUpdateView.as_view(), name='coaching_edit'),
    path('coaching/<int:pk>/delete/', views.CoachingNoteDeleteView.as_view(), name='coaching_delete'),
]
