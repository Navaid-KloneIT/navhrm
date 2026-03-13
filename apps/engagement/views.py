from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .models import (
    EngagementSurvey, EngagementSurveyQuestion, EngagementSurveyQuestionOption, EngagementSurveyResponse,
    EngagementSurveyAnswer, EngagementActionPlan,
    WellbeingProgram, WellbeingResource, WellnessChallenge, ChallengeParticipant,
    FlexibleWorkArrangement, RemoteWorkPolicy, WorkLifeBalanceAssessment,
    EAPProgram, CounselingSession, EAPUtilization,
    CompanyValue, CultureAssessment, CultureAssessmentResponse, ValueNomination,
    TeamEvent, EventParticipant, InterestGroup, InterestGroupMember,
    VolunteerActivity, VolunteerParticipant,
)
from .forms import (
    SurveyForm, SurveyQuestionForm, SurveyQuestionOptionForm, SurveyActionPlanForm,
    WellbeingProgramForm, WellbeingResourceForm, WellnessChallengeForm, ChallengeParticipantForm,
    FlexibleWorkArrangementForm, RemoteWorkPolicyForm, WorkLifeBalanceAssessmentForm,
    EAPProgramForm, CounselingSessionForm, EAPUtilizationForm,
    CompanyValueForm, CultureAssessmentForm, CultureAssessmentResponseForm, ValueNominationForm,
    TeamEventForm, EventParticipantForm, InterestGroupForm, InterestGroupMemberForm,
    VolunteerActivityForm, VolunteerParticipantForm,
)


# =============================================================================
# SUB-MODULE 1: ENGAGEMENT SURVEYS
# =============================================================================

class SurveyListView(LoginRequiredMixin, ListView):
    model = EngagementSurvey
    template_name = 'engagement/survey_list.html'
    context_object_name = 'surveys'
    paginate_by = 20

    def get_queryset(self):
        qs = EngagementSurvey.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        survey_type = self.request.GET.get('survey_type', '').strip()
        if survey_type:
            qs = qs.filter(survey_type=survey_type)
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey_type_choices'] = EngagementSurvey.SURVEY_TYPE_CHOICES
        context['status_choices'] = EngagementSurvey.STATUS_CHOICES
        return context


class SurveyCreateView(LoginRequiredMixin, CreateView):
    model = EngagementSurvey
    form_class = SurveyForm
    template_name = 'engagement/survey_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Survey created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url() if hasattr(self.object, 'get_absolute_url') else f'/engagement/surveys/{self.object.pk}/'


class SurveyDetailView(LoginRequiredMixin, DetailView):
    model = EngagementSurvey
    template_name = 'engagement/survey_detail.html'

    def get_queryset(self):
        return EngagementSurvey.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.prefetch_related('options')
        context['responses'] = self.object.responses.filter(is_complete=True).select_related('employee')
        context['action_plans'] = self.object.action_plans.select_related('assigned_to')
        return context


class SurveyUpdateView(LoginRequiredMixin, UpdateView):
    model = EngagementSurvey
    form_class = SurveyForm
    template_name = 'engagement/survey_form.html'

    def get_queryset(self):
        return EngagementSurvey.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Survey updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/surveys/{self.object.pk}/'


class SurveyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        survey = get_object_or_404(EngagementSurvey, pk=pk, tenant=request.tenant)
        survey.delete()
        messages.success(request, 'Survey deleted successfully.')
        return redirect('engagement:survey_list')


# --- Survey Questions ---

