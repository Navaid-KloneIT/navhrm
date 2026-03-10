from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from .models import (
    SalaryBenchmark,
    BenefitPlan, EmployeeBenefit,
    FlexBenefitPlan, FlexBenefitOption, EmployeeFlexSelection,
    EquityGrant, VestingEvent, ExerciseRecord,
    CompensationPlan, CompensationRecommendation,
    RewardProgram, Recognition,
)
from .forms import (
    SalaryBenchmarkForm,
    BenefitPlanForm, EmployeeBenefitForm,
    FlexBenefitPlanForm, FlexBenefitOptionForm, EmployeeFlexSelectionForm,
    EquityGrantForm, VestingEventForm, ExerciseRecordForm,
    CompensationPlanForm, CompensationRecommendationForm,
    RewardProgramForm, RecognitionForm,
)


# ===========================================================================
# Salary Benchmarking Views
# ===========================================================================

class BenchmarkListView(LoginRequiredMixin, ListView):
    model = SalaryBenchmark
    template_name = 'compensation/benchmark_list.html'
    context_object_name = 'benchmarks'
    paginate_by = 20

    def get_queryset(self):
        qs = SalaryBenchmark.objects.filter(tenant=self.request.tenant).select_related('designation')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(job_title__icontains=search) | Q(industry__icontains=search) | Q(location__icontains=search)
            )
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        return context


class BenchmarkCreateView(LoginRequiredMixin, CreateView):
    model = SalaryBenchmark
    form_class = SalaryBenchmarkForm
    template_name = 'compensation/benchmark_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Salary Benchmark'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Salary benchmark created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:benchmark_detail', kwargs={'pk': self.object.pk})


class BenchmarkDetailView(LoginRequiredMixin, DetailView):
    model = SalaryBenchmark
    template_name = 'compensation/benchmark_detail.html'
    context_object_name = 'benchmark'

    def get_queryset(self):
        return SalaryBenchmark.objects.filter(tenant=self.request.tenant).select_related('designation')


class BenchmarkUpdateView(LoginRequiredMixin, UpdateView):
    model = SalaryBenchmark
    form_class = SalaryBenchmarkForm
    template_name = 'compensation/benchmark_form.html'

    def get_queryset(self):
        return SalaryBenchmark.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Salary Benchmark'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Salary benchmark updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:benchmark_detail', kwargs={'pk': self.object.pk})


class BenchmarkDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        benchmark = get_object_or_404(SalaryBenchmark, pk=pk, tenant=request.tenant)
        benchmark.delete()
        messages.success(request, 'Salary benchmark deleted successfully.')
        return redirect('compensation:benchmark_list')


# ===========================================================================
# Benefits Administration Views
# ===========================================================================

class BenefitPlanListView(LoginRequiredMixin, ListView):
    model = BenefitPlan
    template_name = 'compensation/benefit_plan_list.html'
    context_object_name = 'plans'
    paginate_by = 20

    def get_queryset(self):
        qs = BenefitPlan.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        plan_type = self.request.GET.get('plan_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(provider__icontains=search))
        if plan_type:
            qs = qs.filter(plan_type=plan_type)
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_plan_type'] = self.request.GET.get('plan_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['plan_type_choices'] = BenefitPlan.PLAN_TYPE_CHOICES
        return context


class BenefitPlanCreateView(LoginRequiredMixin, CreateView):
    model = BenefitPlan
    form_class = BenefitPlanForm
    template_name = 'compensation/benefit_plan_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Benefit Plan'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Benefit plan created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:benefit_plan_detail', kwargs={'pk': self.object.pk})


class BenefitPlanDetailView(LoginRequiredMixin, DetailView):
    model = BenefitPlan
    template_name = 'compensation/benefit_plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return BenefitPlan.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = self.object.enrollments.select_related('employee').all()[:20]
        return context


class BenefitPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = BenefitPlan
    form_class = BenefitPlanForm
    template_name = 'compensation/benefit_plan_form.html'

    def get_queryset(self):
        return BenefitPlan.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Benefit Plan'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Benefit plan updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:benefit_plan_detail', kwargs={'pk': self.object.pk})


class BenefitPlanDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(BenefitPlan, pk=pk, tenant=request.tenant)
        plan.delete()
        messages.success(request, 'Benefit plan deleted successfully.')
        return redirect('compensation:benefit_plan_list')


