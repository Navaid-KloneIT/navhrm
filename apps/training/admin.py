from django.contrib import admin
from .models import (
    TrainingCategory, TrainingVendor, Training, TrainingSession,
    Course, CourseContent, LearningPath, LearningPathCourse, CourseEnrollment,
    Assessment, AssessmentQuestion, Badge, EmployeeBadge,
    TrainingNomination, TrainingAttendance, TrainingFeedback,
    TrainingCertificate, TrainingBudget,
)


# ===========================================================================
# Training Management Admin
# ===========================================================================

@admin.register(TrainingCategory)
class TrainingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name']


@admin.register(TrainingVendor)
class TrainingVendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'contact_person']


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'training_type', 'status', 'duration_hours', 'cost_per_person', 'tenant']
    list_filter = ['training_type', 'status', 'tenant']
    search_fields = ['title', 'description']


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'training', 'session_date', 'venue', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['title']


# ===========================================================================
# Learning Management Admin
# ===========================================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'course_type', 'difficulty_level', 'is_mandatory', 'is_published', 'tenant']
    list_filter = ['course_type', 'difficulty_level', 'is_published', 'tenant']
    search_fields = ['title']


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'content_type', 'order', 'duration_minutes', 'tenant']
    list_filter = ['content_type', 'tenant']
    search_fields = ['title']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_role', 'target_department', 'is_mandatory', 'is_published', 'tenant']
    list_filter = ['is_published', 'is_mandatory', 'tenant']
    search_fields = ['title']


@admin.register(LearningPathCourse)
class LearningPathCourseAdmin(admin.ModelAdmin):
    list_display = ['learning_path', 'course', 'order', 'is_mandatory', 'tenant']
    list_filter = ['tenant']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'course', 'status', 'progress', 'score', 'enrolled_date', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'course__title']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'assessment_type', 'passing_score', 'is_published', 'tenant']
    list_filter = ['assessment_type', 'is_published', 'tenant']
    search_fields = ['title']


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'question_type', 'points', 'order', 'tenant']
    list_filter = ['question_type', 'tenant']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'points_value', 'tenant']
    list_filter = ['badge_type', 'tenant']
    search_fields = ['name']


@admin.register(EmployeeBadge)
class EmployeeBadgeAdmin(admin.ModelAdmin):
    list_display = ['employee', 'badge', 'earned_date', 'tenant']
    list_filter = ['tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


# ===========================================================================
# Training Administration Admin
# ===========================================================================

@admin.register(TrainingNomination)
class TrainingNominationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'training', 'nominated_by', 'status', 'approved_date', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name', 'training__title']


@admin.register(TrainingAttendance)
class TrainingAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'session', 'status', 'check_in_time', 'check_out_time', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(TrainingFeedback)
class TrainingFeedbackAdmin(admin.ModelAdmin):
    list_display = ['employee', 'training', 'overall_rating', 'would_recommend', 'created_at', 'tenant']
    list_filter = ['overall_rating', 'would_recommend', 'tenant']
    search_fields = ['employee__first_name', 'training__title']


@admin.register(TrainingCertificate)
class TrainingCertificateAdmin(admin.ModelAdmin):
    list_display = ['employee', 'certificate_number', 'training', 'course', 'issue_date', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['certificate_number', 'employee__first_name', 'employee__last_name']


@admin.register(TrainingBudget)
class TrainingBudgetAdmin(admin.ModelAdmin):
    list_display = ['fiscal_year', 'department', 'allocated_amount', 'utilized_amount', 'status', 'tenant']
    list_filter = ['status', 'tenant']
    search_fields = ['fiscal_year']
