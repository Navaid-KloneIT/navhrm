from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse

from apps.organization.models import Department

from .models import (
    DemandForecast, SkillInventory, TalentAvailability,
    WorkforceGap, HiringBudget, SalaryForecast,
    WorkforceScenario, ScenarioDetail,
    ProductivityMetric, UtilizationRate,
)
from .forms import (
    DemandForecastForm, SkillInventoryForm, TalentAvailabilityForm,
    WorkforceGapForm, HiringBudgetForm, SalaryForecastForm,
    WorkforceScenarioForm, ScenarioDetailForm,
    ProductivityMetricForm, UtilizationRateForm,
)


# ===========================================================================
# Demand Forecast Views
# ===========================================================================

class DemandForecastListView(LoginRequiredMixin, ListView):
    model = DemandForecast
    template_name = 'workforce/forecast_list.html'
    context_object_name = 'forecasts'
    paginate_by = 20

    def get_queryset(self):
        qs = DemandForecast.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        priority = self.request.GET.get('priority', '').strip()
        if search:
            qs = qs.filter(
                Q(department__name__icontains=search) |
                Q(designation__name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['status_choices'] = DemandForecast.STATUS_CHOICES
        context['priority_choices'] = DemandForecast.PRIORITY_CHOICES
        return context


class DemandForecastCreateView(LoginRequiredMixin, CreateView):
    model = DemandForecast
    form_class = DemandForecastForm
    template_name = 'workforce/forecast_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Demand Forecast'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Demand forecast created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:forecast_detail', kwargs={'pk': self.object.pk})


class DemandForecastDetailView(LoginRequiredMixin, DetailView):
    model = DemandForecast
    template_name = 'workforce/forecast_detail.html'
    context_object_name = 'forecast'

    def get_queryset(self):
        return DemandForecast.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')


class DemandForecastUpdateView(LoginRequiredMixin, UpdateView):
    model = DemandForecast
    form_class = DemandForecastForm
    template_name = 'workforce/forecast_form.html'

    def get_queryset(self):
        return DemandForecast.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Demand Forecast'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Demand forecast updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:forecast_detail', kwargs={'pk': self.object.pk})


class DemandForecastDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        forecast = get_object_or_404(DemandForecast, pk=pk, tenant=request.tenant)
        forecast.delete()
        messages.success(request, 'Demand forecast deleted successfully.')
        return redirect('workforce:forecast_list')


# ===========================================================================
# Skill Inventory Views
# ===========================================================================

class SkillInventoryListView(LoginRequiredMixin, ListView):
    model = SkillInventory
    template_name = 'workforce/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 20

    def get_queryset(self):
        qs = SkillInventory.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee')
        search = self.request.GET.get('search', '').strip()
        proficiency_level = self.request.GET.get('proficiency_level', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(skill_name__icontains=search)
            )
        if proficiency_level:
            qs = qs.filter(proficiency_level=proficiency_level)
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_proficiency_level'] = self.request.GET.get('proficiency_level', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['proficiency_choices'] = SkillInventory.PROFICIENCY_CHOICES
        return context


class SkillInventoryCreateView(LoginRequiredMixin, CreateView):
    model = SkillInventory
    form_class = SkillInventoryForm
    template_name = 'workforce/skill_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Skill Inventory'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Skill inventory created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:skill_detail', kwargs={'pk': self.object.pk})


class SkillInventoryDetailView(LoginRequiredMixin, DetailView):
    model = SkillInventory
    template_name = 'workforce/skill_detail.html'
    context_object_name = 'skill'

    def get_queryset(self):
        return SkillInventory.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee')


class SkillInventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = SkillInventory
    form_class = SkillInventoryForm
    template_name = 'workforce/skill_form.html'

    def get_queryset(self):
        return SkillInventory.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Skill Inventory'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Skill inventory updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:skill_detail', kwargs={'pk': self.object.pk})


class SkillInventoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        inventory = get_object_or_404(SkillInventory, pk=pk, tenant=request.tenant)
        inventory.delete()
        messages.success(request, 'Skill inventory deleted successfully.')
        return redirect('workforce:skill_list')


# ===========================================================================
# Talent Availability Views
# ===========================================================================

class TalentAvailabilityListView(LoginRequiredMixin, ListView):
    model = TalentAvailability
    template_name = 'workforce/availability_list.html'
    context_object_name = 'availabilities'
    paginate_by = 20

    def get_queryset(self):
        qs = TalentAvailability.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')
        search = self.request.GET.get('search', '').strip()
        department = self.request.GET.get('department', '').strip()
        if search:
            qs = qs.filter(
                Q(department__name__icontains=search)
            )
        if department:
            qs = qs.filter(department_id=department)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_department'] = self.request.GET.get('department', '')
        context['departments'] = Department.objects.filter(tenant=self.request.tenant)
        return context


