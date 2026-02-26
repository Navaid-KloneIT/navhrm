from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    # Training Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Training Vendors
    path('vendors/', views.VendorListView.as_view(), name='vendor_list'),
    path('vendors/create/', views.VendorCreateView.as_view(), name='vendor_create'),
    path('vendors/<int:pk>/edit/', views.VendorUpdateView.as_view(), name='vendor_edit'),
    path('vendors/<int:pk>/delete/', views.VendorDeleteView.as_view(), name='vendor_delete'),

    # Trainings
    path('trainings/', views.TrainingListView.as_view(), name='training_list'),
    path('trainings/create/', views.TrainingCreateView.as_view(), name='training_create'),
    path('trainings/<int:pk>/', views.TrainingDetailView.as_view(), name='training_detail'),
    path('trainings/<int:pk>/edit/', views.TrainingUpdateView.as_view(), name='training_edit'),
    path('trainings/<int:pk>/delete/', views.TrainingDeleteView.as_view(), name='training_delete'),
    path('calendar/', views.TrainingCalendarView.as_view(), name='training_calendar'),

    # Training Sessions
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/create/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_edit'),
    path('sessions/<int:pk>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),

    # Courses
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('courses/<int:pk>/content/', views.ContentCreateView.as_view(), name='content_create'),
    path('courses/content/<int:pk>/edit/', views.ContentUpdateView.as_view(), name='content_edit'),
    path('courses/content/<int:pk>/delete/', views.ContentDeleteView.as_view(), name='content_delete'),

    # Learning Paths
    path('learning-paths/', views.PathListView.as_view(), name='path_list'),
    path('learning-paths/create/', views.PathCreateView.as_view(), name='path_create'),
    path('learning-paths/<int:pk>/', views.PathDetailView.as_view(), name='path_detail'),
    path('learning-paths/<int:pk>/edit/', views.PathUpdateView.as_view(), name='path_edit'),
    path('learning-paths/<int:pk>/delete/', views.PathDeleteView.as_view(), name='path_delete'),
    path('learning-paths/<int:pk>/add-course/', views.PathAddCourseView.as_view(), name='path_add_course'),
    path('learning-paths/course/<int:pk>/remove/', views.PathRemoveCourseView.as_view(), name='path_remove_course'),

    # Assessments
    path('assessments/', views.AssessmentListView.as_view(), name='assessment_list'),
    path('assessments/create/', views.AssessmentCreateView.as_view(), name='assessment_create'),
    path('assessments/<int:pk>/', views.AssessmentDetailView.as_view(), name='assessment_detail'),
    path('assessments/<int:pk>/edit/', views.AssessmentUpdateView.as_view(), name='assessment_edit'),
    path('assessments/<int:pk>/delete/', views.AssessmentDeleteView.as_view(), name='assessment_delete'),
    path('assessments/<int:pk>/question/', views.QuestionCreateView.as_view(), name='question_create'),
    path('assessments/question/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question_edit'),
    path('assessments/<int:pk>/take/', views.TakeAssessmentView.as_view(), name='take_assessment'),

    # Enrollments
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/create/', views.EnrollmentCreateView.as_view(), name='enrollment_create'),

    # Badges
    path('badges/', views.BadgeListView.as_view(), name='badge_list'),
    path('badges/create/', views.BadgeCreateView.as_view(), name='badge_create'),
    path('badges/<int:pk>/edit/', views.BadgeUpdateView.as_view(), name='badge_edit'),
    path('badges/<int:pk>/delete/', views.BadgeDeleteView.as_view(), name='badge_delete'),

    # Nominations
    path('nominations/', views.NominationListView.as_view(), name='nomination_list'),
    path('nominations/create/', views.NominationCreateView.as_view(), name='nomination_create'),
    path('nominations/<int:pk>/', views.NominationDetailView.as_view(), name='nomination_detail'),
    path('nominations/<int:pk>/approve/', views.NominationApproveView.as_view(), name='nomination_approve'),
    path('nominations/<int:pk>/reject/', views.NominationRejectView.as_view(), name='nomination_reject'),

    # Training Attendance
    path('attendance/', views.TrainingAttendanceListView.as_view(), name='training_attendance_list'),
    path('attendance/<int:pk>/mark/', views.MarkAttendanceView.as_view(), name='mark_attendance'),

    # Training Feedback
    path('feedback/', views.TrainingFeedbackListView.as_view(), name='training_feedback_list'),
    path('feedback/create/', views.TrainingFeedbackCreateView.as_view(), name='training_feedback_create'),
    path('feedback/<int:pk>/', views.TrainingFeedbackDetailView.as_view(), name='training_feedback_detail'),

    # Certificates
    path('certificates/', views.CertificateListView.as_view(), name='certificate_list'),
    path('certificates/<int:pk>/', views.CertificateDetailView.as_view(), name='certificate_detail'),

    # Budgets
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
]