class SurveyQuestionCreateView(LoginRequiredMixin, CreateView):
    model = EngagementSurveyQuestion
    form_class = SurveyQuestionForm
    template_name = 'engagement/survey_question_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        survey = get_object_or_404(EngagementSurvey, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.survey = survey
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Question added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = get_object_or_404(EngagementSurvey, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/surveys/{self.kwargs["pk"]}/'


class SurveyQuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = EngagementSurveyQuestion
    form_class = SurveyQuestionForm
    template_name = 'engagement/survey_question_form.html'

    def get_queryset(self):
        return EngagementSurveyQuestion.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Question updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = self.object.survey
        return context

    def get_success_url(self):
        return f'/engagement/surveys/{self.object.survey.pk}/'


class SurveyQuestionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        question = get_object_or_404(EngagementSurveyQuestion, pk=pk, tenant=request.tenant)
        survey_pk = question.survey.pk
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        return redirect('engagement:survey_detail', pk=survey_pk)


# --- Survey Question Options ---

class SurveyQuestionOptionCreateView(LoginRequiredMixin, CreateView):
    model = EngagementSurveyQuestionOption
    form_class = SurveyQuestionOptionForm
    template_name = 'engagement/survey_question_option_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        question = get_object_or_404(EngagementSurveyQuestion, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.question = question
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Option added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = get_object_or_404(EngagementSurveyQuestion, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        question = get_object_or_404(EngagementSurveyQuestion, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return f'/engagement/surveys/{question.survey.pk}/'


class SurveyQuestionOptionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        option = get_object_or_404(EngagementSurveyQuestionOption, pk=pk, tenant=request.tenant)
        survey_pk = option.question.survey.pk
        option.delete()
        messages.success(request, 'Option deleted successfully.')
        return redirect('engagement:survey_detail', pk=survey_pk)


# --- Survey Responses ---

class SurveyRespondView(LoginRequiredMixin, DetailView):
    model = EngagementSurvey
    template_name = 'engagement/survey_respond_form.html'

    def get_queryset(self):
        return EngagementSurvey.objects.filter(tenant=self.request.tenant, status='active')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.prefetch_related('options')
        return context

    def post(self, request, pk):
        survey = get_object_or_404(EngagementSurvey, pk=pk, tenant=request.tenant, status='active')
        employee = getattr(request.user, 'employee', None) if not survey.is_anonymous else None
        response = EngagementSurveyResponse.objects.create(
            survey=survey,
            employee=employee,
            tenant=request.tenant,
            submitted_at=timezone.now(),
            is_complete=True,
        )
        for question in survey.questions.all():
            answer = EngagementSurveyAnswer(
                response=response,
                question=question,
                tenant=request.tenant,
            )
            if question.question_type == 'text':
                answer.text_answer = request.POST.get(f'question_{question.pk}', '')
            elif question.question_type in ('single_choice', 'yes_no'):
                option_pk = request.POST.get(f'question_{question.pk}')
                if option_pk:
                    answer.selected_option_id = option_pk
            elif question.question_type in ('rating', 'scale'):
                rating = request.POST.get(f'question_{question.pk}')
                if rating:
                    answer.rating_value = int(rating)
            elif question.question_type == 'multiple_choice':
                answer.text_answer = ','.join(request.POST.getlist(f'question_{question.pk}'))
            answer.save()
        messages.success(request, 'Survey response submitted successfully.')
        return redirect('engagement:survey_list')


class SurveyResponseDetailView(LoginRequiredMixin, DetailView):
    model = EngagementSurveyResponse
    template_name = 'engagement/survey_response_detail.html'

    def get_queryset(self):
        return EngagementSurveyResponse.objects.filter(
            tenant=self.request.tenant
        ).select_related('survey', 'employee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = self.object.answers.select_related('question', 'selected_option')
        return context


# --- Survey Action Plans ---

class SurveyActionPlanListView(LoginRequiredMixin, ListView):
    model = EngagementActionPlan
    template_name = 'engagement/action_plan_list.html'
    context_object_name = 'action_plans'
    paginate_by = 20

    def get_queryset(self):
        qs = EngagementActionPlan.objects.filter(
            tenant=self.request.tenant
        ).select_related('survey', 'assigned_to')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        priority = self.request.GET.get('priority', '').strip()
        if priority:
            qs = qs.filter(priority=priority)
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['priority_choices'] = EngagementActionPlan.PRIORITY_CHOICES
        context['status_choices'] = EngagementActionPlan.STATUS_CHOICES
        return context


class SurveyActionPlanCreateView(LoginRequiredMixin, CreateView):
    model = EngagementActionPlan
    form_class = SurveyActionPlanForm
    template_name = 'engagement/action_plan_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        survey = get_object_or_404(EngagementSurvey, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.survey = survey
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Action plan created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = get_object_or_404(EngagementSurvey, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/surveys/{self.kwargs["pk"]}/'


class SurveyActionPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = EngagementActionPlan
    form_class = SurveyActionPlanForm
    template_name = 'engagement/action_plan_form.html'

    def get_queryset(self):
        return EngagementActionPlan.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Action plan updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/surveys/{self.object.survey.pk}/'


class SurveyActionPlanDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(EngagementActionPlan, pk=pk, tenant=request.tenant)
        survey_pk = plan.survey.pk
        plan.delete()
        messages.success(request, 'Action plan deleted successfully.')
        return redirect('engagement:survey_detail', pk=survey_pk)


# =============================================================================
# SUB-MODULE 2: WELLBEING PROGRAMS
# =============================================================================

class WellbeingProgramListView(LoginRequiredMixin, ListView):
    model = WellbeingProgram
    template_name = 'engagement/program_list.html'
    context_object_name = 'programs'
    paginate_by = 20

    def get_queryset(self):
        qs = WellbeingProgram.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        category = self.request.GET.get('category', '').strip()
        if category:
            qs = qs.filter(category=category)
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = WellbeingProgram.CATEGORY_CHOICES
        context['status_choices'] = WellbeingProgram.STATUS_CHOICES
        return context


class WellbeingProgramCreateView(LoginRequiredMixin, CreateView):
    model = WellbeingProgram
    form_class = WellbeingProgramForm
    template_name = 'engagement/program_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Wellbeing program created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/programs/{self.object.pk}/'


class WellbeingProgramDetailView(LoginRequiredMixin, DetailView):
    model = WellbeingProgram
    template_name = 'engagement/program_detail.html'

    def get_queryset(self):
        return WellbeingProgram.objects.filter(tenant=self.request.tenant)


class WellbeingProgramUpdateView(LoginRequiredMixin, UpdateView):
    model = WellbeingProgram
    form_class = WellbeingProgramForm
    template_name = 'engagement/program_form.html'

    def get_queryset(self):
        return WellbeingProgram.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Wellbeing program updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/programs/{self.object.pk}/'


class WellbeingProgramDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        program = get_object_or_404(WellbeingProgram, pk=pk, tenant=request.tenant)
        program.delete()
        messages.success(request, 'Wellbeing program deleted successfully.')
        return redirect('engagement:program_list')


# --- Wellbeing Resources ---

class WellbeingResourceListView(LoginRequiredMixin, ListView):
    model = WellbeingResource
    template_name = 'engagement/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 20

    def get_queryset(self):
        qs = WellbeingResource.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        resource_type = self.request.GET.get('resource_type', '').strip()
        if resource_type:
            qs = qs.filter(resource_type=resource_type)
        category = self.request.GET.get('category', '').strip()
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_type_choices'] = WellbeingResource.RESOURCE_TYPE_CHOICES
        context['category_choices'] = WellbeingResource.CATEGORY_CHOICES
        return context


class WellbeingResourceCreateView(LoginRequiredMixin, CreateView):
    model = WellbeingResource
    form_class = WellbeingResourceForm
    template_name = 'engagement/resource_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Wellbeing resource created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/resources/{self.object.pk}/'


class WellbeingResourceDetailView(LoginRequiredMixin, DetailView):
    model = WellbeingResource
    template_name = 'engagement/resource_detail.html'

    def get_queryset(self):
        return WellbeingResource.objects.filter(tenant=self.request.tenant)


class WellbeingResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = WellbeingResource
    form_class = WellbeingResourceForm
    template_name = 'engagement/resource_form.html'

    def get_queryset(self):
        return WellbeingResource.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Wellbeing resource updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/resources/{self.object.pk}/'


class WellbeingResourceDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        resource = get_object_or_404(WellbeingResource, pk=pk, tenant=request.tenant)
        resource.delete()
        messages.success(request, 'Wellbeing resource deleted successfully.')
        return redirect('engagement:resource_list')


# --- Wellness Challenges ---

class WellnessChallengeListView(LoginRequiredMixin, ListView):
    model = WellnessChallenge
    template_name = 'engagement/challenge_list.html'
    context_object_name = 'challenges'
    paginate_by = 20

    def get_queryset(self):
        qs = WellnessChallenge.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        challenge_type = self.request.GET.get('challenge_type', '').strip()
        if challenge_type:
            qs = qs.filter(challenge_type=challenge_type)
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challenge_type_choices'] = WellnessChallenge.CHALLENGE_TYPE_CHOICES
        context['status_choices'] = WellnessChallenge.STATUS_CHOICES
        return context


class WellnessChallengeCreateView(LoginRequiredMixin, CreateView):
    model = WellnessChallenge
    form_class = WellnessChallengeForm
    template_name = 'engagement/challenge_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Wellness challenge created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/challenges/{self.object.pk}/'


class WellnessChallengeDetailView(LoginRequiredMixin, DetailView):
    model = WellnessChallenge
    template_name = 'engagement/challenge_detail.html'

    def get_queryset(self):
        return WellnessChallenge.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participants'] = self.object.participants.select_related('employee')
        return context


class WellnessChallengeUpdateView(LoginRequiredMixin, UpdateView):
    model = WellnessChallenge
    form_class = WellnessChallengeForm
    template_name = 'engagement/challenge_form.html'

    def get_queryset(self):
        return WellnessChallenge.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Wellness challenge updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/challenges/{self.object.pk}/'


class WellnessChallengeDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        challenge = get_object_or_404(WellnessChallenge, pk=pk, tenant=request.tenant)
        challenge.delete()
        messages.success(request, 'Wellness challenge deleted successfully.')
        return redirect('engagement:challenge_list')


class ChallengeParticipantCreateView(LoginRequiredMixin, CreateView):
    model = ChallengeParticipant
    form_class = ChallengeParticipantForm
    template_name = 'engagement/challenge_participant_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        challenge = get_object_or_404(WellnessChallenge, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.challenge = challenge
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Participant added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challenge'] = get_object_or_404(WellnessChallenge, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/challenges/{self.kwargs["pk"]}/'


class ChallengeParticipantUpdateView(LoginRequiredMixin, UpdateView):
    model = ChallengeParticipant
    form_class = ChallengeParticipantForm
    template_name = 'engagement/challenge_participant_form.html'

    def get_queryset(self):
        return ChallengeParticipant.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Participant updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challenge'] = self.object.challenge
        return context

    def get_success_url(self):
        return f'/engagement/challenges/{self.object.challenge.pk}/'


# =============================================================================
# SUB-MODULE 3: WORK-LIFE BALANCE
# =============================================================================

class FlexibleWorkArrangementListView(LoginRequiredMixin, ListView):
    model = FlexibleWorkArrangement
    template_name = 'engagement/arrangement_list.html'
    context_object_name = 'arrangements'
    paginate_by = 20

    def get_queryset(self):
        qs = FlexibleWorkArrangement.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'approved_by')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(notes__icontains=search)
            )
        arrangement_type = self.request.GET.get('arrangement_type', '').strip()
        if arrangement_type:
            qs = qs.filter(arrangement_type=arrangement_type)
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['arrangement_type_choices'] = FlexibleWorkArrangement.ARRANGEMENT_TYPE_CHOICES
        context['status_choices'] = FlexibleWorkArrangement.STATUS_CHOICES
        return context


class FlexibleWorkArrangementCreateView(LoginRequiredMixin, CreateView):
    model = FlexibleWorkArrangement
    form_class = FlexibleWorkArrangementForm
    template_name = 'engagement/arrangement_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Work arrangement created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/arrangements/{self.object.pk}/'


class FlexibleWorkArrangementDetailView(LoginRequiredMixin, DetailView):
    model = FlexibleWorkArrangement
    template_name = 'engagement/arrangement_detail.html'

    def get_queryset(self):
        return FlexibleWorkArrangement.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'approved_by')


class FlexibleWorkArrangementUpdateView(LoginRequiredMixin, UpdateView):
    model = FlexibleWorkArrangement
    form_class = FlexibleWorkArrangementForm
    template_name = 'engagement/arrangement_form.html'

    def get_queryset(self):
        return FlexibleWorkArrangement.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Work arrangement updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/arrangements/{self.object.pk}/'


class FlexibleWorkArrangementDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        arrangement = get_object_or_404(FlexibleWorkArrangement, pk=pk, tenant=request.tenant)
        arrangement.delete()
        messages.success(request, 'Work arrangement deleted successfully.')
        return redirect('engagement:arrangement_list')


# --- Remote Work Policies ---

class RemoteWorkPolicyListView(LoginRequiredMixin, ListView):
    model = RemoteWorkPolicy
    template_name = 'engagement/remote_policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        qs = RemoteWorkPolicy.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        is_active = self.request.GET.get('is_active', '').strip()
        if is_active == 'active':
            qs = qs.filter(is_active=True)
        elif is_active == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RemoteWorkPolicyCreateView(LoginRequiredMixin, CreateView):
    model = RemoteWorkPolicy
    form_class = RemoteWorkPolicyForm
    template_name = 'engagement/remote_policy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Remote work policy created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/remote-policies/{self.object.pk}/'


class RemoteWorkPolicyDetailView(LoginRequiredMixin, DetailView):
    model = RemoteWorkPolicy
    template_name = 'engagement/remote_policy_detail.html'

    def get_queryset(self):
        return RemoteWorkPolicy.objects.filter(tenant=self.request.tenant)


class RemoteWorkPolicyUpdateView(LoginRequiredMixin, UpdateView):
    model = RemoteWorkPolicy
    form_class = RemoteWorkPolicyForm
    template_name = 'engagement/remote_policy_form.html'

    def get_queryset(self):
        return RemoteWorkPolicy.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Remote work policy updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/remote-policies/{self.object.pk}/'


class RemoteWorkPolicyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        policy = get_object_or_404(RemoteWorkPolicy, pk=pk, tenant=request.tenant)
        policy.delete()
        messages.success(request, 'Remote work policy deleted successfully.')
        return redirect('engagement:remote_policy_list')


# --- Work-Life Balance Assessments ---

class WorkLifeBalanceAssessmentListView(LoginRequiredMixin, ListView):
    model = WorkLifeBalanceAssessment
    template_name = 'engagement/wlb_assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20

    def get_queryset(self):
        qs = WorkLifeBalanceAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WorkLifeBalanceAssessmentCreateView(LoginRequiredMixin, CreateView):
    model = WorkLifeBalanceAssessment
    form_class = WorkLifeBalanceAssessmentForm
    template_name = 'engagement/wlb_assessment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Assessment created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/wlb-assessments/{self.object.pk}/'


class WorkLifeBalanceAssessmentDetailView(LoginRequiredMixin, DetailView):
    model = WorkLifeBalanceAssessment
    template_name = 'engagement/wlb_assessment_detail.html'

    def get_queryset(self):
        return WorkLifeBalanceAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee')


class WorkLifeBalanceAssessmentUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkLifeBalanceAssessment
    form_class = WorkLifeBalanceAssessmentForm
    template_name = 'engagement/wlb_assessment_form.html'

    def get_queryset(self):
        return WorkLifeBalanceAssessment.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Assessment updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/wlb-assessments/{self.object.pk}/'


class WorkLifeBalanceAssessmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        assessment = get_object_or_404(WorkLifeBalanceAssessment, pk=pk, tenant=request.tenant)
        assessment.delete()
        messages.success(request, 'Assessment deleted successfully.')
        return redirect('engagement:wlb_assessment_list')


# =============================================================================
# SUB-MODULE 4: EMPLOYEE ASSISTANCE
# =============================================================================

class EAPProgramListView(LoginRequiredMixin, ListView):
    model = EAPProgram
    template_name = 'engagement/eap_program_list.html'
    context_object_name = 'programs'
    paginate_by = 20

    def get_queryset(self):
        qs = EAPProgram.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(provider__icontains=search))
        service_type = self.request.GET.get('service_type', '').strip()
        if service_type:
            qs = qs.filter(service_type=service_type)
        is_active = self.request.GET.get('is_active', '').strip()
        if is_active == 'active':
            qs = qs.filter(is_active=True)
        elif is_active == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_type_choices'] = EAPProgram.SERVICE_TYPE_CHOICES
        return context


class EAPProgramCreateView(LoginRequiredMixin, CreateView):
    model = EAPProgram
    form_class = EAPProgramForm
    template_name = 'engagement/eap_program_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'EAP program created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/eap-programs/{self.object.pk}/'


class EAPProgramDetailView(LoginRequiredMixin, DetailView):
    model = EAPProgram
    template_name = 'engagement/eap_program_detail.html'

    def get_queryset(self):
        return EAPProgram.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = self.object.sessions.select_related('employee')[:10]
        context['utilizations'] = self.object.utilizations.all()[:10]
        return context


class EAPProgramUpdateView(LoginRequiredMixin, UpdateView):
    model = EAPProgram
    form_class = EAPProgramForm
    template_name = 'engagement/eap_program_form.html'

    def get_queryset(self):
        return EAPProgram.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'EAP program updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/eap-programs/{self.object.pk}/'


class EAPProgramDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        program = get_object_or_404(EAPProgram, pk=pk, tenant=request.tenant)
        program.delete()
        messages.success(request, 'EAP program deleted successfully.')
        return redirect('engagement:eap_program_list')


# --- Counseling Sessions ---

class CounselingSessionListView(LoginRequiredMixin, ListView):
    model = CounselingSession
    template_name = 'engagement/counseling_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        qs = CounselingSession.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'program')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(counselor_name__icontains=search)
            )
        session_type = self.request.GET.get('session_type', '').strip()
        if session_type:
            qs = qs.filter(session_type=session_type)
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        program = self.request.GET.get('program', '').strip()
        if program:
            qs = qs.filter(program_id=program)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_type_choices'] = CounselingSession.SESSION_TYPE_CHOICES
        context['status_choices'] = CounselingSession.STATUS_CHOICES
        context['eap_programs'] = EAPProgram.objects.filter(tenant=self.request.tenant, is_active=True)
        return context