class EmployeeBenefitListView(LoginRequiredMixin, ListView):
    model = EmployeeBenefit
    template_name = 'compensation/employee_benefit_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        qs = EmployeeBenefit.objects.filter(tenant=self.request.tenant).select_related('employee', 'benefit_plan')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        plan = self.request.GET.get('plan', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(policy_number__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if plan:
            qs = qs.filter(benefit_plan_id=plan)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_plan'] = self.request.GET.get('plan', '')
        context['status_choices'] = EmployeeBenefit.STATUS_CHOICES
        context['plans'] = BenefitPlan.objects.filter(tenant=self.request.tenant, is_active=True)
        return context


class EmployeeBenefitCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeBenefit
    form_class = EmployeeBenefitForm
    template_name = 'compensation/employee_benefit_form.html'
    success_url = reverse_lazy('compensation:employee_benefit_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Employee Benefit Enrollment'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Employee benefit enrollment created successfully.')
        return super().form_valid(form)


class EmployeeBenefitUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeBenefit
    form_class = EmployeeBenefitForm
    template_name = 'compensation/employee_benefit_form.html'
    success_url = reverse_lazy('compensation:employee_benefit_list')

    def get_queryset(self):
        return EmployeeBenefit.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Employee Benefit Enrollment'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Employee benefit enrollment updated successfully.')
        return super().form_valid(form)


class EmployeeBenefitDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        enrollment = get_object_or_404(EmployeeBenefit, pk=pk, tenant=request.tenant)
        enrollment.delete()
        messages.success(request, 'Employee benefit enrollment deleted successfully.')
        return redirect('compensation:employee_benefit_list')


# ===========================================================================
# Flexible Benefits Views
# ===========================================================================

class FlexPlanListView(LoginRequiredMixin, ListView):
    model = FlexBenefitPlan
    template_name = 'compensation/flex_plan_list.html'
    context_object_name = 'plans'
    paginate_by = 20

    def get_queryset(self):
        qs = FlexBenefitPlan.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        return context


class FlexPlanCreateView(LoginRequiredMixin, CreateView):
    model = FlexBenefitPlan
    form_class = FlexBenefitPlanForm
    template_name = 'compensation/flex_plan_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Flexible Benefit Plan'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Flexible benefit plan created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:flex_plan_detail', kwargs={'pk': self.object.pk})


class FlexPlanDetailView(LoginRequiredMixin, DetailView):
    model = FlexBenefitPlan
    template_name = 'compensation/flex_plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return FlexBenefitPlan.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['options'] = self.object.options.all()
        context['selections'] = self.object.selections.select_related('employee', 'flex_option').all()[:20]
        return context


class FlexPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = FlexBenefitPlan
    form_class = FlexBenefitPlanForm
    template_name = 'compensation/flex_plan_form.html'

    def get_queryset(self):
        return FlexBenefitPlan.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Flexible Benefit Plan'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Flexible benefit plan updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:flex_plan_detail', kwargs={'pk': self.object.pk})


class FlexPlanDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(FlexBenefitPlan, pk=pk, tenant=request.tenant)
        plan.delete()
        messages.success(request, 'Flexible benefit plan deleted successfully.')
        return redirect('compensation:flex_plan_list')


class FlexOptionCreateView(LoginRequiredMixin, CreateView):
    model = FlexBenefitOption
    form_class = FlexBenefitOptionForm
    template_name = 'compensation/flex_option_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Flex Benefit Option'
        context['plan'] = get_object_or_404(FlexBenefitPlan, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.flex_plan_id = self.kwargs['pk']
        messages.success(self.request, 'Flex benefit option created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:flex_plan_detail', kwargs={'pk': self.kwargs['pk']})


class FlexOptionUpdateView(LoginRequiredMixin, UpdateView):
    model = FlexBenefitOption
    form_class = FlexBenefitOptionForm
    template_name = 'compensation/flex_option_form.html'

    def get_queryset(self):
        return FlexBenefitOption.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Flex Benefit Option'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Flex benefit option updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:flex_plan_detail', kwargs={'pk': self.object.flex_plan_id})


class FlexOptionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        option = get_object_or_404(FlexBenefitOption, pk=pk, tenant=request.tenant)
        plan_pk = option.flex_plan_id
        option.delete()
        messages.success(request, 'Flex benefit option deleted successfully.')
        return redirect('compensation:flex_plan_detail', pk=plan_pk)


