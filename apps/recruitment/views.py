from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.db.models import Q, Count
from django.urls import reverse_lazy, reverse
from django.http import Http404

from apps.organization.models import Department
from apps.employees.models import Employee
from .models import (
    JobTemplate, JobRequisition, RequisitionApproval,
    Candidate, JobApplication,
    InterviewRound, Interview, InterviewFeedback,
    OfferLetter,
)
from .forms import (
    JobTemplateForm, JobRequisitionForm,
    CandidateForm, JobApplicationForm, ApplicationStatusForm,
    InterviewForm, InterviewFeedbackForm,
    OfferLetterForm, CareerApplicationForm,
)


# ===========================================================================
# Job Requisition Views
# ===========================================================================

class JobListView(LoginRequiredMixin, ListView):
    model = JobRequisition
    template_name = 'recruitment/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20

    def get_queryset(self):
        qs = JobRequisition.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(code__icontains=search) |
                Q(location__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        department = self.request.GET.get('department', '')
        if department:
            qs = qs.filter(department_id=department)
        return qs.select_related('department', 'designation').annotate(
            app_count=Count('applications')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(tenant=self.request.tenant, is_active=True)
        context['status_choices'] = JobRequisition.STATUS_CHOICES
        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    model = JobRequisition
    form_class = JobRequisitionForm
    template_name = 'recruitment/job_form.html'
    success_url = reverse_lazy('recruitment:job_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Job requisition "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Job Requisition'
        return context


class JobDetailView(LoginRequiredMixin, DetailView):
    model = JobRequisition
    template_name = 'recruitment/job_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        return JobRequisition.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.object.applications.select_related('candidate').all()
        context['approvals'] = self.object.approvals.select_related('approver').all()
        context['interview_rounds'] = self.object.interview_rounds.all()
        return context


class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = JobRequisition
    form_class = JobRequisitionForm
    template_name = 'recruitment/job_form.html'
    success_url = reverse_lazy('recruitment:job_list')

    def get_queryset(self):
        return JobRequisition.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Job requisition "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Job Requisition'
        return context


class JobDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        job = get_object_or_404(JobRequisition, pk=pk, tenant=request.tenant)
        title = job.title
        job.delete()
        messages.success(request, f'Job requisition "{title}" deleted successfully.')
        return redirect('recruitment:job_list')


# ===========================================================================
# Job Template Views
# ===========================================================================

class JobTemplateListView(LoginRequiredMixin, ListView):
    model = JobTemplate
    template_name = 'recruitment/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

    def get_queryset(self):
        qs = JobTemplate.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        return qs


class JobTemplateCreateView(LoginRequiredMixin, CreateView):
    model = JobTemplate
    form_class = JobTemplateForm
    template_name = 'recruitment/template_form.html'
    success_url = reverse_lazy('recruitment:template_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Job template "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Job Template'
        return context


class JobTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = JobTemplate
    form_class = JobTemplateForm
    template_name = 'recruitment/template_form.html'
    success_url = reverse_lazy('recruitment:template_list')

    def get_queryset(self):
        return JobTemplate.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Job template "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Job Template'
        return context


class JobTemplateDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        template = get_object_or_404(JobTemplate, pk=pk, tenant=request.tenant)
        title = template.title
        template.delete()
        messages.success(request, f'Job template "{title}" deleted successfully.')
        return redirect('recruitment:template_list')


# ===========================================================================
# Candidate Views
# ===========================================================================

class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate
    template_name = 'recruitment/candidate_list.html'
    context_object_name = 'candidates'
    paginate_by = 20

    def get_queryset(self):
        qs = Candidate.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(skills__icontains=search) |
                Q(current_company__icontains=search)
            )
        source = self.request.GET.get('source', '')
        if source:
            qs = qs.filter(source=source)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import SOURCE_CHOICES
        context['source_choices'] = SOURCE_CHOICES
        return context


class CandidateCreateView(LoginRequiredMixin, CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'recruitment/candidate_form.html'
    success_url = reverse_lazy('recruitment:candidate_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Candidate "{form.instance.full_name}" added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Candidate'
        return context


class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate
    template_name = 'recruitment/candidate_detail.html'
    context_object_name = 'candidate'

    def get_queryset(self):
        return Candidate.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.object.applications.select_related('job').all()
        return context


class CandidateUpdateView(LoginRequiredMixin, UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'recruitment/candidate_form.html'
    success_url = reverse_lazy('recruitment:candidate_list')

    def get_queryset(self):
        return Candidate.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Candidate "{form.instance.full_name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Candidate'
        return context


class CandidateDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        candidate = get_object_or_404(Candidate, pk=pk, tenant=request.tenant)
        name = candidate.full_name
        candidate.delete()
        messages.success(request, f'Candidate "{name}" deleted successfully.')
        return redirect('recruitment:candidate_list')


# ===========================================================================
# Application Views
# ===========================================================================

class ApplicationListView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'recruitment/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        qs = JobApplication.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(candidate__first_name__icontains=search) |
                Q(candidate__last_name__icontains=search) |
                Q(job__title__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        job = self.request.GET.get('job', '')
        if job:
            qs = qs.filter(job_id=job)
        return qs.select_related('job', 'candidate')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = JobApplication.STATUS_CHOICES
        context['jobs'] = JobRequisition.objects.filter(tenant=self.request.tenant)
        return context


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = JobApplication
    template_name = 'recruitment/application_detail.html'
    context_object_name = 'application'

    def get_queryset(self):
        return JobApplication.objects.filter(tenant=self.request.tenant).select_related('job', 'candidate')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interviews'] = self.object.interviews.all()
        context['offers'] = self.object.offers.all()
        return context


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = JobApplication
    form_class = ApplicationStatusForm
    template_name = 'recruitment/application_edit.html'

    def get_queryset(self):
        return JobApplication.objects.filter(tenant=self.request.tenant)

    def get_success_url(self):
        return reverse('recruitment:application_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Application status updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Application'
        return context


class ApplicationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(JobApplication, pk=pk, tenant=request.tenant)
        application.delete()
        messages.success(request, 'Application deleted successfully.')
        return redirect('recruitment:application_list')


# ===========================================================================
# Interview Views
# ===========================================================================

class InterviewListView(LoginRequiredMixin, ListView):
    model = Interview
    template_name = 'recruitment/interview_list.html'
    context_object_name = 'interviews'
    paginate_by = 20

    def get_queryset(self):
        qs = Interview.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(application__candidate__first_name__icontains=search) |
                Q(application__candidate__last_name__icontains=search) |
                Q(round_name__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('application__candidate', 'application__job')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Interview.STATUS_CHOICES
        return context


class InterviewCreateView(LoginRequiredMixin, CreateView):
    model = Interview
    form_class = InterviewForm
    template_name = 'recruitment/interview_form.html'
    success_url = reverse_lazy('recruitment:interview_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Interview scheduled successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Schedule Interview'
        context['employees'] = Employee.objects.filter(tenant=self.request.tenant, status='active')
        return context


class InterviewDetailView(LoginRequiredMixin, DetailView):
    model = Interview
    template_name = 'recruitment/interview_detail.html'
    context_object_name = 'interview'

    def get_queryset(self):
        return Interview.objects.filter(tenant=self.request.tenant).select_related(
            'application__candidate', 'application__job', 'round'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedbacks'] = self.object.feedbacks.select_related('interviewer').all()
        return context


class InterviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Interview
    form_class = InterviewForm
    template_name = 'recruitment/interview_form.html'

    def get_queryset(self):
        return Interview.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_success_url(self):
        return reverse('recruitment:interview_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Interview updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Interview'
        context['employees'] = Employee.objects.filter(tenant=self.request.tenant, status='active')
        return context


class InterviewDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        interview = get_object_or_404(Interview, pk=pk, tenant=request.tenant)
        interview.delete()
        messages.success(request, 'Interview deleted successfully.')
        return redirect('recruitment:interview_list')


# ===========================================================================
# Interview Feedback Views
# ===========================================================================

class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = InterviewFeedback
    form_class = InterviewFeedbackForm
    template_name = 'recruitment/feedback_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.interview = get_object_or_404(Interview, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.interview = self.interview
        # Assign the current user's employee record as interviewer
        if hasattr(self.request.user, 'employee'):
            form.instance.interviewer = self.request.user.employee
        messages.success(self.request, 'Feedback submitted successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('recruitment:interview_detail', kwargs={'pk': self.interview.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Submit Interview Feedback'
        context['interview'] = self.interview
        return context


class FeedbackUpdateView(LoginRequiredMixin, UpdateView):
    model = InterviewFeedback
    form_class = InterviewFeedbackForm
    template_name = 'recruitment/feedback_form.html'
    pk_url_kwarg = 'fpk'

    def get_queryset(self):
        return InterviewFeedback.objects.filter(tenant=self.request.tenant)

    def get_success_url(self):
        return reverse('recruitment:interview_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, 'Feedback updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Interview Feedback'
        context['interview'] = get_object_or_404(Interview, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context


# ===========================================================================
# Offer Views
# ===========================================================================

class OfferListView(LoginRequiredMixin, ListView):
    model = OfferLetter
    template_name = 'recruitment/offer_list.html'
    context_object_name = 'offers'
    paginate_by = 20

    def get_queryset(self):
        qs = OfferLetter.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(application__candidate__first_name__icontains=search) |
                Q(application__candidate__last_name__icontains=search) |
                Q(offered_designation__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('application__candidate', 'application__job', 'offered_department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = OfferLetter.STATUS_CHOICES
        return context


class OfferCreateView(LoginRequiredMixin, CreateView):
    model = OfferLetter
    form_class = OfferLetterForm
    template_name = 'recruitment/offer_form.html'
    success_url = reverse_lazy('recruitment:offer_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Offer letter created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Offer'
        return context


class OfferDetailView(LoginRequiredMixin, DetailView):
    model = OfferLetter
    template_name = 'recruitment/offer_detail.html'
    context_object_name = 'offer'

    def get_queryset(self):
        return OfferLetter.objects.filter(tenant=self.request.tenant).select_related(
            'application__candidate', 'application__job', 'offered_department', 'approved_by'
        )


class OfferUpdateView(LoginRequiredMixin, UpdateView):
    model = OfferLetter
    form_class = OfferLetterForm
    template_name = 'recruitment/offer_form.html'

    def get_queryset(self):
        return OfferLetter.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_success_url(self):
        return reverse('recruitment:offer_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Offer letter updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Offer'
        return context


class OfferDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        offer = get_object_or_404(OfferLetter, pk=pk, tenant=request.tenant)
        offer.delete()
        messages.success(request, 'Offer letter deleted successfully.')
        return redirect('recruitment:offer_list')


# ===========================================================================
# Public Career Page Views (No Login Required)
# ===========================================================================

class CareerPageView(ListView):
    model = JobRequisition
    template_name = 'recruitment/career_page.html'
    context_object_name = 'jobs'
    paginate_by = 12

    def get_queryset(self):
        qs = JobRequisition.all_objects.filter(is_published=True, status='published')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        employment_type = self.request.GET.get('type', '')
        if employment_type:
            qs = qs.filter(employment_type=employment_type)
        department = self.request.GET.get('department', '')
        if department:
            qs = qs.filter(department_id=department)
        return qs.select_related('department', 'designation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employment_types'] = JobRequisition.EMPLOYMENT_TYPE_CHOICES
        return context


class CareerDetailView(DetailView):
    model = JobRequisition
    template_name = 'recruitment/career_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        return JobRequisition.all_objects.filter(is_published=True, status='published')


class CareerApplyView(FormView):
    template_name = 'recruitment/career_apply.html'
    form_class = CareerApplicationForm

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(
            JobRequisition.all_objects, pk=kwargs['pk'], is_published=True, status='published'
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Get or create candidate
        candidate, created = Candidate.all_objects.get_or_create(
            email=form.cleaned_data['email'],
            tenant=self.job.tenant,
            defaults={
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'phone': form.cleaned_data.get('phone', ''),
                'current_company': form.cleaned_data.get('current_company', ''),
                'experience_years': form.cleaned_data.get('experience_years'),
                'expected_salary': form.cleaned_data.get('expected_salary'),
                'linkedin_url': form.cleaned_data.get('linkedin_url', ''),
                'source': 'career_page',
            }
        )
        if not created:
            # Update candidate info
            candidate.first_name = form.cleaned_data['first_name']
            candidate.last_name = form.cleaned_data['last_name']
            if form.cleaned_data.get('phone'):
                candidate.phone = form.cleaned_data['phone']

        # Handle resume upload on candidate
        if form.cleaned_data.get('resume'):
            candidate.resume = form.cleaned_data['resume']
        candidate.save()

        # Check if already applied
        existing = JobApplication.all_objects.filter(
            job=self.job, candidate=candidate, tenant=self.job.tenant
        ).exists()
        if existing:
            messages.warning(self.request, 'You have already applied for this position.')
            return redirect('recruitment:career_detail', pk=self.job.pk)

        # Create application
        application = JobApplication(
            job=self.job,
            candidate=candidate,
            tenant=self.job.tenant,
            cover_letter=form.cleaned_data.get('cover_letter', ''),
            source='career_page',
        )
        if form.cleaned_data.get('resume'):
            application.resume = form.cleaned_data['resume']
        application.save()

        return redirect('recruitment:career_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.job
        return context


class CareerSuccessView(View):
    def get(self, request):
        from django.shortcuts import render
        return render(request, 'recruitment/career_success.html')