class CounselingSessionCreateView(LoginRequiredMixin, CreateView):
    model = CounselingSession
    form_class = CounselingSessionForm
    template_name = 'engagement/counseling_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Counseling session created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/counseling/{self.object.pk}/'


class CounselingSessionDetailView(LoginRequiredMixin, DetailView):
    model = CounselingSession
    template_name = 'engagement/counseling_detail.html'

    def get_queryset(self):
        return CounselingSession.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'program')


class CounselingSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = CounselingSession
    form_class = CounselingSessionForm
    template_name = 'engagement/counseling_form.html'

    def get_queryset(self):
        return CounselingSession.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Counseling session updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/counseling/{self.object.pk}/'


class CounselingSessionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(CounselingSession, pk=pk, tenant=request.tenant)
        session.delete()
        messages.success(request, 'Counseling session deleted successfully.')
        return redirect('engagement:counseling_list')


# --- EAP Utilization ---

class EAPUtilizationCreateView(LoginRequiredMixin, CreateView):
    model = EAPUtilization
    form_class = EAPUtilizationForm
    template_name = 'engagement/eap_utilization_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        program = get_object_or_404(EAPProgram, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.program = program
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Utilization record created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = get_object_or_404(EAPProgram, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/eap-programs/{self.kwargs["pk"]}/'


class EAPUtilizationUpdateView(LoginRequiredMixin, UpdateView):
    model = EAPUtilization
    form_class = EAPUtilizationForm
    template_name = 'engagement/eap_utilization_form.html'

    def get_queryset(self):
        return EAPUtilization.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Utilization record updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = self.object.program
        return context

    def get_success_url(self):
        return f'/engagement/eap-programs/{self.object.program.pk}/'


class EAPUtilizationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        utilization = get_object_or_404(EAPUtilization, pk=pk, tenant=request.tenant)
        program_pk = utilization.program.pk
        utilization.delete()
        messages.success(request, 'Utilization record deleted successfully.')
        return redirect('engagement:eap_program_detail', pk=program_pk)


# =============================================================================
# SUB-MODULE 5: CULTURE & VALUES
# =============================================================================

class CompanyValueListView(LoginRequiredMixin, ListView):
    model = CompanyValue
    template_name = 'engagement/value_list.html'
    context_object_name = 'values'
    paginate_by = 20

    def get_queryset(self):
        qs = CompanyValue.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        is_active = self.request.GET.get('is_active', '').strip()
        if is_active == 'active':
            qs = qs.filter(is_active=True)
        elif is_active == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CompanyValueCreateView(LoginRequiredMixin, CreateView):
    model = CompanyValue
    form_class = CompanyValueForm
    template_name = 'engagement/value_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Company value created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/values/{self.object.pk}/'


class CompanyValueDetailView(LoginRequiredMixin, DetailView):
    model = CompanyValue
    template_name = 'engagement/value_detail.html'

    def get_queryset(self):
        return CompanyValue.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nominations'] = self.object.nominations.select_related(
            'nominee', 'nominated_by'
        ).order_by('-created_at')[:10]
        return context


