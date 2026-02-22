from django.contrib import admin
from .models import Company, Location, Department, JobGrade, Designation, CostCenter


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'email']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'city', 'is_headquarters', 'is_active']
    list_filter = ['is_active', 'is_headquarters']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'head', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(JobGrade)
class JobGradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'level', 'min_salary', 'max_salary']
    list_filter = ['level']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'job_grade', 'is_active']
    list_filter = ['is_active', 'department']


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'budget', 'spent', 'is_active']
    list_filter = ['is_active']
