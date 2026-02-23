from django.contrib import admin
from .models import (
    JobTemplate, JobRequisition, RequisitionApproval,
    Candidate, JobApplication,
    InterviewRound, Interview, InterviewFeedback,
    OfferLetter,
)


@admin.register(JobTemplate)
class JobTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'tenant', 'is_active', 'created_at']
    list_filter = ['is_active', 'tenant']
    search_fields = ['title']


@admin.register(JobRequisition)
class JobRequisitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'department', 'status', 'priority', 'positions', 'tenant', 'created_at']
    list_filter = ['status', 'priority', 'employment_type', 'tenant']
    search_fields = ['title', 'code']


@admin.register(RequisitionApproval)
class RequisitionApprovalAdmin(admin.ModelAdmin):
    list_display = ['requisition', 'approver', 'level', 'status', 'acted_on']
    list_filter = ['status', 'tenant']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'source', 'tenant', 'created_at']
    list_filter = ['source', 'is_active', 'tenant']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'applied_date', 'source', 'tenant']
    list_filter = ['status', 'source', 'tenant']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'job__title']


@admin.register(InterviewRound)
class InterviewRoundAdmin(admin.ModelAdmin):
    list_display = ['name', 'requisition', 'round_number', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['application', 'round_name', 'scheduled_date', 'mode', 'status', 'result', 'tenant']
    list_filter = ['status', 'mode', 'result', 'tenant']


@admin.register(InterviewFeedback)
class InterviewFeedbackAdmin(admin.ModelAdmin):
    list_display = ['interview', 'interviewer', 'overall_rating', 'recommendation', 'tenant']
    list_filter = ['recommendation', 'tenant']


@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = ['application', 'offered_designation', 'offered_salary', 'status', 'joining_date', 'tenant']
    list_filter = ['status', 'tenant']
