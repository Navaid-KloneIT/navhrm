from django.contrib import admin
from .models import (
    LaborLaw, LaborLawCompliance,
    EmploymentContract, ContractAmendment,
    CompliancePolicy, PolicyVersion, PolicyAcknowledgment,
    DisciplinaryIncident, WarningRecord, DisciplinaryAppeal,
    Grievance, GrievanceInvestigation,
    MusterRoll, WageRegister, InspectionReport,
)


@admin.register(LaborLaw)
class LaborLawAdmin(admin.ModelAdmin):
    list_display = ['name', 'jurisdiction', 'category', 'status', 'effective_date', 'tenant']
    list_filter = ['category', 'status', 'tenant']
    search_fields = ['name', 'jurisdiction']


@admin.register(LaborLawCompliance)
class LaborLawComplianceAdmin(admin.ModelAdmin):
    list_display = ['labor_law', 'department', 'compliance_status', 'review_date', 'responsible_person', 'tenant']
    list_filter = ['compliance_status', 'tenant']
    search_fields = ['labor_law__name']


@admin.register(EmploymentContract)
class EmploymentContractAdmin(admin.ModelAdmin):
    list_display = ['employee', 'contract_type', 'start_date', 'end_date', 'status', 'tenant']
    list_filter = ['contract_type', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'contract_number']


@admin.register(ContractAmendment)
class ContractAmendmentAdmin(admin.ModelAdmin):
    list_display = ['contract', 'amendment_type', 'amendment_date', 'effective_date', 'status', 'tenant']
    list_filter = ['amendment_type', 'status', 'tenant']
    search_fields = ['contract__employee__first_name', 'contract__employee__last_name']


@admin.register(CompliancePolicy)
class CompliancePolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'version', 'status', 'effective_date', 'tenant']
    list_filter = ['category', 'status', 'tenant']
    search_fields = ['title']


@admin.register(PolicyVersion)
class PolicyVersionAdmin(admin.ModelAdmin):
    list_display = ['policy', 'version_number', 'effective_date', 'created_by', 'tenant']
    list_filter = ['tenant']
    search_fields = ['policy__title', 'version_number']


@admin.register(PolicyAcknowledgment)
class PolicyAcknowledgmentAdmin(admin.ModelAdmin):
    list_display = ['policy', 'employee', 'is_acknowledged', 'acknowledged_date', 'tenant']
    list_filter = ['is_acknowledged', 'tenant']
    search_fields = ['policy__title', 'employee__first_name', 'employee__last_name']


@admin.register(DisciplinaryIncident)
class DisciplinaryIncidentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'incident_type', 'severity', 'incident_date', 'status', 'tenant']
    list_filter = ['incident_type', 'severity', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(WarningRecord)
class WarningRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'warning_type', 'issued_date', 'issued_by', 'status', 'tenant']
    list_filter = ['warning_type', 'status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(DisciplinaryAppeal)
class DisciplinaryAppealAdmin(admin.ModelAdmin):
    list_display = ['employee', 'warning', 'appeal_date', 'decision', 'reviewed_by', 'tenant']
    list_filter = ['decision', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ['subject', 'employee', 'category', 'priority', 'status', 'grievance_date', 'tenant']
    list_filter = ['category', 'priority', 'status', 'tenant']
    search_fields = ['subject', 'employee__first_name', 'employee__last_name']


@admin.register(GrievanceInvestigation)
class GrievanceInvestigationAdmin(admin.ModelAdmin):
    list_display = ['grievance', 'investigator', 'start_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['grievance__subject']


@admin.register(MusterRoll)
class MusterRollAdmin(admin.ModelAdmin):
    list_display = ['month', 'year', 'department', 'total_employees', 'total_working_days', 'status', 'tenant']
    list_filter = ['status', 'year', 'tenant']
    search_fields = ['department__name']


@admin.register(WageRegister)
class WageRegisterAdmin(admin.ModelAdmin):
    list_display = ['month', 'year', 'department', 'total_gross', 'total_net', 'status', 'tenant']
    list_filter = ['status', 'year', 'tenant']
    search_fields = ['department__name']


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = ['inspection_date', 'inspector_name', 'inspection_type', 'compliance_status', 'status', 'tenant']
    list_filter = ['inspection_type', 'compliance_status', 'status', 'tenant']
    search_fields = ['inspector_name', 'areas_inspected']