class CompanyValueUpdateView(LoginRequiredMixin, UpdateView):
    model = CompanyValue
    form_class = CompanyValueForm
    template_name = 'engagement/value_form.html'

    def get_queryset(self):
        return CompanyValue.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Company value updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/values/{self.object.pk}/'


class CompanyValueDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        value = get_object_or_404(CompanyValue, pk=pk, tenant=request.tenant)
        value.delete()
        messages.success(request, 'Company value deleted successfully.')
        return redirect('engagement:value_list')


# --- Culture Assessments ---

class CultureAssessmentListView(LoginRequiredMixin, ListView):
    model = CultureAssessment
    template_name = 'engagement/culture_assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20

    def get_queryset(self):
        qs = CultureAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('created_by')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = CultureAssessment.STATUS_CHOICES
        return context


class CultureAssessmentCreateView(LoginRequiredMixin, CreateView):
    model = CultureAssessment
    form_class = CultureAssessmentForm
    template_name = 'engagement/culture_assessment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Culture assessment created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/culture-assessments/{self.object.pk}/'


class CultureAssessmentDetailView(LoginRequiredMixin, DetailView):
    model = CultureAssessment
    template_name = 'engagement/culture_assessment_detail.html'

    def get_queryset(self):
        return CultureAssessment.objects.filter(
            tenant=self.request.tenant
        ).select_related('created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = self.object.responses.select_related('employee')
        return context


class CultureAssessmentUpdateView(LoginRequiredMixin, UpdateView):
    model = CultureAssessment
    form_class = CultureAssessmentForm
    template_name = 'engagement/culture_assessment_form.html'

    def get_queryset(self):
        return CultureAssessment.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Culture assessment updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/culture-assessments/{self.object.pk}/'


class CultureAssessmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        assessment = get_object_or_404(CultureAssessment, pk=pk, tenant=request.tenant)
        assessment.delete()
        messages.success(request, 'Culture assessment deleted successfully.')
        return redirect('engagement:culture_assessment_list')


class CultureAssessmentRespondView(LoginRequiredMixin, CreateView):
    model = CultureAssessmentResponse
    form_class = CultureAssessmentResponseForm
    template_name = 'engagement/culture_assessment_respond_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        assessment = get_object_or_404(CultureAssessment, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.assessment = assessment
        form.instance.tenant = self.request.tenant
        employee = getattr(self.request.user, 'employee', None)
        if employee:
            form.instance.employee = employee
        messages.success(self.request, 'Response submitted successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment'] = get_object_or_404(CultureAssessment, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/culture-assessments/{self.kwargs["pk"]}/'


# --- Value Nominations ---

class ValueNominationListView(LoginRequiredMixin, ListView):
    model = ValueNomination
    template_name = 'engagement/nomination_list.html'
    context_object_name = 'nominations'
    paginate_by = 20

    def get_queryset(self):
        qs = ValueNomination.objects.filter(
            tenant=self.request.tenant
        ).select_related('value', 'nominee', 'nominated_by')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(nominee__first_name__icontains=search) |
                Q(nominee__last_name__icontains=search) |
                Q(reason__icontains=search)
            )
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        value = self.request.GET.get('value', '').strip()
        if value:
            qs = qs.filter(value_id=value)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ValueNomination.STATUS_CHOICES
        context['company_values'] = CompanyValue.objects.filter(tenant=self.request.tenant, is_active=True)
        return context


class ValueNominationCreateView(LoginRequiredMixin, CreateView):
    model = ValueNomination
    form_class = ValueNominationForm
    template_name = 'engagement/nomination_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Nomination created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return '/engagement/nominations/'


class ValueNominationUpdateView(LoginRequiredMixin, UpdateView):
    model = ValueNomination
    form_class = ValueNominationForm
    template_name = 'engagement/nomination_form.html'

    def get_queryset(self):
        return ValueNomination.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Nomination updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return '/engagement/nominations/'


class ValueNominationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        nomination = get_object_or_404(ValueNomination, pk=pk, tenant=request.tenant)
        nomination.delete()
        messages.success(request, 'Nomination deleted successfully.')
        return redirect('engagement:nomination_list')


# =============================================================================
# SUB-MODULE 6: SOCIAL CONNECT
# =============================================================================

class TeamEventListView(LoginRequiredMixin, ListView):
    model = TeamEvent
    template_name = 'engagement/event_list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        qs = TeamEvent.objects.filter(
            tenant=self.request.tenant
        ).select_related('organizer')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(location__icontains=search))
        event_type = self.request.GET.get('event_type', '').strip()
        if event_type:
            qs = qs.filter(event_type=event_type)
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_type_choices'] = TeamEvent.EVENT_TYPE_CHOICES
        context['status_choices'] = TeamEvent.STATUS_CHOICES
        return context


