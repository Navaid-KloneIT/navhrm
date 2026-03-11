from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.db.models import Q, Max
from django.urls import reverse

from .models import (
    TalentAssessment,
    CriticalPosition, SuccessionCandidate,
    CareerPath, CareerPathStep, EmployeeCareerPlan,
    InternalJobPosting, TransferApplication,
    TalentReviewSession, TalentReviewParticipant,
    FlightRiskAssessment, RetentionPlan, RetentionAction,
)
from .forms import (
    TalentAssessmentForm,
    CriticalPositionForm, SuccessionCandidateForm,
    CareerPathForm, CareerPathStepForm, EmployeeCareerPlanForm,
    InternalJobPostingForm, TransferApplicationForm, TransferApplicationReviewForm,
    TalentReviewSessionForm, TalentReviewParticipantForm, TalentReviewCalibrationForm,
    FlightRiskAssessmentForm, RetentionPlanForm, RetentionActionForm,
)


# ===========================================================================
# Talent Pool Views
# ===========================================================================

class TalentAssessmentListView(LoginRequiredMixin, ListView):
    model = TalentAssessment
    template_name = 'talent/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20

    def get_queryset(self):
        qs = TalentAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'assessed_by')
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if category:
            qs = qs.filter(category=category)
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['category_choices'] = TalentAssessment.CATEGORY_CHOICES
        return context


class TalentAssessmentCreateView(LoginRequiredMixin, CreateView):
    model = TalentAssessment
    form_class = TalentAssessmentForm
    template_name = 'talent/assessment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Talent Assessment'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Talent assessment created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:assessment_detail', kwargs={'pk': self.object.pk})


class TalentAssessmentDetailView(LoginRequiredMixin, DetailView):
    model = TalentAssessment
    template_name = 'talent/assessment_detail.html'
    context_object_name = 'assessment'

    def get_queryset(self):
        return TalentAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'assessed_by')


class TalentAssessmentUpdateView(LoginRequiredMixin, UpdateView):
    model = TalentAssessment
    form_class = TalentAssessmentForm
    template_name = 'talent/assessment_form.html'

    def get_queryset(self):
        return TalentAssessment.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Talent Assessment'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Talent assessment updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:assessment_detail', kwargs={'pk': self.object.pk})


class TalentAssessmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        assessment = get_object_or_404(TalentAssessment, pk=pk, tenant=request.tenant)
        assessment.delete()
        messages.success(request, 'Talent assessment deleted successfully.')
        return redirect('talent:assessment_list')


class NineBoxGridView(LoginRequiredMixin, TemplateView):
    template_name = 'talent/nine_box_grid.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get latest active assessment per employee (MySQL compatible)
        latest_ids = TalentAssessment.objects.filter(
            tenant=self.request.tenant, is_active=True
        ).values('employee').annotate(
            latest_id=Max('id')
        ).values('latest_id')
        assessments = TalentAssessment.objects.filter(
            tenant=self.request.tenant, is_active=True,
            id__in=latest_ids
        ).select_related('employee')
        # Group by grid position
        grid = {}
        for a in assessments:
            key = (a.potential_rating, a.performance_rating)
            grid.setdefault(key, []).append(a)
        context['grid'] = grid
        context['assessments'] = assessments
        context['category_choices'] = TalentAssessment.CATEGORY_CHOICES
        return context


# ===========================================================================
# Succession Planning Views
# ===========================================================================

class CriticalPositionListView(LoginRequiredMixin, ListView):
    model = CriticalPosition
    template_name = 'talent/critical_position_list.html'
    context_object_name = 'positions'
    paginate_by = 20

    def get_queryset(self):
        qs = CriticalPosition.objects.filter(
            tenant=self.request.tenant
        ).select_related('designation', 'department', 'incumbent')
        search = self.request.GET.get('search', '').strip()
        criticality = self.request.GET.get('criticality', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(designation__name__icontains=search) |
                Q(department__name__icontains=search)
            )
        if criticality:
            qs = qs.filter(criticality=criticality)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_criticality'] = self.request.GET.get('criticality', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['criticality_choices'] = CriticalPosition.CRITICALITY_CHOICES
        context['status_choices'] = CriticalPosition.STATUS_CHOICES
        return context


