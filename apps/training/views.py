from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from apps.employees.models import Employee
from .models import (
    TrainingCategory, TrainingVendor, Training, TrainingSession,
    Course, CourseContent, LearningPath, LearningPathCourse, CourseEnrollment,
    Assessment, AssessmentQuestion, Badge, EmployeeBadge,
    TrainingNomination, TrainingAttendance, TrainingFeedback,
    TrainingCertificate, TrainingBudget,
)
from .forms import (
    TrainingCategoryForm, TrainingVendorForm, TrainingForm, TrainingSessionForm,
    CourseForm, CourseContentForm, LearningPathForm, LearningPathCourseForm,
    CourseEnrollmentForm, AssessmentForm, AssessmentQuestionForm, BadgeForm,
    TrainingNominationForm, TrainingAttendanceForm, TrainingFeedbackForm,
    TrainingCertificateForm, TrainingBudgetForm,
)


# ===========================================================================
# Training Category Views
# ===========================================================================

class CategoryListView(LoginRequiredMixin, ListView):
    model = TrainingCategory
    template_name = 'training/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingCategory.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = TrainingCategory
    form_class = TrainingCategoryForm
    template_name = 'training/category_form.html'
    success_url = reverse_lazy('training:category_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Category "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Category'
        return context


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainingCategory
    form_class = TrainingCategoryForm
    template_name = 'training/category_form.html'
    success_url = reverse_lazy('training:category_list')

    def get_queryset(self):
        return TrainingCategory.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Category'
        return context


class CategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(TrainingCategory, pk=pk, tenant=request.tenant)
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully.')
        return redirect('training:category_list')


# ===========================================================================
# Training Vendor Views
# ===========================================================================

class VendorListView(LoginRequiredMixin, ListView):
    model = TrainingVendor
    template_name = 'training/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingVendor.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(contact_person__icontains=search))
        return qs


class VendorCreateView(LoginRequiredMixin, CreateView):
    model = TrainingVendor
    form_class = TrainingVendorForm
    template_name = 'training/vendor_form.html'
    success_url = reverse_lazy('training:vendor_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Vendor "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Vendor'
        return context


class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainingVendor
    form_class = TrainingVendorForm
    template_name = 'training/vendor_form.html'
    success_url = reverse_lazy('training:vendor_list')

    def get_queryset(self):
        return TrainingVendor.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Vendor "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Vendor'
        return context


class VendorDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        vendor = get_object_or_404(TrainingVendor, pk=pk, tenant=request.tenant)
        name = vendor.name
        vendor.delete()
        messages.success(request, f'Vendor "{name}" deleted successfully.')
        return redirect('training:vendor_list')


# ===========================================================================
# Training Views
# ===========================================================================

class TrainingListView(LoginRequiredMixin, ListView):
    model = Training
    template_name = 'training/training_list.html'
    context_object_name = 'trainings'
    paginate_by = 20

    def get_queryset(self):
        qs = Training.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        training_type = self.request.GET.get('training_type', '')
        if training_type:
            qs = qs.filter(training_type=training_type)
        category = self.request.GET.get('category', '')
        if category:
            qs = qs.filter(category_id=category)
        return qs.select_related('category', 'vendor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Training.STATUS_CHOICES
        context['type_choices'] = Training.TRAINING_TYPE_CHOICES
        context['categories'] = TrainingCategory.objects.filter(tenant=self.request.tenant, is_active=True)
        return context


class TrainingCreateView(LoginRequiredMixin, CreateView):
    model = Training
    form_class = TrainingForm
    template_name = 'training/training_form.html'
    success_url = reverse_lazy('training:training_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Training "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Training'
        return context


class TrainingDetailView(LoginRequiredMixin, DetailView):
    model = Training
    template_name = 'training/training_detail.html'
    context_object_name = 'training'

    def get_queryset(self):
        return Training.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = self.object.sessions.select_related('instructor').all()
        context['nominations'] = self.object.nominations.select_related('employee', 'nominated_by').all()[:10]
        context['feedbacks'] = self.object.feedbacks.select_related('employee').all()[:5]
        return context


class TrainingUpdateView(LoginRequiredMixin, UpdateView):
    model = Training
    form_class = TrainingForm
    template_name = 'training/training_form.html'
    success_url = reverse_lazy('training:training_list')

    def get_queryset(self):
        return Training.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Training "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Training'
        return context


class TrainingDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        training = get_object_or_404(Training, pk=pk, tenant=request.tenant)
        title = training.title
        training.delete()
        messages.success(request, f'Training "{title}" deleted successfully.')
        return redirect('training:training_list')


class TrainingCalendarView(LoginRequiredMixin, ListView):
    model = TrainingSession
    template_name = 'training/training_calendar.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return TrainingSession.objects.filter(
            tenant=self.request.tenant
        ).select_related('training', 'instructor').order_by('session_date', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from itertools import groupby
        sessions = list(self.get_queryset())
        grouped = []
        for key, group in groupby(sessions, key=lambda s: s.session_date.strftime('%B %Y')):
            grouped.append({'month_label': key, 'sessions': list(group)})
        context['grouped_sessions'] = grouped
        return context


# ===========================================================================
# Training Session Views
# ===========================================================================

class SessionListView(LoginRequiredMixin, ListView):
    model = TrainingSession
    template_name = 'training/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingSession.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(training__title__icontains=search))
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('training', 'instructor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = TrainingSession.STATUS_CHOICES
        return context


class SessionCreateView(LoginRequiredMixin, CreateView):
    model = TrainingSession
    form_class = TrainingSessionForm
    template_name = 'training/session_form.html'
    success_url = reverse_lazy('training:session_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Session "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Session'
        return context


class SessionDetailView(LoginRequiredMixin, DetailView):
    model = TrainingSession
    template_name = 'training/session_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return TrainingSession.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendance_records'] = self.object.attendance_records.select_related('employee').all()
        context['attendance_form'] = TrainingAttendanceForm(tenant=self.request.tenant)
        return context


class SessionUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainingSession
    form_class = TrainingSessionForm
    template_name = 'training/session_form.html'
    success_url = reverse_lazy('training:session_list')

    def get_queryset(self):
        return TrainingSession.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Session "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Session'
        return context


class SessionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(TrainingSession, pk=pk, tenant=request.tenant)
        title = session.title
        session.delete()
        messages.success(request, f'Session "{title}" deleted successfully.')
        return redirect('training:session_list')


# ===========================================================================
# Course Views
# ===========================================================================

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'training/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20

    def get_queryset(self):
        qs = Course.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        course_type = self.request.GET.get('course_type', '')
        if course_type:
            qs = qs.filter(course_type=course_type)
        difficulty = self.request.GET.get('difficulty', '')
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)
        return qs.select_related('category').annotate(enrollment_count=Count('enrollments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_choices'] = Course.COURSE_TYPE_CHOICES
        context['difficulty_choices'] = Course.DIFFICULTY_CHOICES
        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'training/course_form.html'
    success_url = reverse_lazy('training:course_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Course "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Course'
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'training/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contents'] = self.object.contents.all()
        context['enrollments'] = self.object.enrollments.select_related('employee').all()[:10]
        context['assessments'] = self.object.assessments.all()
        return context


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'training/course_form.html'
    success_url = reverse_lazy('training:course_list')

    def get_queryset(self):
        return Course.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Course "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Course'
        return context


class CourseDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, tenant=request.tenant)
        title = course.title
        course.delete()
        messages.success(request, f'Course "{title}" deleted successfully.')
        return redirect('training:course_list')


class ContentCreateView(LoginRequiredMixin, CreateView):
    model = CourseContent
    form_class = CourseContentForm
    template_name = 'training/content_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.course = self.course
        messages.success(self.request, f'Content "{form.instance.title}" added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('training:course_detail', kwargs={'pk': self.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['title'] = 'Add Content'
        return context


class ContentUpdateView(LoginRequiredMixin, UpdateView):
    model = CourseContent
    form_class = CourseContentForm
    template_name = 'training/content_form.html'

    def get_queryset(self):
        return CourseContent.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Content "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('training:course_detail', kwargs={'pk': self.object.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        context['title'] = 'Edit Content'
        return context


class ContentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        content = get_object_or_404(CourseContent, pk=pk, tenant=request.tenant)
        course_pk = content.course.pk
        content.delete()
        messages.success(request, 'Content deleted successfully.')
        return redirect('training:course_detail', pk=course_pk)


# ===========================================================================
# Learning Path Views
# ===========================================================================

class PathListView(LoginRequiredMixin, ListView):
    model = LearningPath
    template_name = 'training/path_list.html'
    context_object_name = 'paths'
    paginate_by = 20

    def get_queryset(self):
        qs = LearningPath.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(target_role__icontains=search))
        return qs.select_related('target_department').annotate(course_count=Count('path_courses'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PathCreateView(LoginRequiredMixin, CreateView):
    model = LearningPath
    form_class = LearningPathForm
    template_name = 'training/path_form.html'
    success_url = reverse_lazy('training:path_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Learning path "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Learning Path'
        return context


class PathDetailView(LoginRequiredMixin, DetailView):
    model = LearningPath
    template_name = 'training/path_detail.html'
    context_object_name = 'path'

    def get_queryset(self):
        return LearningPath.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['path_courses'] = self.object.path_courses.select_related('course').all()
        return context


class PathUpdateView(LoginRequiredMixin, UpdateView):
    model = LearningPath
    form_class = LearningPathForm
    template_name = 'training/path_form.html'
    success_url = reverse_lazy('training:path_list')

    def get_queryset(self):
        return LearningPath.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Learning path "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Learning Path'
        return context


class PathDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        path = get_object_or_404(LearningPath, pk=pk, tenant=request.tenant)
        title = path.title
        path.delete()
        messages.success(request, f'Learning path "{title}" deleted successfully.')
        return redirect('training:path_list')


class PathAddCourseView(LoginRequiredMixin, CreateView):
    model = LearningPathCourse
    form_class = LearningPathCourseForm
    template_name = 'training/path_add_course_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.learning_path = get_object_or_404(LearningPath, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.learning_path = self.learning_path
        messages.success(self.request, 'Course added to learning path.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('training:path_detail', kwargs={'pk': self.learning_path.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['path'] = self.learning_path
        return context


class PathRemoveCourseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        path_course = get_object_or_404(LearningPathCourse, pk=pk, tenant=request.tenant)
        path_pk = path_course.learning_path.pk
        path_course.delete()
        messages.success(request, 'Course removed from learning path.')
        return redirect('training:path_detail', pk=path_pk)


# ===========================================================================
# Assessment Views
# ===========================================================================

class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'training/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20

    def get_queryset(self):
        qs = Assessment.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search))
        assessment_type = self.request.GET.get('assessment_type', '')
        if assessment_type:
            qs = qs.filter(assessment_type=assessment_type)
        return qs.select_related('course').annotate(question_count=Count('questions'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_choices'] = Assessment.ASSESSMENT_TYPE_CHOICES
        return context


class AssessmentCreateView(LoginRequiredMixin, CreateView):
    model = Assessment
    form_class = AssessmentForm
    template_name = 'training/assessment_form.html'
    success_url = reverse_lazy('training:assessment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Assessment "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Assessment'
        return context


class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'training/assessment_detail.html'
    context_object_name = 'assessment'

    def get_queryset(self):
        return Assessment.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context


class AssessmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assessment
    form_class = AssessmentForm
    template_name = 'training/assessment_form.html'
    success_url = reverse_lazy('training:assessment_list')

    def get_queryset(self):
        return Assessment.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Assessment "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Assessment'
        return context


class AssessmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        assessment = get_object_or_404(Assessment, pk=pk, tenant=request.tenant)
        title = assessment.title
        assessment.delete()
        messages.success(request, f'Assessment "{title}" deleted successfully.')
        return redirect('training:assessment_list')


class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = AssessmentQuestion
    form_class = AssessmentQuestionForm
    template_name = 'training/question_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.assessment = self.assessment
        messages.success(self.request, 'Question added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('training:assessment_detail', kwargs={'pk': self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['title'] = 'Add Question'
        return context


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = AssessmentQuestion
    form_class = AssessmentQuestionForm
    template_name = 'training/question_form.html'

    def get_queryset(self):
        return AssessmentQuestion.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, 'Question updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('training:assessment_detail', kwargs={'pk': self.object.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment'] = self.object.assessment
        context['title'] = 'Edit Question'
        return context


class TakeAssessmentView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'training/take_assessment.html'
    context_object_name = 'assessment'

    def get_queryset(self):
        return Assessment.objects.filter(tenant=self.request.tenant, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context


# ===========================================================================
# Enrollment Views
# ===========================================================================

class EnrollmentListView(LoginRequiredMixin, ListView):
    model = CourseEnrollment
    template_name = 'training/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        qs = CourseEnrollment.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(course__title__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('employee', 'course')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = CourseEnrollment.STATUS_CHOICES
        return context


class EnrollmentCreateView(LoginRequiredMixin, CreateView):
    model = CourseEnrollment
    form_class = CourseEnrollmentForm
    template_name = 'training/enrollment_form.html'
    success_url = reverse_lazy('training:enrollment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Employee enrolled successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Enroll Employee'
        return context


# ===========================================================================
# Badge Views
# ===========================================================================

class BadgeListView(LoginRequiredMixin, ListView):
    model = Badge
    template_name = 'training/badge_list.html'
    context_object_name = 'badges'
    paginate_by = 20

    def get_queryset(self):
        qs = Badge.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.annotate(awarded_count=Count('awarded_to'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_choices'] = Badge.BADGE_TYPE_CHOICES
        return context


class BadgeCreateView(LoginRequiredMixin, CreateView):
    model = Badge
    form_class = BadgeForm
    template_name = 'training/badge_form.html'
    success_url = reverse_lazy('training:badge_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Badge "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Badge'
        return context


class BadgeUpdateView(LoginRequiredMixin, UpdateView):
    model = Badge
    form_class = BadgeForm
    template_name = 'training/badge_form.html'
    success_url = reverse_lazy('training:badge_list')

    def get_queryset(self):
        return Badge.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Badge "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Badge'
        return context


class BadgeDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        badge = get_object_or_404(Badge, pk=pk, tenant=request.tenant)
        name = badge.name
        badge.delete()
        messages.success(request, f'Badge "{name}" deleted successfully.')
        return redirect('training:badge_list')


# ===========================================================================
# Training Nomination Views
# ===========================================================================

class NominationListView(LoginRequiredMixin, ListView):
    model = TrainingNomination
    template_name = 'training/nomination_list.html'
    context_object_name = 'nominations'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingNomination.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(training__title__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('employee', 'training', 'nominated_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = TrainingNomination.STATUS_CHOICES
        return context


class NominationCreateView(LoginRequiredMixin, CreateView):
    model = TrainingNomination
    form_class = TrainingNominationForm
    template_name = 'training/nomination_form.html'
    success_url = reverse_lazy('training:nomination_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        if not form.instance.nominated_by and hasattr(self.request.user, 'employee'):
            form.instance.nominated_by = self.request.user.employee
        messages.success(self.request, 'Nomination submitted successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Nomination'
        return context


class NominationDetailView(LoginRequiredMixin, DetailView):
    model = TrainingNomination
    template_name = 'training/nomination_detail.html'
    context_object_name = 'nomination'

    def get_queryset(self):
        return TrainingNomination.objects.filter(tenant=self.request.tenant)


class NominationApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        nomination = get_object_or_404(TrainingNomination, pk=pk, tenant=request.tenant)
        nomination.status = 'approved'
        nomination.approved_date = timezone.now().date()
        if hasattr(request.user, 'employee'):
            nomination.approved_by = request.user.employee
        nomination.save()
        messages.success(request, f'Nomination for {nomination.employee} approved.')
        return redirect('training:nomination_detail', pk=pk)


class NominationRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        nomination = get_object_or_404(TrainingNomination, pk=pk, tenant=request.tenant)
        nomination.status = 'rejected'
        nomination.rejection_reason = request.POST.get('rejection_reason', '')
        nomination.save()
        messages.success(request, f'Nomination for {nomination.employee} rejected.')
        return redirect('training:nomination_detail', pk=pk)


# ===========================================================================
# Training Attendance Views
# ===========================================================================

class TrainingAttendanceListView(LoginRequiredMixin, ListView):
    model = TrainingAttendance
    template_name = 'training/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingAttendance.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(session__title__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('employee', 'session', 'session__training')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = TrainingAttendance.STATUS_CHOICES
        return context


class MarkAttendanceView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(TrainingSession, pk=pk, tenant=request.tenant)
        form = TrainingAttendanceForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.tenant = request.tenant
            attendance.session = session
            attendance.save()
            messages.success(request, 'Attendance marked successfully.')
        else:
            messages.error(request, 'Failed to mark attendance.')
        return redirect('training:session_detail', pk=session.pk)


# ===========================================================================
# Training Feedback Views
# ===========================================================================

class TrainingFeedbackListView(LoginRequiredMixin, ListView):
    model = TrainingFeedback
    template_name = 'training/feedback_list.html'
    context_object_name = 'feedbacks'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingFeedback.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(training__title__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return qs.select_related('training', 'employee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TrainingFeedbackCreateView(LoginRequiredMixin, CreateView):
    model = TrainingFeedback
    form_class = TrainingFeedbackForm
    template_name = 'training/feedback_form.html'
    success_url = reverse_lazy('training:training_feedback_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Training feedback submitted successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Submit Feedback'
        return context


class TrainingFeedbackDetailView(LoginRequiredMixin, DetailView):
    model = TrainingFeedback
    template_name = 'training/feedback_detail.html'
    context_object_name = 'feedback'

    def get_queryset(self):
        return TrainingFeedback.objects.filter(tenant=self.request.tenant)


# ===========================================================================
# Certificate Views
# ===========================================================================

class CertificateListView(LoginRequiredMixin, ListView):
    model = TrainingCertificate
    template_name = 'training/certificate_list.html'
    context_object_name = 'certificates'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingCertificate.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(certificate_number__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('employee', 'training', 'course')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = TrainingCertificate.STATUS_CHOICES
        return context


class CertificateDetailView(LoginRequiredMixin, DetailView):
    model = TrainingCertificate
    template_name = 'training/certificate_detail.html'
    context_object_name = 'certificate'

    def get_queryset(self):
        return TrainingCertificate.objects.filter(tenant=self.request.tenant)


# ===========================================================================
# Budget Views
# ===========================================================================

class BudgetListView(LoginRequiredMixin, ListView):
    model = TrainingBudget
    template_name = 'training/budget_list.html'
    context_object_name = 'budgets'
    paginate_by = 20

    def get_queryset(self):
        qs = TrainingBudget.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(fiscal_year__icontains=search) | Q(department__name__icontains=search))
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = TrainingBudget.STATUS_CHOICES
        return context


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = TrainingBudget
    form_class = TrainingBudgetForm
    template_name = 'training/budget_form.html'
    success_url = reverse_lazy('training:budget_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Training budget created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Budget'
        return context


class BudgetDetailView(LoginRequiredMixin, DetailView):
    model = TrainingBudget
    template_name = 'training/budget_detail.html'
    context_object_name = 'budget'

    def get_queryset(self):
        return TrainingBudget.objects.filter(tenant=self.request.tenant)


class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainingBudget
    form_class = TrainingBudgetForm
    template_name = 'training/budget_form.html'
    success_url = reverse_lazy('training:budget_list')

    def get_queryset(self):
        return TrainingBudget.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Training budget updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Budget'
        return context


class BudgetDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        budget = get_object_or_404(TrainingBudget, pk=pk, tenant=request.tenant)
        budget.delete()
        messages.success(request, 'Training budget deleted successfully.')
        return redirect('training:budget_list')
