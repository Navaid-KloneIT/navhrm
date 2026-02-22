from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.utils import timezone

from .models import (
    OnboardingProcess, OnboardingTask, OnboardingTemplate,
    OnboardingTemplateTask, AssetAllocation, OrientationSession, WelcomeKit
)
from .forms import (
    OnboardingProcessForm, OnboardingTaskForm, OnboardingTemplateForm,
    AssetAllocationForm, OrientationSessionForm, WelcomeKitForm
)
from apps.employees.models import Employee


# ---------------------------------------------------------------------------
# Onboarding Process Views
# ---------------------------------------------------------------------------

class OnboardingListView(LoginRequiredMixin, ListView):
    model = OnboardingProcess
    template_name = 'onboarding/list.html'
    context_object_name = 'processes'
    paginate_by = 20

    def get_queryset(self):
        qs = OnboardingProcess.all_objects.filter(tenant=self.request.tenant)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                employee__first_name__icontains=search
            ) | qs.filter(
                employee__last_name__icontains=search
            )
        return qs


class OnboardingCreateView(LoginRequiredMixin, View):
    def get(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = OnboardingProcessForm(tenant=request.tenant)
        form.initial['employee'] = employee.pk
        return render(request, 'onboarding/form.html', {
            'form': form,
            'title': 'Start Onboarding',
            'employee': employee,
        })

    def post(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = OnboardingProcessForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            process = form.save(commit=False)
            process.tenant = request.tenant
            process.save()
            # If a template was selected, create tasks from it
            if process.template:
                template_tasks = OnboardingTemplateTask.all_objects.filter(
                    template=process.template, tenant=request.tenant
                )
                for tt in template_tasks:
                    OnboardingTask.objects.create(
                        tenant=request.tenant,
                        process=process,
                        title=tt.title,
                        description=tt.description,
                        is_mandatory=tt.is_mandatory,
                        order=tt.order,
                    )
            messages.success(request, f'Onboarding started for {employee.full_name}.')
            return redirect('onboarding:detail', pk=process.pk)
        return render(request, 'onboarding/form.html', {
            'form': form,
            'title': 'Start Onboarding',
            'employee': employee,
        })


class OnboardingDetailView(LoginRequiredMixin, DetailView):
    model = OnboardingProcess
    template_name = 'onboarding/detail.html'
    context_object_name = 'process'

    def get_queryset(self):
        return OnboardingProcess.all_objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all()
        return context


class TaskUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, task_id):
        process = get_object_or_404(
            OnboardingProcess.all_objects, pk=pk, tenant=request.tenant
        )
        task = get_object_or_404(OnboardingTask.all_objects, pk=task_id, process=process)
        form = OnboardingTaskForm(instance=task, tenant=request.tenant)
        return render(request, 'onboarding/task_form.html', {
            'form': form,
            'process': process,
            'task': task,
            'title': 'Update Task',
        })

    def post(self, request, pk, task_id):
        process = get_object_or_404(
            OnboardingProcess.all_objects, pk=pk, tenant=request.tenant
        )
        task = get_object_or_404(OnboardingTask.all_objects, pk=task_id, process=process)
        form = OnboardingTaskForm(request.POST, instance=task, tenant=request.tenant)
        if form.is_valid():
            updated_task = form.save(commit=False)
            # Mark completed date if status changed to completed
            status = request.POST.get('status', '')
            if status:
                updated_task.status = status
            if updated_task.status == 'completed' and not updated_task.completed_date:
                updated_task.completed_date = timezone.now().date()
            updated_task.save()
            messages.success(request, f'Task "{task.title}" updated.')
            return redirect('onboarding:detail', pk=process.pk)
        return render(request, 'onboarding/task_form.html', {
            'form': form,
            'process': process,
            'task': task,
            'title': 'Update Task',
        })


# ---------------------------------------------------------------------------
# Template Views
# ---------------------------------------------------------------------------

class TemplateListView(LoginRequiredMixin, ListView):
    model = OnboardingTemplate
    template_name = 'onboarding/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

    def get_queryset(self):
        return OnboardingTemplate.all_objects.filter(tenant=self.request.tenant)


class TemplateCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = OnboardingTemplateForm(tenant=request.tenant)
        return render(request, 'onboarding/template_form.html', {
            'form': form,
            'title': 'Create Template',
        })

    def post(self, request):
        form = OnboardingTemplateForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            template = form.save(commit=False)
            template.tenant = request.tenant
            template.save()
            messages.success(request, f'Template "{template.name}" created.')
            return redirect('onboarding:template_list')
        return render(request, 'onboarding/template_form.html', {
            'form': form,
            'title': 'Create Template',
        })


class TemplateUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        template = get_object_or_404(
            OnboardingTemplate.all_objects, pk=pk, tenant=request.tenant
        )
        form = OnboardingTemplateForm(instance=template, tenant=request.tenant)
        return render(request, 'onboarding/template_form.html', {
            'form': form,
            'title': 'Edit Template',
            'template_obj': template,
        })

    def post(self, request, pk):
        template = get_object_or_404(
            OnboardingTemplate.all_objects, pk=pk, tenant=request.tenant
        )
        form = OnboardingTemplateForm(request.POST, instance=template, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Template "{template.name}" updated.')
            return redirect('onboarding:template_list')
        return render(request, 'onboarding/template_form.html', {
            'form': form,
            'title': 'Edit Template',
            'template_obj': template,
        })


# ---------------------------------------------------------------------------
# Asset Views
# ---------------------------------------------------------------------------

class AssetListView(LoginRequiredMixin, ListView):
    model = AssetAllocation
    template_name = 'onboarding/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20

    def get_queryset(self):
        qs = AssetAllocation.all_objects.filter(tenant=self.request.tenant)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(asset_name__icontains=search)
        return qs


class AssetAllocateView(LoginRequiredMixin, View):
    def get(self, request):
        form = AssetAllocationForm(tenant=request.tenant)
        return render(request, 'onboarding/asset_form.html', {
            'form': form,
            'title': 'Allocate Asset',
        })

    def post(self, request):
        form = AssetAllocationForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.tenant = request.tenant
            asset.save()
            messages.success(request, f'Asset "{asset.asset_name}" allocated to {asset.employee}.')
            return redirect('onboarding:asset_list')
        return render(request, 'onboarding/asset_form.html', {
            'form': form,
            'title': 'Allocate Asset',
        })


class AssetReturnView(LoginRequiredMixin, View):
    def get(self, request, pk):
        asset = get_object_or_404(
            AssetAllocation.all_objects, pk=pk, tenant=request.tenant
        )
        return render(request, 'onboarding/asset_return.html', {'asset': asset})

    def post(self, request, pk):
        asset = get_object_or_404(
            AssetAllocation.all_objects, pk=pk, tenant=request.tenant
        )
        asset.status = 'returned'
        asset.returned_date = timezone.now().date()
        asset.save()
        messages.success(request, f'Asset "{asset.asset_name}" marked as returned.')
        return redirect('onboarding:asset_list')


# ---------------------------------------------------------------------------
# Orientation Views
# ---------------------------------------------------------------------------

class OrientationListView(LoginRequiredMixin, ListView):
    model = OrientationSession
    template_name = 'onboarding/orientation_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        return OrientationSession.all_objects.filter(tenant=self.request.tenant)


class OrientationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = OrientationSessionForm(tenant=request.tenant)
        return render(request, 'onboarding/orientation_form.html', {
            'form': form,
            'title': 'Schedule Orientation',
        })

    def post(self, request):
        form = OrientationSessionForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            session = form.save(commit=False)
            session.tenant = request.tenant
            session.save()
            messages.success(request, f'Orientation session "{session.title}" scheduled.')
            return redirect('onboarding:orientation_list')
        return render(request, 'onboarding/orientation_form.html', {
            'form': form,
            'title': 'Schedule Orientation',
        })


# ---------------------------------------------------------------------------
# Welcome Kit Views
# ---------------------------------------------------------------------------

class WelcomeKitListView(LoginRequiredMixin, ListView):
    model = WelcomeKit
    template_name = 'onboarding/welcomekit_list.html'
    context_object_name = 'kits'
    paginate_by = 20

    def get_queryset(self):
        return WelcomeKit.all_objects.filter(tenant=self.request.tenant)


class WelcomeKitCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = WelcomeKitForm()
        return render(request, 'onboarding/welcomekit_form.html', {
            'form': form,
            'title': 'Create Welcome Kit',
        })

    def post(self, request):
        form = WelcomeKitForm(request.POST)
        if form.is_valid():
            kit = form.save(commit=False)
            kit.tenant = request.tenant
            kit.save()
            messages.success(request, f'Welcome kit "{kit.name}" created.')
            return redirect('onboarding:welcomekit_list')
        return render(request, 'onboarding/welcomekit_form.html', {
            'form': form,
            'title': 'Create Welcome Kit',
        })