class TeamEventCreateView(LoginRequiredMixin, CreateView):
    model = TeamEvent
    form_class = TeamEventForm
    template_name = 'engagement/event_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Team event created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/events/{self.object.pk}/'


class TeamEventDetailView(LoginRequiredMixin, DetailView):
    model = TeamEvent
    template_name = 'engagement/event_detail.html'

    def get_queryset(self):
        return TeamEvent.objects.filter(
            tenant=self.request.tenant
        ).select_related('organizer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participants'] = self.object.participants.select_related('employee')
        return context


class TeamEventUpdateView(LoginRequiredMixin, UpdateView):
    model = TeamEvent
    form_class = TeamEventForm
    template_name = 'engagement/event_form.html'

    def get_queryset(self):
        return TeamEvent.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Team event updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/events/{self.object.pk}/'


class TeamEventDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(TeamEvent, pk=pk, tenant=request.tenant)
        event.delete()
        messages.success(request, 'Team event deleted successfully.')
        return redirect('engagement:event_list')


class EventParticipantCreateView(LoginRequiredMixin, CreateView):
    model = EventParticipant
    form_class = EventParticipantForm
    template_name = 'engagement/event_participant_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        event = get_object_or_404(TeamEvent, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.event = event
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Participant added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(TeamEvent, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/events/{self.kwargs["pk"]}/'


class EventParticipantUpdateView(LoginRequiredMixin, UpdateView):
    model = EventParticipant
    form_class = EventParticipantForm
    template_name = 'engagement/event_participant_form.html'

    def get_queryset(self):
        return EventParticipant.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Participant updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.object.event
        return context

    def get_success_url(self):
        return f'/engagement/events/{self.object.event.pk}/'


# --- Interest Groups ---

class InterestGroupListView(LoginRequiredMixin, ListView):
    model = InterestGroup
    template_name = 'engagement/interest_group_list.html'
    context_object_name = 'groups'
    paginate_by = 20

    def get_queryset(self):
        qs = InterestGroup.objects.filter(
            tenant=self.request.tenant
        ).select_related('created_by')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        category = self.request.GET.get('category', '').strip()
        if category:
            qs = qs.filter(category=category)
        is_active = self.request.GET.get('is_active', '').strip()
        if is_active == 'active':
            qs = qs.filter(is_active=True)
        elif is_active == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = InterestGroup.CATEGORY_CHOICES
        return context


class InterestGroupCreateView(LoginRequiredMixin, CreateView):
    model = InterestGroup
    form_class = InterestGroupForm
    template_name = 'engagement/interest_group_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Interest group created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/interest-groups/{self.object.pk}/'


class InterestGroupDetailView(LoginRequiredMixin, DetailView):
    model = InterestGroup
    template_name = 'engagement/interest_group_detail.html'

    def get_queryset(self):
        return InterestGroup.objects.filter(
            tenant=self.request.tenant
        ).select_related('created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.select_related('employee')
        return context


class InterestGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = InterestGroup
    form_class = InterestGroupForm
    template_name = 'engagement/interest_group_form.html'

    def get_queryset(self):
        return InterestGroup.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Interest group updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/interest-groups/{self.object.pk}/'


class InterestGroupDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        group = get_object_or_404(InterestGroup, pk=pk, tenant=request.tenant)
        group.delete()
        messages.success(request, 'Interest group deleted successfully.')
        return redirect('engagement:interest_group_list')


class InterestGroupMemberCreateView(LoginRequiredMixin, CreateView):
    model = InterestGroupMember
    form_class = InterestGroupMemberForm
    template_name = 'engagement/interest_group_member_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        group = get_object_or_404(InterestGroup, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.group = group
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Member added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(InterestGroup, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/interest-groups/{self.kwargs["pk"]}/'


class InterestGroupMemberDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(InterestGroupMember, pk=pk, tenant=request.tenant)
        group_pk = member.group.pk
        member.delete()
        messages.success(request, 'Member removed successfully.')
        return redirect('engagement:interest_group_detail', pk=group_pk)


# --- Volunteer Activities ---

class VolunteerActivityListView(LoginRequiredMixin, ListView):
    model = VolunteerActivity
    template_name = 'engagement/volunteer_list.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        qs = VolunteerActivity.objects.filter(
            tenant=self.request.tenant
        ).select_related('organizer')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(location__icontains=search))
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = VolunteerActivity.STATUS_CHOICES
        return context


class VolunteerActivityCreateView(LoginRequiredMixin, CreateView):
    model = VolunteerActivity
    form_class = VolunteerActivityForm
    template_name = 'engagement/volunteer_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Volunteer activity created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/volunteering/{self.object.pk}/'


class VolunteerActivityDetailView(LoginRequiredMixin, DetailView):
    model = VolunteerActivity
    template_name = 'engagement/volunteer_detail.html'

    def get_queryset(self):
        return VolunteerActivity.objects.filter(
            tenant=self.request.tenant
        ).select_related('organizer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participants'] = self.object.participants.select_related('employee')
        return context


class VolunteerActivityUpdateView(LoginRequiredMixin, UpdateView):
    model = VolunteerActivity
    form_class = VolunteerActivityForm
    template_name = 'engagement/volunteer_form.html'

    def get_queryset(self):
        return VolunteerActivity.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Volunteer activity updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'/engagement/volunteering/{self.object.pk}/'


class VolunteerActivityDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(VolunteerActivity, pk=pk, tenant=request.tenant)
        activity.delete()
        messages.success(request, 'Volunteer activity deleted successfully.')
        return redirect('engagement:volunteer_list')


class VolunteerParticipantCreateView(LoginRequiredMixin, CreateView):
    model = VolunteerParticipant
    form_class = VolunteerParticipantForm
    template_name = 'engagement/volunteer_participant_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        activity = get_object_or_404(VolunteerActivity, pk=self.kwargs['pk'], tenant=self.request.tenant)
        form.instance.activity = activity
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Volunteer added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity'] = get_object_or_404(VolunteerActivity, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def get_success_url(self):
        return f'/engagement/volunteering/{self.kwargs["pk"]}/'


class VolunteerParticipantUpdateView(LoginRequiredMixin, UpdateView):
    model = VolunteerParticipant
    form_class = VolunteerParticipantForm
    template_name = 'engagement/volunteer_participant_form.html'

    def get_queryset(self):
        return VolunteerParticipant.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Volunteer updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity'] = self.object.activity
        return context

    def get_success_url(self):
        return f'/engagement/volunteering/{self.object.activity.pk}/'
