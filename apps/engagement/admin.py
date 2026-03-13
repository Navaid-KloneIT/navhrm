from django.contrib import admin
from .models import (
    EngagementSurvey, EngagementSurveyQuestion, EngagementSurveyQuestionOption, EngagementSurveyResponse,
    EngagementSurveyAnswer, EngagementActionPlan,
    WellbeingProgram, WellbeingResource, WellnessChallenge, ChallengeParticipant,
    FlexibleWorkArrangement, RemoteWorkPolicy, WorkLifeBalanceAssessment,
    EAPProgram, CounselingSession, EAPUtilization,
    CompanyValue, CultureAssessment, CultureAssessmentResponse, ValueNomination,
    TeamEvent, EventParticipant, InterestGroup, InterestGroupMember,
    VolunteerActivity, VolunteerParticipant,
)


# === Engagement Surveys ===

class EngagementSurveyQuestionInline(admin.TabularInline):
    model = EngagementSurveyQuestion
    extra = 1


@admin.register(EngagementSurvey)
class EngagementSurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'survey_type', 'status', 'start_date', 'end_date', 'is_anonymous', 'is_active', 'tenant']
    list_filter = ['survey_type', 'status', 'is_active', 'tenant']
    search_fields = ['title', 'description']
    inlines = [EngagementSurveyQuestionInline]


class EngagementSurveyQuestionOptionInline(admin.TabularInline):
    model = EngagementSurveyQuestionOption
    extra = 1


@admin.register(EngagementSurveyQuestion)
class EngagementSurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'survey', 'question_type', 'order', 'is_required', 'tenant']
    list_filter = ['question_type', 'is_required', 'tenant']
    search_fields = ['question_text']
    inlines = [EngagementSurveyQuestionOptionInline]


@admin.register(EngagementSurveyQuestionOption)
class EngagementSurveyQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['option_text', 'question', 'order', 'tenant']
    list_filter = ['tenant']


@admin.register(EngagementSurveyResponse)
class EngagementSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'employee', 'submitted_at', 'is_complete', 'tenant']
    list_filter = ['is_complete', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(EngagementSurveyAnswer)
class EngagementSurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ['response', 'question', 'rating_value', 'tenant']
    list_filter = ['tenant']


@admin.register(EngagementActionPlan)
class EngagementActionPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'survey', 'assigned_to', 'priority', 'status', 'due_date', 'tenant']
    list_filter = ['priority', 'status', 'tenant']
    search_fields = ['title', 'description']


# === Wellbeing Programs ===

@admin.register(WellbeingProgram)
class WellbeingProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'start_date', 'end_date', 'is_active', 'tenant']
    list_filter = ['category', 'status', 'is_active', 'tenant']
    search_fields = ['name', 'description']


@admin.register(WellbeingResource)
class WellbeingResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'category', 'is_featured', 'is_active', 'tenant']
    list_filter = ['resource_type', 'category', 'is_featured', 'is_active', 'tenant']
    search_fields = ['title', 'description']


@admin.register(WellnessChallenge)
class WellnessChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'challenge_type', 'start_date', 'end_date', 'status', 'is_active', 'tenant']
    list_filter = ['challenge_type', 'status', 'is_active', 'tenant']
    search_fields = ['title', 'description']


@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ['employee', 'challenge', 'progress', 'joined_at', 'completed_at', 'tenant']
    list_filter = ['tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


# === Work-Life Balance ===

@admin.register(FlexibleWorkArrangement)
class FlexibleWorkArrangementAdmin(admin.ModelAdmin):
    list_display = ['employee', 'arrangement_type', 'status', 'start_date', 'end_date', 'is_active', 'tenant']
    list_filter = ['arrangement_type', 'status', 'is_active', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(RemoteWorkPolicy)
class RemoteWorkPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'description']


@admin.register(WorkLifeBalanceAssessment)
class WorkLifeBalanceAssessmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'assessment_date', 'work_satisfaction', 'life_satisfaction', 'stress_level', 'overall_score', 'tenant']
    list_filter = ['tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


# === Employee Assistance ===

@admin.register(EAPProgram)
class EAPProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'provider', 'is_active', 'tenant']
    list_filter = ['service_type', 'is_active', 'tenant']
    search_fields = ['name', 'provider']


@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'program', 'session_type', 'session_date', 'status', 'tenant']
    list_filter = ['session_type', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'counselor_name']


@admin.register(EAPUtilization)
class EAPUtilizationAdmin(admin.ModelAdmin):
    list_display = ['program', 'period_start', 'period_end', 'total_sessions', 'total_participants', 'satisfaction_score', 'tenant']
    list_filter = ['tenant']


# === Culture & Values ===

@admin.register(CompanyValue)
class CompanyValueAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name']


@admin.register(CultureAssessment)
class CultureAssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'assessment_date', 'status', 'created_by', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['title']


@admin.register(CultureAssessmentResponse)
class CultureAssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'employee', 'alignment_score', 'submitted_at', 'tenant']
    list_filter = ['tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(ValueNomination)
class ValueNominationAdmin(admin.ModelAdmin):
    list_display = ['nominee', 'value', 'nominated_by', 'status', 'is_featured', 'tenant']
    list_filter = ['status', 'is_featured', 'tenant']
    search_fields = ['nominee__first_name', 'nominee__last_name']


# === Social Connect ===

@admin.register(TeamEvent)
class TeamEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'location', 'status', 'is_active', 'tenant']
    list_filter = ['event_type', 'status', 'is_active', 'tenant']
    search_fields = ['title', 'location']


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['employee', 'event', 'rsvp_status', 'attended', 'tenant']
    list_filter = ['rsvp_status', 'attended', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(InterestGroup)
class InterestGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_by', 'is_active', 'tenant']
    list_filter = ['category', 'is_active', 'tenant']
    search_fields = ['name']


@admin.register(InterestGroupMember)
class InterestGroupMemberAdmin(admin.ModelAdmin):
    list_display = ['employee', 'group', 'role', 'joined_at', 'tenant']
    list_filter = ['role', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(VolunteerActivity)
class VolunteerActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'activity_date', 'location', 'status', 'is_active', 'tenant']
    list_filter = ['status', 'is_active', 'tenant']
    search_fields = ['title', 'location']


@admin.register(VolunteerParticipant)
class VolunteerParticipantAdmin(admin.ModelAdmin):
    list_display = ['employee', 'activity', 'hours_contributed', 'tenant']
    list_filter = ['tenant']
    search_fields = ['employee__first_name', 'employee__last_name']
