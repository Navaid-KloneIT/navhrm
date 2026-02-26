from django.contrib import admin
from .models import (
    FamilyMember, DocumentRequest, IDCardRequest, AssetRequest,
    Announcement, BirthdayWish, Survey, SurveyQuestion, SurveyResponse,
    Suggestion, HelpDeskTicket, TicketComment,
)


# ===========================================================================
# Personal Information
# ===========================================================================

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee', 'relationship', 'is_dependent', 'is_nominee', 'tenant']
    list_filter = ['relationship', 'is_dependent', 'tenant']
    search_fields = ['name', 'employee__first_name', 'employee__last_name']


# ===========================================================================
# Request Management
# ===========================================================================

@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'status', 'delivery_method', 'created_at', 'tenant']
    list_filter = ['document_type', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(IDCardRequest)
class IDCardRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'request_type', 'status', 'created_at', 'tenant']
    list_filter = ['request_type', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(AssetRequest)
class AssetRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'asset_type', 'asset_name', 'priority', 'status', 'created_at', 'tenant']
    list_filter = ['asset_type', 'priority', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'asset_name']


# ===========================================================================
# Communication Hub
# ===========================================================================

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'publish_date', 'is_pinned', 'is_active', 'tenant']
    list_filter = ['category', 'priority', 'is_active', 'tenant']
    search_fields = ['title', 'content']


@admin.register(BirthdayWish)
class BirthdayWishAdmin(admin.ModelAdmin):
    list_display = ['employee', 'wished_by', 'occasion', 'occasion_date', 'tenant']
    list_filter = ['occasion', 'tenant']
    search_fields = ['employee__first_name', 'wished_by__first_name']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'start_date', 'end_date', 'is_anonymous', 'tenant']
    list_filter = ['status', 'is_anonymous', 'tenant']
    search_fields = ['title']


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'question_type', 'order', 'is_required', 'tenant']
    list_filter = ['question_type', 'tenant']


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'respondent', 'question', 'created_at', 'tenant']
    list_filter = ['tenant']
    search_fields = ['respondent__first_name', 'respondent__last_name']


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'category', 'status', 'is_anonymous', 'upvotes', 'created_at', 'tenant']
    list_filter = ['category', 'status', 'tenant']
    search_fields = ['title', 'description']


@admin.register(HelpDeskTicket)
class HelpDeskTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'subject', 'employee', 'category', 'priority', 'status', 'created_at', 'tenant']
    list_filter = ['category', 'priority', 'status', 'tenant']
    search_fields = ['ticket_number', 'subject', 'employee__first_name']


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'is_internal', 'created_at', 'tenant']
    list_filter = ['is_internal', 'tenant']
    search_fields = ['ticket__ticket_number', 'message']
