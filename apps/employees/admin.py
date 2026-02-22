from django.contrib import admin
from .models import Employee, EmergencyContact, EmployeeDocument, EmployeeLifecycleEvent


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0


class DocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'email', 'department', 'designation', 'status']
    list_filter = ['status', 'employment_type', 'department']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    inlines = [EmergencyContactInline, DocumentInline]


@admin.register(EmployeeLifecycleEvent)
class LifecycleEventAdmin(admin.ModelAdmin):
    list_display = ['employee', 'event_type', 'event_date', 'processed_by']
    list_filter = ['event_type']