class CriticalPositionCreateView(LoginRequiredMixin, CreateView):
    model = CriticalPosition
    form_class = CriticalPositionForm
    template_name = 'talent/critical_position_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Critical Position'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Critical position created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:critical_position_detail', kwargs={'pk': self.object.pk})


class CriticalPositionDetailView(LoginRequiredMixin, DetailView):
    model = CriticalPosition
    template_name = 'talent/critical_position_detail.html'
    context_object_name = 'position'

    def get_queryset(self):
        return CriticalPosition.objects.filter(
            tenant=self.request.tenant
        ).select_related('designation', 'department', 'incumbent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['successors'] = self.object.successors.select_related('employee').all()
        return context


class CriticalPositionUpdateView(LoginRequiredMixin, UpdateView):
    model = CriticalPosition
    form_class = CriticalPositionForm
    template_name = 'talent/critical_position_form.html'

    def get_queryset(self):
        return CriticalPosition.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Critical Position'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Critical position updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:critical_position_detail', kwargs={'pk': self.object.pk})


class CriticalPositionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        position = get_object_or_404(CriticalPosition, pk=pk, tenant=request.tenant)
        position.delete()
        messages.success(request, 'Critical position deleted successfully.')
        return redirect('talent:critical_position_list')


class SuccessionCandidateCreateView(LoginRequiredMixin, CreateView):
    model = SuccessionCandidate
    form_class = SuccessionCandidateForm
    template_name = 'talent/successor_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Succession Candidate'
        context['position'] = get_object_or_404(
            CriticalPosition, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.critical_position = get_object_or_404(
            CriticalPosition, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        messages.success(self.request, 'Succession candidate added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:critical_position_detail', kwargs={'pk': self.kwargs['pk']})


class SuccessionCandidateUpdateView(LoginRequiredMixin, UpdateView):
    model = SuccessionCandidate
    form_class = SuccessionCandidateForm
    template_name = 'talent/successor_form.html'

    def get_queryset(self):
        return SuccessionCandidate.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Succession Candidate'
        context['position'] = self.object.critical_position
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Succession candidate updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:critical_position_detail', kwargs={'pk': self.object.critical_position.pk})


class SuccessionCandidateDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        candidate = get_object_or_404(SuccessionCandidate, pk=pk, tenant=request.tenant)
        position_pk = candidate.critical_position.pk
        candidate.delete()
        messages.success(request, 'Succession candidate removed successfully.')
        return redirect('talent:critical_position_detail', pk=position_pk)


# ===========================================================================
# Career Pathing Views
# ===========================================================================

class CareerPathListView(LoginRequiredMixin, ListView):
    model = CareerPath
    template_name = 'talent/career_path_list.html'
    context_object_name = 'paths'
    paginate_by = 20

    def get_queryset(self):
        qs = CareerPath.objects.filter(
            tenant=self.request.tenant
        ).select_related('department')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = CareerPath.STATUS_CHOICES
        return context


class CareerPathCreateView(LoginRequiredMixin, CreateView):
    model = CareerPath
    form_class = CareerPathForm
    template_name = 'talent/career_path_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Career Path'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Career path created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:career_path_detail', kwargs={'pk': self.object.pk})


class CareerPathDetailView(LoginRequiredMixin, DetailView):
    model = CareerPath
    template_name = 'talent/career_path_detail.html'
    context_object_name = 'path'

    def get_queryset(self):
        return CareerPath.objects.filter(
            tenant=self.request.tenant
        ).select_related('department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.steps.select_related('designation').order_by('sequence')
        return context


class CareerPathUpdateView(LoginRequiredMixin, UpdateView):
    model = CareerPath
    form_class = CareerPathForm
    template_name = 'talent/career_path_form.html'

    def get_queryset(self):
        return CareerPath.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Career Path'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Career path updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:career_path_detail', kwargs={'pk': self.object.pk})


class CareerPathDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        path = get_object_or_404(CareerPath, pk=pk, tenant=request.tenant)
        path.delete()
        messages.success(request, 'Career path deleted successfully.')
        return redirect('talent:career_path_list')


class CareerPathStepCreateView(LoginRequiredMixin, CreateView):
    model = CareerPathStep
    form_class = CareerPathStepForm
    template_name = 'talent/career_path_step_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Career Path Step'
        context['career_path'] = get_object_or_404(
            CareerPath, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.career_path = get_object_or_404(
            CareerPath, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        messages.success(self.request, 'Career path step added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:career_path_detail', kwargs={'pk': self.kwargs['pk']})


class CareerPathStepUpdateView(LoginRequiredMixin, UpdateView):
    model = CareerPathStep
    form_class = CareerPathStepForm
    template_name = 'talent/career_path_step_form.html'

    def get_queryset(self):
        return CareerPathStep.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Career Path Step'
        context['career_path'] = self.object.career_path
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Career path step updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:career_path_detail', kwargs={'pk': self.object.career_path.pk})


class CareerPathStepDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        step = get_object_or_404(CareerPathStep, pk=pk, tenant=request.tenant)
        path_pk = step.career_path.pk
        step.delete()
        messages.success(request, 'Career path step deleted successfully.')
        return redirect('talent:career_path_detail', pk=path_pk)


class EmployeeCareerPlanListView(LoginRequiredMixin, ListView):
    model = EmployeeCareerPlan
    template_name = 'talent/career_plan_list.html'
    context_object_name = 'plans'
    paginate_by = 20

    def get_queryset(self):
        qs = EmployeeCareerPlan.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'career_path', 'current_step', 'target_step')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(career_path__name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = EmployeeCareerPlan.STATUS_CHOICES
        return context


class EmployeeCareerPlanCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeCareerPlan
    form_class = EmployeeCareerPlanForm
    template_name = 'talent/career_plan_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Employee Career Plan'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Employee career plan created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:career_plan_detail', kwargs={'pk': self.object.pk})


class EmployeeCareerPlanDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeCareerPlan
    template_name = 'talent/career_plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return EmployeeCareerPlan.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'career_path', 'current_step', 'target_step')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.career_path.steps.select_related('designation').order_by('sequence')
        return context


class EmployeeCareerPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeCareerPlan
    form_class = EmployeeCareerPlanForm
    template_name = 'talent/career_plan_form.html'

    def get_queryset(self):
        return EmployeeCareerPlan.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Employee Career Plan'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Employee career plan updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:career_plan_detail', kwargs={'pk': self.object.pk})


class EmployeeCareerPlanDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(EmployeeCareerPlan, pk=pk, tenant=request.tenant)
        plan.delete()
        messages.success(request, 'Employee career plan deleted successfully.')
        return redirect('talent:career_plan_list')


# ===========================================================================
# Internal Mobility Views
# ===========================================================================

class InternalJobPostingListView(LoginRequiredMixin, ListView):
    model = InternalJobPosting
    template_name = 'talent/internal_posting_list.html'
    context_object_name = 'postings'
    paginate_by = 20

    def get_queryset(self):
        qs = InternalJobPosting.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation', 'posted_by')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = InternalJobPosting.STATUS_CHOICES
        return context


class InternalJobPostingCreateView(LoginRequiredMixin, CreateView):
    model = InternalJobPosting
    form_class = InternalJobPostingForm
    template_name = 'talent/internal_posting_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Internal Job Posting'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Internal job posting created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:internal_posting_detail', kwargs={'pk': self.object.pk})


class InternalJobPostingDetailView(LoginRequiredMixin, DetailView):
    model = InternalJobPosting
    template_name = 'talent/internal_posting_detail.html'
    context_object_name = 'posting'

    def get_queryset(self):
        return InternalJobPosting.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation', 'posted_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.object.transfer_applications.select_related(
            'employee', 'current_department', 'current_designation'
        ).all()
        return context


class InternalJobPostingUpdateView(LoginRequiredMixin, UpdateView):
    model = InternalJobPosting
    form_class = InternalJobPostingForm
    template_name = 'talent/internal_posting_form.html'

    def get_queryset(self):
        return InternalJobPosting.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Internal Job Posting'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Internal job posting updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:internal_posting_detail', kwargs={'pk': self.object.pk})


class InternalJobPostingDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        posting = get_object_or_404(InternalJobPosting, pk=pk, tenant=request.tenant)
        posting.delete()
        messages.success(request, 'Internal job posting deleted successfully.')
        return redirect('talent:internal_posting_list')


class TransferApplicationCreateView(LoginRequiredMixin, CreateView):
    model = TransferApplication
    form_class = TransferApplicationForm
    template_name = 'talent/transfer_application_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Apply for Internal Position'
        context['posting'] = get_object_or_404(
            InternalJobPosting, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.posting = get_object_or_404(
            InternalJobPosting, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        messages.success(self.request, 'Transfer application submitted successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:internal_posting_detail', kwargs={'pk': self.kwargs['pk']})


class TransferApplicationListView(LoginRequiredMixin, ListView):
    model = TransferApplication
    template_name = 'talent/transfer_application_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        qs = TransferApplication.objects.filter(
            tenant=self.request.tenant
        ).select_related('posting', 'employee', 'current_department', 'current_designation')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(posting__title__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = TransferApplication.STATUS_CHOICES
        return context


class TransferApplicationDetailView(LoginRequiredMixin, DetailView):
    model = TransferApplication
    template_name = 'talent/transfer_application_detail.html'
    context_object_name = 'application'

    def get_queryset(self):
        return TransferApplication.objects.filter(
            tenant=self.request.tenant
        ).select_related('posting', 'employee', 'current_department', 'current_designation', 'reviewed_by')


class TransferApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = TransferApplication
    form_class = TransferApplicationReviewForm
    template_name = 'talent/transfer_application_form.html'

    def get_queryset(self):
        return TransferApplication.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Review Transfer Application'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Transfer application updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:transfer_application_detail', kwargs={'pk': self.object.pk})


# ===========================================================================
# Talent Review Views
# ===========================================================================

class TalentReviewSessionListView(LoginRequiredMixin, ListView):
    model = TalentReviewSession
    template_name = 'talent/review_session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        qs = TalentReviewSession.objects.filter(
            tenant=self.request.tenant
        ).select_related('facilitator')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = TalentReviewSession.STATUS_CHOICES
        return context


class TalentReviewSessionCreateView(LoginRequiredMixin, CreateView):
    model = TalentReviewSession
    form_class = TalentReviewSessionForm
    template_name = 'talent/review_session_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Talent Review Session'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Talent review session created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:review_session_detail', kwargs={'pk': self.object.pk})


class TalentReviewSessionDetailView(LoginRequiredMixin, DetailView):
    model = TalentReviewSession
    template_name = 'talent/review_session_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return TalentReviewSession.objects.filter(
            tenant=self.request.tenant
        ).select_related('facilitator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participants'] = self.object.participants.select_related('employee').all()
        return context


class TalentReviewSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = TalentReviewSession
    form_class = TalentReviewSessionForm
    template_name = 'talent/review_session_form.html'

    def get_queryset(self):
        return TalentReviewSession.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Talent Review Session'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Talent review session updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:review_session_detail', kwargs={'pk': self.object.pk})


class TalentReviewSessionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(TalentReviewSession, pk=pk, tenant=request.tenant)
        session.delete()
        messages.success(request, 'Talent review session deleted successfully.')
        return redirect('talent:review_session_list')


class TalentReviewParticipantCreateView(LoginRequiredMixin, CreateView):
    model = TalentReviewParticipant
    form_class = TalentReviewParticipantForm
    template_name = 'talent/review_participant_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Review Participant'
        context['session'] = get_object_or_404(
            TalentReviewSession, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.session = get_object_or_404(
            TalentReviewSession, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        messages.success(self.request, 'Review participant added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:review_session_detail', kwargs={'pk': self.kwargs['pk']})


class TalentReviewParticipantUpdateView(LoginRequiredMixin, UpdateView):
    model = TalentReviewParticipant
    form_class = TalentReviewCalibrationForm
    template_name = 'talent/review_participant_form.html'

    def get_queryset(self):
        return TalentReviewParticipant.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Calibrate Participant'
        context['session'] = self.object.session
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Participant calibration updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:review_session_detail', kwargs={'pk': self.object.session.pk})


class TalentReviewParticipantDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        participant = get_object_or_404(TalentReviewParticipant, pk=pk, tenant=request.tenant)
        session_pk = participant.session.pk
        participant.delete()
        messages.success(request, 'Review participant removed successfully.')
        return redirect('talent:review_session_detail', pk=session_pk)


# ===========================================================================
# Retention Strategy Views
# ===========================================================================

class FlightRiskAssessmentListView(LoginRequiredMixin, ListView):
    model = FlightRiskAssessment
    template_name = 'talent/flight_risk_list.html'
    context_object_name = 'assessments'
    paginate_by = 20

    def get_queryset(self):
        qs = FlightRiskAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'assessed_by')
        search = self.request.GET.get('search', '').strip()
        risk_level = self.request.GET.get('risk_level', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if risk_level:
            qs = qs.filter(risk_level=risk_level)
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_risk_level'] = self.request.GET.get('risk_level', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['risk_level_choices'] = FlightRiskAssessment.RISK_LEVEL_CHOICES
        return context


class FlightRiskAssessmentCreateView(LoginRequiredMixin, CreateView):
    model = FlightRiskAssessment
    form_class = FlightRiskAssessmentForm
    template_name = 'talent/flight_risk_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Flight Risk Assessment'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Flight risk assessment created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:flight_risk_detail', kwargs={'pk': self.object.pk})


class FlightRiskAssessmentDetailView(LoginRequiredMixin, DetailView):
    model = FlightRiskAssessment
    template_name = 'talent/flight_risk_detail.html'
    context_object_name = 'assessment'

    def get_queryset(self):
        return FlightRiskAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'assessed_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['retention_plans'] = self.object.retention_plans.select_related(
            'employee', 'responsible_person'
        ).all()
        return context


class FlightRiskAssessmentUpdateView(LoginRequiredMixin, UpdateView):
    model = FlightRiskAssessment
    form_class = FlightRiskAssessmentForm
    template_name = 'talent/flight_risk_form.html'

    def get_queryset(self):
        return FlightRiskAssessment.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Flight Risk Assessment'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Flight risk assessment updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:flight_risk_detail', kwargs={'pk': self.object.pk})


class FlightRiskAssessmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        assessment = get_object_or_404(FlightRiskAssessment, pk=pk, tenant=request.tenant)
        assessment.delete()
        messages.success(request, 'Flight risk assessment deleted successfully.')
        return redirect('talent:flight_risk_list')


class RetentionPlanListView(LoginRequiredMixin, ListView):
    model = RetentionPlan
    template_name = 'talent/retention_plan_list.html'
    context_object_name = 'plans'
    paginate_by = 20

    def get_queryset(self):
        qs = RetentionPlan.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'flight_risk', 'responsible_person')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = RetentionPlan.STATUS_CHOICES
        return context


class RetentionPlanCreateView(LoginRequiredMixin, CreateView):
    model = RetentionPlan
    form_class = RetentionPlanForm
    template_name = 'talent/retention_plan_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Retention Plan'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Retention plan created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:retention_plan_detail', kwargs={'pk': self.object.pk})


class RetentionPlanDetailView(LoginRequiredMixin, DetailView):
    model = RetentionPlan
    template_name = 'talent/retention_plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return RetentionPlan.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'flight_risk', 'responsible_person')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actions'] = self.object.actions.select_related('assigned_to').all()
        return context


class RetentionPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = RetentionPlan
    form_class = RetentionPlanForm
    template_name = 'talent/retention_plan_form.html'

    def get_queryset(self):
        return RetentionPlan.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Retention Plan'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Retention plan updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:retention_plan_detail', kwargs={'pk': self.object.pk})


class RetentionPlanDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(RetentionPlan, pk=pk, tenant=request.tenant)
        plan.delete()
        messages.success(request, 'Retention plan deleted successfully.')
        return redirect('talent:retention_plan_list')


class RetentionActionCreateView(LoginRequiredMixin, CreateView):
    model = RetentionAction
    form_class = RetentionActionForm
    template_name = 'talent/retention_action_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Retention Action'
        context['plan'] = get_object_or_404(
            RetentionPlan, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.retention_plan = get_object_or_404(
            RetentionPlan, pk=self.kwargs['pk'], tenant=self.request.tenant
        )
        messages.success(self.request, 'Retention action added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:retention_plan_detail', kwargs={'pk': self.kwargs['pk']})


class RetentionActionUpdateView(LoginRequiredMixin, UpdateView):
    model = RetentionAction
    form_class = RetentionActionForm
    template_name = 'talent/retention_action_form.html'

    def get_queryset(self):
        return RetentionAction.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Retention Action'
        context['plan'] = self.object.retention_plan
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Retention action updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('talent:retention_plan_detail', kwargs={'pk': self.object.retention_plan.pk})
