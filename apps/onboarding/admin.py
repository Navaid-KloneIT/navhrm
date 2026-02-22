from django.contrib import admin
from .models import (
    OnboardingTemplate, OnboardingTemplateTask, OnboardingProcess,
    OnboardingTask, AssetAllocation, OrientationSession, WelcomeKit
)


@admin.register(OnboardingTemplate)
class OnboardingTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'is_active']


@admin.register(OnboardingProcess)
class OnboardingProcessAdmin(admin.ModelAdmin):
    list_display = ['employee', 'status', 'start_date', 'target_completion_date']
    list_filter = ['status']


@admin.register(AssetAllocation)
class AssetAllocationAdmin(admin.ModelAdmin):
    list_display = ['asset_name', 'asset_type', 'employee', 'status', 'allocated_date']
    list_filter = ['asset_type', 'status']


@admin.register(OrientationSession)
class OrientationSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'session_type', 'date', 'facilitator']
    list_filter = ['session_type']


@admin.register(WelcomeKit)
class WelcomeKitAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
