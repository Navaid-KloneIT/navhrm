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
    GoalPeriod, Goal, GoalUpdate,
    ReviewCycle, PerformanceReview, ReviewGoalRating,
    PeerReviewer, PeerFeedback,
    Feedback, OneOnOneMeeting, MeetingActionItem,
    PIP, PIPCheckpoint, WarningLetter, CoachingNote,
)
from .forms import (
    GoalPeriodForm, GoalForm, GoalUpdateForm,
    ReviewCycleForm, PerformanceReviewForm, SelfAssessmentForm,
    ManagerReviewForm, PeerReviewerForm, PeerFeedbackForm, CalibrationForm,
    FeedbackForm, MeetingForm, MeetingActionItemForm,
    PIPForm, PIPCheckpointForm, WarningLetterForm, CoachingNoteForm,
)


# ===========================================================================
# Goal Period Views
# ===========================================================================

class GoalPeriodListView(LoginRequiredMixin, ListView):
    model = GoalPeriod
    template_name = 'performance/period_list.html'
    context_object_name = 'periods'
    paginate_by = 20

    def get_queryset(self):
        qs = GoalPeriod.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        period_type = self.request.GET.get('period_type', '')
        if period_type:
            qs = qs.filter(period_type=period_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = GoalPeriod.STATUS_CHOICES
        context['period_type_choices'] = GoalPeriod.PERIOD_TYPE_CHOICES
        return context


class GoalPeriodCreateView(LoginRequiredMixin, CreateView):
    model = GoalPeriod
    form_class = GoalPeriodForm
    template_name = 'performance/period_form.html'
    success_url = reverse_lazy('performance:period_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Goal period "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Goal Period'
        return context


class GoalPeriodUpdateView(LoginRequiredMixin, UpdateView):
    model = GoalPeriod
    form_class = GoalPeriodForm
    template_name = 'performance/period_form.html'
    success_url = reverse_lazy('performance:period_list')

    def get_queryset(self):
        return GoalPeriod.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Goal period "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Goal Period'
        return context


class GoalPeriodDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        period = get_object_or_404(GoalPeriod, pk=pk, tenant=request.tenant)
        name = period.name
        period.delete()
        messages.success(request, f'Goal period "{name}" deleted successfully.')
        return redirect('performance:period_list')


# ===========================================================================
# Goal Views
# ===========================================================================

class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'performance/goal_list.html'
    context_object_name = 'goals'
    paginate_by = 20

    def get_queryset(self):
        qs = Goal.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        goal_type = self.request.GET.get('goal_type', '')
        if goal_type:
            qs = qs.filter(goal_type=goal_type)
        period = self.request.GET.get('period', '')
        if period:
            qs = qs.filter(period_id=period)
        employee = self.request.GET.get('employee', '')
        if employee:
            qs = qs.filter(employee_id=employee)
        return qs.select_related('employee', 'period')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Goal.STATUS_CHOICES
        context['goal_type_choices'] = Goal.GOAL_TYPE_CHOICES
        context['periods'] = GoalPeriod.objects.filter(tenant=self.request.tenant)
        context['employees'] = Employee.objects.filter(tenant=self.request.tenant, status='active')
        return context


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'performance/goal_form.html'
    success_url = reverse_lazy('performance:goal_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Goal "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Goal'
        return context


class GoalDetailView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'performance/goal_detail.html'
    context_object_name = 'goal'

    def get_queryset(self):
        return Goal.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.select_related('updated_by').all()
        context['child_goals'] = self.object.child_goals.select_related('employee').all()
        return context


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    template_name = 'performance/goal_form.html'
    success_url = reverse_lazy('performance:goal_list')

    def get_queryset(self):
        return Goal.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Goal "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Goal'
        return context


class GoalDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        goal = get_object_or_404(Goal, pk=pk, tenant=request.tenant)
        title = goal.title
        goal.delete()
        messages.success(request, f'Goal "{title}" deleted successfully.')
        return redirect('performance:goal_list')


class GoalUpdateCreateView(LoginRequiredMixin, CreateView):
    model = GoalUpdate
    form_class = GoalUpdateForm
    template_name = 'performance/goal_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.goal = get_object_or_404(Goal, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.goal = self.goal
        if hasattr(self.request.user, 'employee'):
            form.instance.updated_by = self.request.user.employee
        # Update goal progress
        self.goal.progress = form.instance.progress
        if form.instance.current_value:
            self.goal.current_value = form.instance.current_value
        self.goal.save()
        messages.success(self.request, 'Goal progress updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:goal_detail', kwargs={'pk': self.goal.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goal'] = self.goal
        return context


# ===========================================================================
# Review Cycle Views
# ===========================================================================

class ReviewCycleListView(LoginRequiredMixin, ListView):
    model = ReviewCycle
    template_name = 'performance/cycle_list.html'
    context_object_name = 'cycles'
    paginate_by = 20

    def get_queryset(self):
        qs = ReviewCycle.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        cycle_type = self.request.GET.get('cycle_type', '')
        if cycle_type:
            qs = qs.filter(cycle_type=cycle_type)
        return qs.annotate(review_count=Count('reviews'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ReviewCycle.STATUS_CHOICES
        context['cycle_type_choices'] = ReviewCycle.CYCLE_TYPE_CHOICES
        return context


class ReviewCycleCreateView(LoginRequiredMixin, CreateView):
    model = ReviewCycle
    form_class = ReviewCycleForm
    template_name = 'performance/cycle_form.html'
    success_url = reverse_lazy('performance:cycle_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Review cycle "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Review Cycle'
        return context


class ReviewCycleDetailView(LoginRequiredMixin, DetailView):
    model = ReviewCycle
    template_name = 'performance/cycle_detail.html'
    context_object_name = 'cycle'

    def get_queryset(self):
        return ReviewCycle.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.select_related('employee', 'reviewer').all()
        return context


class ReviewCycleUpdateView(LoginRequiredMixin, UpdateView):
    model = ReviewCycle
    form_class = ReviewCycleForm
    template_name = 'performance/cycle_form.html'
    success_url = reverse_lazy('performance:cycle_list')

    def get_queryset(self):
        return ReviewCycle.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Review cycle "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Review Cycle'
        return context


class ReviewCycleDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cycle = get_object_or_404(ReviewCycle, pk=pk, tenant=request.tenant)
        name = cycle.name
        cycle.delete()
        messages.success(request, f'Review cycle "{name}" deleted successfully.')
        return redirect('performance:cycle_list')


# ===========================================================================
# Performance Review Views
# ===========================================================================

class ReviewListView(LoginRequiredMixin, ListView):
    model = PerformanceReview
    template_name = 'performance/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 20

    def get_queryset(self):
        qs = PerformanceReview.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        cycle = self.request.GET.get('cycle', '')
        if cycle:
            qs = qs.filter(cycle_id=cycle)
        return qs.select_related('employee', 'reviewer', 'cycle')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PerformanceReview.STATUS_CHOICES
        context['cycles'] = ReviewCycle.objects.filter(tenant=self.request.tenant)
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = PerformanceReview
    form_class = PerformanceReviewForm
    template_name = 'performance/review_form.html'
    success_url = reverse_lazy('performance:review_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Performance review created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Performance Review'
        return context


class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = PerformanceReview
    template_name = 'performance/review_detail.html'
    context_object_name = 'review'

    def get_queryset(self):
        return PerformanceReview.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goal_ratings'] = self.object.goal_ratings.select_related('goal').all()
        context['peer_reviewers'] = self.object.peer_reviewers.select_related('reviewer').all()
        return context


class SelfAssessmentView(LoginRequiredMixin, UpdateView):
    model = PerformanceReview
    form_class = SelfAssessmentForm
    template_name = 'performance/self_assessment_form.html'

    def get_queryset(self):
        return PerformanceReview.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get goals for this employee in the review's period
        if self.object.cycle.period:
            context['goals'] = Goal.objects.filter(
                tenant=self.request.tenant,
                employee=self.object.employee,
                period=self.object.cycle.period,
            )
        else:
            context['goals'] = Goal.objects.none()
        context['goal_ratings'] = {
            gr.goal_id: gr for gr in self.object.goal_ratings.all()
        }
        return context

    def form_valid(self, form):
        form.instance.status = 'self_assessment'
        form.instance.submitted_at = timezone.now()
        # Save per-goal self ratings from POST data
        for key, value in self.request.POST.items():
            if key.startswith('goal_self_rating_'):
                goal_id = key.replace('goal_self_rating_', '')
                comment_key = f'goal_self_comment_{goal_id}'
                comment = self.request.POST.get(comment_key, '')
                ReviewGoalRating.objects.update_or_create(
                    tenant=self.request.tenant,
                    review=self.object,
                    goal_id=goal_id,
                    defaults={
                        'self_rating': value or None,
                        'self_comments': comment,
                    }
                )
        messages.success(self.request, 'Self assessment submitted successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:review_detail', kwargs={'pk': self.object.pk})


class ManagerReviewView(LoginRequiredMixin, UpdateView):
    model = PerformanceReview
    form_class = ManagerReviewForm
    template_name = 'performance/manager_review_form.html'

    def get_queryset(self):
        return PerformanceReview.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goal_ratings'] = self.object.goal_ratings.select_related('goal').all()
        return context

    def form_valid(self, form):
        form.instance.status = 'manager_review'
        form.instance.reviewed_at = timezone.now()
        # Save per-goal manager ratings from POST data
        for key, value in self.request.POST.items():
            if key.startswith('goal_mgr_rating_'):
                goal_id = key.replace('goal_mgr_rating_', '')
                comment_key = f'goal_mgr_comment_{goal_id}'
                comment = self.request.POST.get(comment_key, '')
                ReviewGoalRating.objects.update_or_create(
                    tenant=self.request.tenant,
                    review=self.object,
                    goal_id=goal_id,
                    defaults={
                        'manager_rating': value or None,
                        'manager_comments': comment,
                    }
                )
        messages.success(self.request, 'Manager review submitted successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:review_detail', kwargs={'pk': self.object.pk})


class PeerReviewerAssignView(LoginRequiredMixin, CreateView):
    model = PeerReviewer
    form_class = PeerReviewerForm
    template_name = 'performance/peer_assign_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.review = get_object_or_404(PerformanceReview, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.review = self.review
        if hasattr(self.request.user, 'employee'):
            form.instance.assigned_by = self.request.user.employee
        messages.success(self.request, f'Peer reviewer assigned successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:review_detail', kwargs={'pk': self.review.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review'] = self.review
        context['existing_peers'] = self.review.peer_reviewers.select_related('reviewer').all()
        return context


class PeerFeedbackCreateView(LoginRequiredMixin, CreateView):
    model = PeerFeedback
    form_class = PeerFeedbackForm
    template_name = 'performance/peer_feedback_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.peer_reviewer = get_object_or_404(PeerReviewer, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.peer_reviewer = self.peer_reviewer
        self.peer_reviewer.status = 'completed'
        self.peer_reviewer.save()
        messages.success(self.request, 'Peer feedback submitted successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:review_detail', kwargs={'pk': self.peer_reviewer.review.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['peer_reviewer'] = self.peer_reviewer
        context['review'] = self.peer_reviewer.review
        return context


class CalibrationView(LoginRequiredMixin, UpdateView):
    model = PerformanceReview
    form_class = CalibrationForm
    template_name = 'performance/calibration_form.html'

    def get_queryset(self):
        return PerformanceReview.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        form.instance.status = 'completed'
        if hasattr(self.request.user, 'employee'):
            form.instance.calibrated_by = self.request.user.employee
        form.instance.calibrated_at = timezone.now()
        messages.success(self.request, 'Review calibrated and completed successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:review_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goal_ratings'] = self.object.goal_ratings.select_related('goal').all()
        return context


# ===========================================================================
# Continuous Feedback Views
# ===========================================================================

class FeedbackListView(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'performance/feedback_list.html'
    context_object_name = 'feedbacks'
    paginate_by = 20

    def get_queryset(self):
        qs = Feedback.objects.filter(tenant=self.request.tenant)
        tab = self.request.GET.get('tab', 'received')
        if hasattr(self.request.user, 'employee'):
            emp = self.request.user.employee
            if tab == 'given':
                qs = qs.filter(from_employee=emp)
            else:
                qs = qs.filter(to_employee=emp)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(subject__icontains=search) | Q(message__icontains=search))
        feedback_type = self.request.GET.get('feedback_type', '')
        if feedback_type:
            qs = qs.filter(feedback_type=feedback_type)
        return qs.select_related('from_employee', 'to_employee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback_type_choices'] = Feedback.FEEDBACK_TYPE_CHOICES
        context['current_tab'] = self.request.GET.get('tab', 'received')
        return context


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'performance/feedback_form.html'
    success_url = reverse_lazy('performance:feedback_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        if hasattr(self.request.user, 'employee'):
            form.instance.from_employee = self.request.user.employee
        messages.success(self.request, 'Feedback sent successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Give Feedback'
        return context


class FeedbackDetailView(LoginRequiredMixin, DetailView):
    model = Feedback
    template_name = 'performance/feedback_detail.html'
    context_object_name = 'feedback'

    def get_queryset(self):
        return Feedback.objects.filter(tenant=self.request.tenant)


class FeedbackDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        feedback = get_object_or_404(Feedback, pk=pk, tenant=request.tenant)
        feedback.delete()
        messages.success(request, 'Feedback deleted successfully.')
        return redirect('performance:feedback_list')


# ===========================================================================
# 1:1 Meeting Views
# ===========================================================================

class MeetingListView(LoginRequiredMixin, ListView):
    model = OneOnOneMeeting
    template_name = 'performance/meeting_list.html'
    context_object_name = 'meetings'
    paginate_by = 20

    def get_queryset(self):
        qs = OneOnOneMeeting.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(manager__first_name__icontains=search) |
                Q(employee__first_name__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('manager', 'employee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = OneOnOneMeeting.STATUS_CHOICES
        return context


class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = OneOnOneMeeting
    form_class = MeetingForm
    template_name = 'performance/meeting_form.html'
    success_url = reverse_lazy('performance:meeting_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Meeting "{form.instance.title}" scheduled successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Schedule 1:1 Meeting'
        return context


class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = OneOnOneMeeting
    template_name = 'performance/meeting_detail.html'
    context_object_name = 'meeting'

    def get_queryset(self):
        return OneOnOneMeeting.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_items'] = self.object.action_items.select_related('assigned_to').all()
        context['action_form'] = MeetingActionItemForm(tenant=self.request.tenant)
        return context


class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = OneOnOneMeeting
    form_class = MeetingForm
    template_name = 'performance/meeting_form.html'
    success_url = reverse_lazy('performance:meeting_list')

    def get_queryset(self):
        return OneOnOneMeeting.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Meeting "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit 1:1 Meeting'
        return context


class MeetingDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        meeting = get_object_or_404(OneOnOneMeeting, pk=pk, tenant=request.tenant)
        title = meeting.title
        meeting.delete()
        messages.success(request, f'Meeting "{title}" deleted successfully.')
        return redirect('performance:meeting_list')


class ActionItemCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        meeting = get_object_or_404(OneOnOneMeeting, pk=pk, tenant=request.tenant)
        form = MeetingActionItemForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            item = form.save(commit=False)
            item.tenant = request.tenant
            item.meeting = meeting
            item.save()
            messages.success(request, 'Action item added successfully.')
        else:
            messages.error(request, 'Failed to add action item.')
        return redirect('performance:meeting_detail', pk=meeting.pk)


class ActionItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MeetingActionItem
    form_class = MeetingActionItemForm
    template_name = 'performance/action_item_form.html'

    def get_queryset(self):
        return MeetingActionItem.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Action item updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:meeting_detail', kwargs={'pk': self.object.meeting.pk})


# ===========================================================================
# PIP Views
# ===========================================================================

class PIPListView(LoginRequiredMixin, ListView):
    model = PIP
    template_name = 'performance/pip_list.html'
    context_object_name = 'pips'
    paginate_by = 20

    def get_queryset(self):
        qs = PIP.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.select_related('employee', 'initiated_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PIP.STATUS_CHOICES
        return context


class PIPCreateView(LoginRequiredMixin, CreateView):
    model = PIP
    form_class = PIPForm
    template_name = 'performance/pip_form.html'
    success_url = reverse_lazy('performance:pip_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'PIP "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create PIP'
        return context


class PIPDetailView(LoginRequiredMixin, DetailView):
    model = PIP
    template_name = 'performance/pip_detail.html'
    context_object_name = 'pip'

    def get_queryset(self):
        return PIP.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['checkpoints'] = self.object.checkpoints.all()
        return context


class PIPUpdateView(LoginRequiredMixin, UpdateView):
    model = PIP
    form_class = PIPForm
    template_name = 'performance/pip_form.html'
    success_url = reverse_lazy('performance:pip_list')

    def get_queryset(self):
        return PIP.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'PIP "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit PIP'
        return context


class PIPDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        pip = get_object_or_404(PIP, pk=pk, tenant=request.tenant)
        title = pip.title
        pip.delete()
        messages.success(request, f'PIP "{title}" deleted successfully.')
        return redirect('performance:pip_list')


class PIPCheckpointCreateView(LoginRequiredMixin, CreateView):
    model = PIPCheckpoint
    form_class = PIPCheckpointForm
    template_name = 'performance/pip_checkpoint_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.pip = get_object_or_404(PIP, pk=kwargs['pk'], tenant=request.tenant)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.pip = self.pip
        messages.success(self.request, 'Checkpoint added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:pip_detail', kwargs={'pk': self.pip.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pip'] = self.pip
        context['title'] = 'Add Checkpoint'
        return context


class PIPCheckpointUpdateView(LoginRequiredMixin, UpdateView):
    model = PIPCheckpoint
    form_class = PIPCheckpointForm
    template_name = 'performance/pip_checkpoint_form.html'

    def get_queryset(self):
        return PIPCheckpoint.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, 'Checkpoint updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('performance:pip_detail', kwargs={'pk': self.object.pip.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pip'] = self.object.pip
        context['title'] = 'Edit Checkpoint'
        return context


# ===========================================================================
# Warning Letter Views
# ===========================================================================

class WarningLetterListView(LoginRequiredMixin, ListView):
    model = WarningLetter
    template_name = 'performance/warning_list.html'
    context_object_name = 'warnings'
    paginate_by = 20

    def get_queryset(self):
        qs = WarningLetter.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(subject__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        warning_type = self.request.GET.get('warning_type', '')
        if warning_type:
            qs = qs.filter(warning_type=warning_type)
        return qs.select_related('employee', 'issued_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = WarningLetter.STATUS_CHOICES
        context['warning_type_choices'] = WarningLetter.WARNING_TYPE_CHOICES
        return context


class WarningLetterCreateView(LoginRequiredMixin, CreateView):
    model = WarningLetter
    form_class = WarningLetterForm
    template_name = 'performance/warning_form.html'
    success_url = reverse_lazy('performance:warning_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Warning letter created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Warning Letter'
        return context


class WarningLetterDetailView(LoginRequiredMixin, DetailView):
    model = WarningLetter
    template_name = 'performance/warning_detail.html'
    context_object_name = 'warning'

    def get_queryset(self):
        return WarningLetter.objects.filter(tenant=self.request.tenant)


class WarningLetterUpdateView(LoginRequiredMixin, UpdateView):
    model = WarningLetter
    form_class = WarningLetterForm
    template_name = 'performance/warning_form.html'
    success_url = reverse_lazy('performance:warning_list')

    def get_queryset(self):
        return WarningLetter.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Warning letter updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Warning Letter'
        return context


class WarningLetterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        warning = get_object_or_404(WarningLetter, pk=pk, tenant=request.tenant)
        warning.delete()
        messages.success(request, 'Warning letter deleted successfully.')
        return redirect('performance:warning_list')


# ===========================================================================
# Coaching Note Views
# ===========================================================================

class CoachingNoteListView(LoginRequiredMixin, ListView):
    model = CoachingNote
    template_name = 'performance/coaching_list.html'
    context_object_name = 'notes'
    paginate_by = 20

    def get_queryset(self):
        qs = CoachingNote.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(topic__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return qs.select_related('employee', 'coach')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CoachingNoteCreateView(LoginRequiredMixin, CreateView):
    model = CoachingNote
    form_class = CoachingNoteForm
    template_name = 'performance/coaching_form.html'
    success_url = reverse_lazy('performance:coaching_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Coaching note added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Coaching Note'
        return context


class CoachingNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = CoachingNote
    form_class = CoachingNoteForm
    template_name = 'performance/coaching_form.html'
    success_url = reverse_lazy('performance:coaching_list')

    def get_queryset(self):
        return CoachingNote.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Coaching note updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Coaching Note'
        return context


class CoachingNoteDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(CoachingNote, pk=pk, tenant=request.tenant)
        note.delete()
        messages.success(request, 'Coaching note deleted successfully.')
        return redirect('performance:coaching_list')