class TalentAvailabilityCreateView(LoginRequiredMixin, CreateView):
    model = TalentAvailability
    form_class = TalentAvailabilityForm
    template_name = 'workforce/availability_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Talent Availability'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Talent availability created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:availability_detail', kwargs={'pk': self.object.pk})


class TalentAvailabilityDetailView(LoginRequiredMixin, DetailView):
    model = TalentAvailability
    template_name = 'workforce/availability_detail.html'
    context_object_name = 'availability'

    def get_queryset(self):
        return TalentAvailability.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')


class TalentAvailabilityUpdateView(LoginRequiredMixin, UpdateView):
    model = TalentAvailability
    form_class = TalentAvailabilityForm
    template_name = 'workforce/availability_form.html'

    def get_queryset(self):
        return TalentAvailability.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Talent Availability'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Talent availability updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:availability_detail', kwargs={'pk': self.object.pk})


class TalentAvailabilityDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        availability = get_object_or_404(TalentAvailability, pk=pk, tenant=request.tenant)
        availability.delete()
        messages.success(request, 'Talent availability deleted successfully.')
        return redirect('workforce:availability_list')


# ===========================================================================
# Workforce Gap Views
# ===========================================================================

class WorkforceGapListView(LoginRequiredMixin, ListView):
    model = WorkforceGap
    template_name = 'workforce/gap_list.html'
    context_object_name = 'gaps'
    paginate_by = 20

    def get_queryset(self):
        qs = WorkforceGap.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')
        search = self.request.GET.get('search', '').strip()
        gap_type = self.request.GET.get('gap_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        priority = self.request.GET.get('priority', '').strip()
        if search:
            qs = qs.filter(
                Q(department__name__icontains=search) |
                Q(designation__name__icontains=search)
            )
        if gap_type:
            qs = qs.filter(gap_type=gap_type)
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_gap_type'] = self.request.GET.get('gap_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['gap_type_choices'] = WorkforceGap.GAP_TYPE_CHOICES
        context['status_choices'] = WorkforceGap.STATUS_CHOICES
        context['priority_choices'] = WorkforceGap.PRIORITY_CHOICES
        return context


class WorkforceGapCreateView(LoginRequiredMixin, CreateView):
    model = WorkforceGap
    form_class = WorkforceGapForm
    template_name = 'workforce/gap_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Workforce Gap'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Workforce gap created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:gap_detail', kwargs={'pk': self.object.pk})


class WorkforceGapDetailView(LoginRequiredMixin, DetailView):
    model = WorkforceGap
    template_name = 'workforce/gap_detail.html'
    context_object_name = 'gap'

    def get_queryset(self):
        return WorkforceGap.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')


class WorkforceGapUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkforceGap
    form_class = WorkforceGapForm
    template_name = 'workforce/gap_form.html'

    def get_queryset(self):
        return WorkforceGap.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Workforce Gap'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Workforce gap updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:gap_detail', kwargs={'pk': self.object.pk})


class WorkforceGapDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        gap = get_object_or_404(WorkforceGap, pk=pk, tenant=request.tenant)
        gap.delete()
        messages.success(request, 'Workforce gap deleted successfully.')
        return redirect('workforce:gap_list')


# ===========================================================================
# Hiring Budget Views
# ===========================================================================

class HiringBudgetListView(LoginRequiredMixin, ListView):
    model = HiringBudget
    template_name = 'workforce/hiring_budget_list.html'
    context_object_name = 'budgets'
    paginate_by = 20

    def get_queryset(self):
        qs = HiringBudget.objects.filter(
            tenant=self.request.tenant
        ).select_related('department')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(department__name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = HiringBudget.STATUS_CHOICES
        return context


class HiringBudgetCreateView(LoginRequiredMixin, CreateView):
    model = HiringBudget
    form_class = HiringBudgetForm
    template_name = 'workforce/hiring_budget_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Hiring Budget'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Hiring budget created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:hiring_budget_detail', kwargs={'pk': self.object.pk})


class HiringBudgetDetailView(LoginRequiredMixin, DetailView):
    model = HiringBudget
    template_name = 'workforce/hiring_budget_detail.html'
    context_object_name = 'budget'

    def get_queryset(self):
        return HiringBudget.objects.filter(
            tenant=self.request.tenant
        ).select_related('department')


class HiringBudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = HiringBudget
    form_class = HiringBudgetForm
    template_name = 'workforce/hiring_budget_form.html'

    def get_queryset(self):
        return HiringBudget.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Hiring Budget'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Hiring budget updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:hiring_budget_detail', kwargs={'pk': self.object.pk})


class HiringBudgetDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        budget = get_object_or_404(HiringBudget, pk=pk, tenant=request.tenant)
        budget.delete()
        messages.success(request, 'Hiring budget deleted successfully.')
        return redirect('workforce:hiring_budget_list')


# ===========================================================================
# Salary Forecast Views
# ===========================================================================

class SalaryForecastListView(LoginRequiredMixin, ListView):
    model = SalaryForecast
    template_name = 'workforce/salary_forecast_list.html'
    context_object_name = 'forecasts'
    paginate_by = 20

    def get_queryset(self):
        qs = SalaryForecast.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')
        search = self.request.GET.get('search', '').strip()
        department = self.request.GET.get('department', '').strip()
        if search:
            qs = qs.filter(
                Q(department__name__icontains=search) |
                Q(designation__name__icontains=search)
            )
        if department:
            qs = qs.filter(department_id=department)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_department'] = self.request.GET.get('department', '')
        context['departments'] = Department.objects.filter(tenant=self.request.tenant)
        return context


class SalaryForecastCreateView(LoginRequiredMixin, CreateView):
    model = SalaryForecast
    form_class = SalaryForecastForm
    template_name = 'workforce/salary_forecast_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Salary Forecast'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Salary forecast created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:salary_forecast_detail', kwargs={'pk': self.object.pk})


class SalaryForecastDetailView(LoginRequiredMixin, DetailView):
    model = SalaryForecast
    template_name = 'workforce/salary_forecast_detail.html'
    context_object_name = 'forecast'

    def get_queryset(self):
        return SalaryForecast.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'designation')


class SalaryForecastUpdateView(LoginRequiredMixin, UpdateView):
    model = SalaryForecast
    form_class = SalaryForecastForm
    template_name = 'workforce/salary_forecast_form.html'

    def get_queryset(self):
        return SalaryForecast.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Salary Forecast'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Salary forecast updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:salary_forecast_detail', kwargs={'pk': self.object.pk})


class SalaryForecastDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        forecast = get_object_or_404(SalaryForecast, pk=pk, tenant=request.tenant)
        forecast.delete()
        messages.success(request, 'Salary forecast deleted successfully.')
        return redirect('workforce:salary_forecast_list')


# ===========================================================================
# Workforce Scenario Views
# ===========================================================================

class WorkforceScenarioListView(LoginRequiredMixin, ListView):
    model = WorkforceScenario
    template_name = 'workforce/scenario_list.html'
    context_object_name = 'scenarios'
    paginate_by = 20

    def get_queryset(self):
        qs = WorkforceScenario.objects.filter(
            tenant=self.request.tenant
        ).select_related('created_by')
        search = self.request.GET.get('search', '').strip()
        scenario_type = self.request.GET.get('scenario_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
            )
        if scenario_type:
            qs = qs.filter(scenario_type=scenario_type)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_scenario_type'] = self.request.GET.get('scenario_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['scenario_type_choices'] = WorkforceScenario.SCENARIO_TYPE_CHOICES
        context['status_choices'] = WorkforceScenario.STATUS_CHOICES
        return context


class WorkforceScenarioCreateView(LoginRequiredMixin, CreateView):
    model = WorkforceScenario
    form_class = WorkforceScenarioForm
    template_name = 'workforce/scenario_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Workforce Scenario'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Workforce scenario created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:scenario_detail', kwargs={'pk': self.object.pk})


class WorkforceScenarioDetailView(LoginRequiredMixin, DetailView):
    model = WorkforceScenario
    template_name = 'workforce/scenario_detail.html'
    context_object_name = 'scenario'

    def get_queryset(self):
        return WorkforceScenario.objects.filter(
            tenant=self.request.tenant
        ).select_related('created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.select_related(
            'department', 'designation'
        ).all()
        return context


class WorkforceScenarioUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkforceScenario
    form_class = WorkforceScenarioForm
    template_name = 'workforce/scenario_form.html'

    def get_queryset(self):
        return WorkforceScenario.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Workforce Scenario'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Workforce scenario updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:scenario_detail', kwargs={'pk': self.object.pk})


class WorkforceScenarioDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        scenario = get_object_or_404(WorkforceScenario, pk=pk, tenant=request.tenant)
        scenario.delete()
        messages.success(request, 'Workforce scenario deleted successfully.')
        return redirect('workforce:scenario_list')


# ===========================================================================
# Scenario Detail Views (child of WorkforceScenario)
# ===========================================================================