class FlexSelectionListView(LoginRequiredMixin, ListView):
    model = EmployeeFlexSelection
    template_name = 'compensation/flex_selection_list.html'
    context_object_name = 'selections'
    paginate_by = 20

    def get_queryset(self):
        qs = EmployeeFlexSelection.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'flex_plan', 'flex_option')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        plan = self.request.GET.get('plan', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if plan:
            qs = qs.filter(flex_plan_id=plan)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_plan'] = self.request.GET.get('plan', '')
        context['status_choices'] = EmployeeFlexSelection.STATUS_CHOICES
        context['plans'] = FlexBenefitPlan.objects.filter(tenant=self.request.tenant, is_active=True)
        return context


class FlexSelectionCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeFlexSelection
    form_class = EmployeeFlexSelectionForm
    template_name = 'compensation/flex_selection_form.html'
    success_url = reverse_lazy('compensation:flex_selection_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Flex Benefit Selection'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Flex benefit selection created successfully.')
        return super().form_valid(form)


class FlexSelectionUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeFlexSelection
    form_class = EmployeeFlexSelectionForm
    template_name = 'compensation/flex_selection_form.html'
    success_url = reverse_lazy('compensation:flex_selection_list')

    def get_queryset(self):
        return EmployeeFlexSelection.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Flex Benefit Selection'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Flex benefit selection updated successfully.')
        return super().form_valid(form)


# ===========================================================================
# Stock/ESOP Management Views
# ===========================================================================

class EquityGrantListView(LoginRequiredMixin, ListView):
    model = EquityGrant
    template_name = 'compensation/equity_grant_list.html'
    context_object_name = 'grants'
    paginate_by = 20

    def get_queryset(self):
        qs = EquityGrant.objects.filter(tenant=self.request.tenant).select_related('employee')
        search = self.request.GET.get('search', '').strip()
        grant_type = self.request.GET.get('grant_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(grant_number__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if grant_type:
            qs = qs.filter(grant_type=grant_type)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_grant_type'] = self.request.GET.get('grant_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['grant_type_choices'] = EquityGrant.GRANT_TYPE_CHOICES
        context['status_choices'] = EquityGrant.STATUS_CHOICES
        return context


class EquityGrantCreateView(LoginRequiredMixin, CreateView):
    model = EquityGrant
    form_class = EquityGrantForm
    template_name = 'compensation/equity_grant_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Equity Grant'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Equity grant created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:equity_grant_detail', kwargs={'pk': self.object.pk})


class EquityGrantDetailView(LoginRequiredMixin, DetailView):
    model = EquityGrant
    template_name = 'compensation/equity_grant_detail.html'
    context_object_name = 'grant'

    def get_queryset(self):
        return EquityGrant.objects.filter(tenant=self.request.tenant).select_related('employee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vesting_events'] = self.object.vesting_events.all()
        context['exercise_records'] = self.object.exercise_records.all()
        return context


class EquityGrantUpdateView(LoginRequiredMixin, UpdateView):
    model = EquityGrant
    form_class = EquityGrantForm
    template_name = 'compensation/equity_grant_form.html'

    def get_queryset(self):
        return EquityGrant.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Equity Grant'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Equity grant updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:equity_grant_detail', kwargs={'pk': self.object.pk})


class EquityGrantDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        grant = get_object_or_404(EquityGrant, pk=pk, tenant=request.tenant)
        grant.delete()
        messages.success(request, 'Equity grant deleted successfully.')
        return redirect('compensation:equity_grant_list')


class VestingEventCreateView(LoginRequiredMixin, CreateView):
    model = VestingEvent
    form_class = VestingEventForm
    template_name = 'compensation/vesting_event_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Vesting Event'
        context['grant'] = get_object_or_404(EquityGrant, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.equity_grant_id = self.kwargs['pk']
        messages.success(self.request, 'Vesting event created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:equity_grant_detail', kwargs={'pk': self.kwargs['pk']})


class ExerciseRecordCreateView(LoginRequiredMixin, CreateView):
    model = ExerciseRecord
    form_class = ExerciseRecordForm
    template_name = 'compensation/exercise_record_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Exercise Record'
        context['grant'] = get_object_or_404(EquityGrant, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.equity_grant_id = self.kwargs['pk']
        messages.success(self.request, 'Exercise record created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:equity_grant_detail', kwargs={'pk': self.kwargs['pk']})


# ===========================================================================
# Compensation Planning Views
# ===========================================================================

class CompensationPlanListView(LoginRequiredMixin, ListView):
    model = CompensationPlan
    template_name = 'compensation/compensation_plan_list.html'
    context_object_name = 'plans'
    paginate_by = 20

    def get_queryset(self):
        qs = CompensationPlan.objects.filter(tenant=self.request.tenant).select_related('approved_by')
        search = self.request.GET.get('search', '').strip()
        plan_type = self.request.GET.get('plan_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(fiscal_year__icontains=search))
        if plan_type:
            qs = qs.filter(plan_type=plan_type)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_plan_type'] = self.request.GET.get('plan_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['plan_type_choices'] = CompensationPlan.PLAN_TYPE_CHOICES
        context['status_choices'] = CompensationPlan.STATUS_CHOICES
        return context


class CompensationPlanCreateView(LoginRequiredMixin, CreateView):
    model = CompensationPlan
    form_class = CompensationPlanForm
    template_name = 'compensation/compensation_plan_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Compensation Plan'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Compensation plan created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:compensation_plan_detail', kwargs={'pk': self.object.pk})


class CompensationPlanDetailView(LoginRequiredMixin, DetailView):
    model = CompensationPlan
    template_name = 'compensation/compensation_plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return CompensationPlan.objects.filter(tenant=self.request.tenant).select_related('approved_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recommendations'] = self.object.recommendations.select_related('employee').all()[:20]
        return context


class CompensationPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = CompensationPlan
    form_class = CompensationPlanForm
    template_name = 'compensation/compensation_plan_form.html'

    def get_queryset(self):
        return CompensationPlan.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Compensation Plan'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Compensation plan updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:compensation_plan_detail', kwargs={'pk': self.object.pk})


class CompensationPlanDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(CompensationPlan, pk=pk, tenant=request.tenant)
        plan.delete()
        messages.success(request, 'Compensation plan deleted successfully.')
        return redirect('compensation:compensation_plan_list')


class CompensationPlanApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(CompensationPlan, pk=pk, tenant=request.tenant)
        plan.status = 'approved'
        plan.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Compensation plan approved successfully.')
        return redirect('compensation:compensation_plan_detail', pk=pk)


class RecommendationListView(LoginRequiredMixin, ListView):
    model = CompensationRecommendation
    template_name = 'compensation/recommendation_list.html'
    context_object_name = 'recommendations'
    paginate_by = 20

    def get_queryset(self):
        qs = CompensationRecommendation.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'compensation_plan')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        increase_type = self.request.GET.get('increase_type', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if increase_type:
            qs = qs.filter(increase_type=increase_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_increase_type'] = self.request.GET.get('increase_type', '')
        context['status_choices'] = CompensationRecommendation.STATUS_CHOICES
        context['increase_type_choices'] = CompensationRecommendation.INCREASE_TYPE_CHOICES
        return context


class RecommendationCreateView(LoginRequiredMixin, CreateView):
    model = CompensationRecommendation
    form_class = CompensationRecommendationForm
    template_name = 'compensation/recommendation_form.html'
    success_url = reverse_lazy('compensation:recommendation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Compensation Recommendation'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Compensation recommendation created successfully.')
        return super().form_valid(form)


class RecommendationUpdateView(LoginRequiredMixin, UpdateView):
    model = CompensationRecommendation
    form_class = CompensationRecommendationForm
    template_name = 'compensation/recommendation_form.html'
    success_url = reverse_lazy('compensation:recommendation_list')

    def get_queryset(self):
        return CompensationRecommendation.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Compensation Recommendation'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Compensation recommendation updated successfully.')
        return super().form_valid(form)


class RecommendationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rec = get_object_or_404(CompensationRecommendation, pk=pk, tenant=request.tenant)
        rec.delete()
        messages.success(request, 'Compensation recommendation deleted successfully.')
        return redirect('compensation:recommendation_list')


class RecommendationApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rec = get_object_or_404(CompensationRecommendation, pk=pk, tenant=request.tenant)
        rec.status = 'approved'
        rec.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Recommendation approved successfully.')
        return redirect('compensation:recommendation_list')


class RecommendationRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rec = get_object_or_404(CompensationRecommendation, pk=pk, tenant=request.tenant)
        rec.status = 'rejected'
        rec.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Recommendation rejected.')
        return redirect('compensation:recommendation_list')


# ===========================================================================
# Rewards & Recognition Views
# ===========================================================================

class RewardProgramListView(LoginRequiredMixin, ListView):
    model = RewardProgram
    template_name = 'compensation/reward_program_list.html'
    context_object_name = 'programs'
    paginate_by = 20

    def get_queryset(self):
        qs = RewardProgram.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        program_type = self.request.GET.get('program_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))
        if program_type:
            qs = qs.filter(program_type=program_type)
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_program_type'] = self.request.GET.get('program_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['program_type_choices'] = RewardProgram.PROGRAM_TYPE_CHOICES
        return context


class RewardProgramCreateView(LoginRequiredMixin, CreateView):
    model = RewardProgram
    form_class = RewardProgramForm
    template_name = 'compensation/reward_program_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Reward Program'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Reward program created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:reward_program_detail', kwargs={'pk': self.object.pk})


class RewardProgramDetailView(LoginRequiredMixin, DetailView):
    model = RewardProgram
    template_name = 'compensation/reward_program_detail.html'
    context_object_name = 'program'

    def get_queryset(self):
        return RewardProgram.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recognitions'] = self.object.recognitions.select_related('nominee', 'nominator').all()[:20]
        return context


class RewardProgramUpdateView(LoginRequiredMixin, UpdateView):
    model = RewardProgram
    form_class = RewardProgramForm
    template_name = 'compensation/reward_program_form.html'

    def get_queryset(self):
        return RewardProgram.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Reward Program'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Reward program updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:reward_program_detail', kwargs={'pk': self.object.pk})


class RewardProgramDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        program = get_object_or_404(RewardProgram, pk=pk, tenant=request.tenant)
        program.delete()
        messages.success(request, 'Reward program deleted successfully.')
        return redirect('compensation:reward_program_list')


class RecognitionListView(LoginRequiredMixin, ListView):
    model = Recognition
    template_name = 'compensation/recognition_list.html'
    context_object_name = 'recognitions'
    paginate_by = 20

    def get_queryset(self):
        qs = Recognition.objects.filter(
            tenant=self.request.tenant
        ).select_related('reward_program', 'nominee', 'nominator')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        recognition_type = self.request.GET.get('recognition_type', '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(nominee__first_name__icontains=search) |
                Q(nominee__last_name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if recognition_type:
            qs = qs.filter(recognition_type=recognition_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_recognition_type'] = self.request.GET.get('recognition_type', '')
        context['status_choices'] = Recognition.STATUS_CHOICES
        context['recognition_type_choices'] = Recognition.RECOGNITION_TYPE_CHOICES
        return context


class RecognitionCreateView(LoginRequiredMixin, CreateView):
    model = Recognition
    form_class = RecognitionForm
    template_name = 'compensation/recognition_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Recognition'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Recognition created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:recognition_detail', kwargs={'pk': self.object.pk})


class RecognitionDetailView(LoginRequiredMixin, DetailView):
    model = Recognition
    template_name = 'compensation/recognition_detail.html'
    context_object_name = 'recognition'

    def get_queryset(self):
        return Recognition.objects.filter(
            tenant=self.request.tenant
        ).select_related('reward_program', 'nominee', 'nominator', 'approved_by')


class RecognitionUpdateView(LoginRequiredMixin, UpdateView):
    model = Recognition
    form_class = RecognitionForm
    template_name = 'compensation/recognition_form.html'

    def get_queryset(self):
        return Recognition.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Recognition'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Recognition updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compensation:recognition_detail', kwargs={'pk': self.object.pk})


class RecognitionApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recognition = get_object_or_404(Recognition, pk=pk, tenant=request.tenant)
        recognition.status = 'approved'
        recognition.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Recognition approved successfully.')
        return redirect('compensation:recognition_detail', pk=pk)


class RecognitionRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recognition = get_object_or_404(Recognition, pk=pk, tenant=request.tenant)
        recognition.status = 'rejected'
        recognition.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Recognition rejected.')
        return redirect('compensation:recognition_detail', pk=pk)
