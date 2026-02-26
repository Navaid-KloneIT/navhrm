from django.contrib import admin
from .models import (
    GoalPeriod, Goal, GoalUpdate,
    ReviewCycle, PerformanceReview, ReviewGoalRating,
    PeerReviewer, PeerFeedback,
    Feedback, OneOnOneMeeting, MeetingActionItem,
    PIP, PIPCheckpoint, WarningLetter, CoachingNote,
)


@admin.register(GoalPeriod)
class GoalPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'period_type', 'start_date', 'end_date', 'status', 'tenant']
    list_filter = ['period_type', 'status', 'tenant']
    search_fields = ['name']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'period', 'goal_type', 'weight', 'progress', 'status', 'tenant']
    list_filter = ['goal_type', 'status', 'tenant']
    search_fields = ['title', 'employee__first_name', 'employee__last_name']


@admin.register(GoalUpdate)
class GoalUpdateAdmin(admin.ModelAdmin):
    list_display = ['goal', 'updated_by', 'progress', 'created_at', 'tenant']
    list_filter = ['tenant']


@admin.register(ReviewCycle)
class ReviewCycleAdmin(admin.ModelAdmin):
    list_display = ['name', 'cycle_type', 'status', 'start_date', 'end_date', 'tenant']
    list_filter = ['cycle_type', 'status', 'tenant']
    search_fields = ['name']


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'cycle', 'reviewer', 'status', 'self_rating', 'manager_rating', 'final_rating', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(ReviewGoalRating)
class ReviewGoalRatingAdmin(admin.ModelAdmin):
    list_display = ['review', 'goal', 'self_rating', 'manager_rating', 'tenant']
    list_filter = ['tenant']


@admin.register(PeerReviewer)
class PeerReviewerAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'review', 'status', 'tenant']
    list_filter = ['status', 'tenant']


@admin.register(PeerFeedback)
class PeerFeedbackAdmin(admin.ModelAdmin):
    list_display = ['peer_reviewer', 'rating', 'created_at', 'tenant']
    list_filter = ['tenant']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['from_employee', 'to_employee', 'feedback_type', 'visibility', 'subject', 'tenant', 'created_at']
    list_filter = ['feedback_type', 'visibility', 'tenant']
    search_fields = ['subject']


@admin.register(OneOnOneMeeting)
class OneOnOneMeetingAdmin(admin.ModelAdmin):
    list_display = ['manager', 'employee', 'title', 'scheduled_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['title']


@admin.register(MeetingActionItem)
class MeetingActionItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'meeting', 'assigned_to', 'due_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']


@admin.register(PIP)
class PIPAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'initiated_by', 'start_date', 'end_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['title', 'employee__first_name', 'employee__last_name']


@admin.register(PIPCheckpoint)
class PIPCheckpointAdmin(admin.ModelAdmin):
    list_display = ['pip', 'title', 'due_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']


@admin.register(WarningLetter)
class WarningLetterAdmin(admin.ModelAdmin):
    list_display = ['employee', 'warning_type', 'subject', 'issue_date', 'status', 'tenant']
    list_filter = ['warning_type', 'status', 'tenant']
    search_fields = ['subject', 'employee__first_name', 'employee__last_name']


@admin.register(CoachingNote)
class CoachingNoteAdmin(admin.ModelAdmin):
    list_display = ['employee', 'coach', 'topic', 'session_date', 'tenant']
    list_filter = ['tenant']
    search_fields = ['topic', 'employee__first_name', 'employee__last_name']