class ScenarioDetailCreateView(LoginRequiredMixin, CreateView):
    model = ScenarioDetail
    form_class = ScenarioDetailForm
    template_name = 'workforce/scenario_detail_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Scenario Detail'
        context['scenario'] = get_object_or_404(
            WorkforceScenario, pk=self.kwargs['scenario_pk'], tenant=self.request.tenant
        )
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.scenario = get_object_or_404(
            WorkforceScenario, pk=self.kwargs['scenario_pk'], tenant=self.request.tenant
        )
        messages.success(self.request, 'Scenario detail added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:scenario_detail', kwargs={'pk': self.kwargs['scenario_pk']})


class ScenarioDetailUpdateView(LoginRequiredMixin, UpdateView):
    model = ScenarioDetail
    form_class = ScenarioDetailForm
    template_name = 'workforce/scenario_detail_form.html'

    def get_queryset(self):
        return ScenarioDetail.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Scenario Detail'
        context['scenario'] = self.object.scenario
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Scenario detail updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:scenario_detail', kwargs={'pk': self.object.scenario.pk})


class ScenarioDetailDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        detail = get_object_or_404(ScenarioDetail, pk=pk, tenant=request.tenant)
        scenario_pk = detail.scenario.pk
        detail.delete()
        messages.success(request, 'Scenario detail deleted successfully.')
        return redirect('workforce:scenario_detail', pk=scenario_pk)


# ===========================================================================
# Productivity Metric Views
# ===========================================================================

class ProductivityMetricListView(LoginRequiredMixin, ListView):
    model = ProductivityMetric
    template_name = 'workforce/productivity_list.html'
    context_object_name = 'metrics'
    paginate_by = 20

    def get_queryset(self):
        qs = ProductivityMetric.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'employee')
        search = self.request.GET.get('search', '').strip()
        department = self.request.GET.get('department', '').strip()
        if search:
            qs = qs.filter(
                Q(metric_name__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if department:
            qs = qs.filter(department_id=department)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_department'] = self.request.GET.get('department', '')
        context['departments'] = Department.objects.filter(tenant=self.request.tenant)
        return context


class ProductivityMetricCreateView(LoginRequiredMixin, CreateView):
    model = ProductivityMetric
    form_class = ProductivityMetricForm
    template_name = 'workforce/productivity_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Productivity Metric'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Productivity metric created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:productivity_detail', kwargs={'pk': self.object.pk})


class ProductivityMetricDetailView(LoginRequiredMixin, DetailView):
    model = ProductivityMetric
    template_name = 'workforce/productivity_detail.html'
    context_object_name = 'metric'

    def get_queryset(self):
        return ProductivityMetric.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'employee')


class ProductivityMetricUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductivityMetric
    form_class = ProductivityMetricForm
    template_name = 'workforce/productivity_form.html'

    def get_queryset(self):
        return ProductivityMetric.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Productivity Metric'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Productivity metric updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:productivity_detail', kwargs={'pk': self.object.pk})


class ProductivityMetricDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        metric = get_object_or_404(ProductivityMetric, pk=pk, tenant=request.tenant)
        metric.delete()
        messages.success(request, 'Productivity metric deleted successfully.')
        return redirect('workforce:productivity_list')


# ===========================================================================
# Utilization Rate Views
# ===========================================================================

class UtilizationRateListView(LoginRequiredMixin, ListView):
    model = UtilizationRate
    template_name = 'workforce/utilization_list.html'
    context_object_name = 'rates'
    paginate_by = 20

    def get_queryset(self):
        qs = UtilizationRate.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'employee')
        search = self.request.GET.get('search', '').strip()
        department = self.request.GET.get('department', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(department__name__icontains=search)
            )
        if department:
            qs = qs.filter(department_id=department)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_department'] = self.request.GET.get('department', '')
        context['departments'] = Department.objects.filter(tenant=self.request.tenant)
        return context


class UtilizationRateCreateView(LoginRequiredMixin, CreateView):
    model = UtilizationRate
    form_class = UtilizationRateForm
    template_name = 'workforce/utilization_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Utilization Rate'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Utilization rate created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:utilization_detail', kwargs={'pk': self.object.pk})


class UtilizationRateDetailView(LoginRequiredMixin, DetailView):
    model = UtilizationRate
    template_name = 'workforce/utilization_detail.html'
    context_object_name = 'rate'

    def get_queryset(self):
        return UtilizationRate.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'employee')


class UtilizationRateUpdateView(LoginRequiredMixin, UpdateView):
    model = UtilizationRate
    form_class = UtilizationRateForm
    template_name = 'workforce/utilization_form.html'

    def get_queryset(self):
        return UtilizationRate.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Utilization Rate'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Utilization rate updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workforce:utilization_detail', kwargs={'pk': self.object.pk})


class UtilizationRateDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rate = get_object_or_404(UtilizationRate, pk=pk, tenant=request.tenant)
        rate.delete()
        messages.success(request, 'Utilization rate deleted successfully.')
        return redirect('workforce:utilization_list')
