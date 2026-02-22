from django.contrib import admin
from .models import (
    Resignation, ExitInterview, ClearanceItem, ClearanceProcess,
    ClearanceChecklistItem, FnFSettlement, ExperienceLetter
)


@admin.register(Resignation)
class ResignationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'resignation_date', 'last_working_day', 'status']
    list_filter = ['status']


@admin.register(ExitInterview)
class ExitInterviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'interviewer', 'scheduled_date', 'status']
    list_filter = ['status']


@admin.register(ClearanceItem)
class ClearanceItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'is_mandatory', 'order']


@admin.register(ClearanceProcess)
class ClearanceProcessAdmin(admin.ModelAdmin):
    list_display = ['employee', 'status', 'initiated_date']
    list_filter = ['status']


@admin.register(FnFSettlement)
class FnFSettlementAdmin(admin.ModelAdmin):
    list_display = ['employee', 'settlement_date', 'status', 'net_payable']
    list_filter = ['status']


@admin.register(ExperienceLetter)
class ExperienceLetterAdmin(admin.ModelAdmin):
    list_display = ['employee', 'letter_type', 'letter_date', 'is_issued']
    list_filter = ['letter_type', 'is_issued']
