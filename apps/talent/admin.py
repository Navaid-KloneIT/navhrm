from django.contrib import admin
from .models import (
    TalentAssessment,
    CriticalPosition, SuccessionCandidate,
    CareerPath, CareerPathStep, EmployeeCareerPlan,
    InternalJobPosting, TransferApplication,
    TalentReviewSession, TalentReviewParticipant,
    FlightRiskAssessment, RetentionPlan, RetentionAction,
)


@admin.register(TalentAssessment)
class TalentAssessmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'performance_rating', 'potential_rating', 'category', 'assessment_date', 'is_active', 'tenant']
    list_filter = ['category', 'is_active', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(CriticalPosition)
class CriticalPositionAdmin(admin.ModelAdmin):
    list_display = ['designation', 'department', 'criticality', 'incumbent', 'status', 'tenant']
    list_filter = ['criticality', 'status', 'tenant']
    search_fields = ['designation__name', 'department__name']


@admin.register(SuccessionCandidate)
class SuccessionCandidateAdmin(admin.ModelAdmin):
    list_display = ['employee', 'critical_position', 'readiness', 'status', 'tenant']
    list_filter = ['readiness', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['name']


@admin.register(CareerPathStep)
class CareerPathStepAdmin(admin.ModelAdmin):
    list_display = ['career_path', 'sequence', 'designation', 'required_experience_years', 'tenant']
    list_filter = ['tenant']
    search_fields = ['career_path__name', 'designation__name']


@admin.register(EmployeeCareerPlan)
class EmployeeCareerPlanAdmin(admin.ModelAdmin):
    list_display = ['employee', 'career_path', 'current_step', 'target_step', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'career_path__name']


@admin.register(InternalJobPosting)
class InternalJobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'designation', 'positions', 'status', 'closing_date', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['title']


@admin.register(TransferApplication)
class TransferApplicationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'posting', 'current_department', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'posting__title']


@admin.register(TalentReviewSession)
class TalentReviewSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'session_date', 'status', 'facilitator', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['name']


@admin.register(TalentReviewParticipant)
class TalentReviewParticipantAdmin(admin.ModelAdmin):
    list_display = ['employee', 'session', 'initial_performance_rating', 'calibrated_performance_rating', 'tenant']
    list_filter = ['tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'session__name']


@admin.register(FlightRiskAssessment)
class FlightRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'risk_level', 'assessed_date', 'assessed_by', 'is_active', 'tenant']
    list_filter = ['risk_level', 'is_active', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(RetentionPlan)
class RetentionPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'responsible_person', 'target_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['title', 'employee__first_name', 'employee__last_name']


@admin.register(RetentionAction)
class RetentionActionAdmin(admin.ModelAdmin):
    list_display = ['description', 'retention_plan', 'assigned_to', 'due_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['description']
