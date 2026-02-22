from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.utils import timezone

from .models import (
    Resignation, ExitInterview, ClearanceProcess, ClearanceItem,
    ClearanceChecklistItem, FnFSettlement, ExperienceLetter
)
from .forms import (
    ResignationForm, ExitInterviewForm, ExitInterviewFeedbackForm,
    ClearanceProcessForm, FnFSettlementForm, ExperienceLetterForm
)
from apps.employees.models import Employee


# ---------------------------------------------------------------------------
# Resignation Views
# ---------------------------------------------------------------------------

class ResignationListView(LoginRequiredMixin, ListView):
    model = Resignation
    template_name = 'offboarding/resignation_list.html'
    context_object_name = 'resignations'
    paginate_by = 20

    def get_queryset(self):
        qs = Resignation.all_objects.filter(tenant=self.request.tenant)
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


class ResignationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ResignationForm(tenant=request.tenant)
        return render(request, 'offboarding/resignation_form.html', {
            'form': form,
            'title': 'Submit Resignation',
        })

    def post(self, request):
        form = ResignationForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            resignation = form.save(commit=False)
            resignation.tenant = request.tenant
            resignation.save()
            messages.success(request, 'Resignation submitted successfully.')
            return redirect('offboarding:resignation_detail', pk=resignation.pk)
        return render(request, 'offboarding/resignation_form.html', {
            'form': form,
            'title': 'Submit Resignation',
        })


class ResignationDetailView(LoginRequiredMixin, DetailView):
    model = Resignation
    template_name = 'offboarding/resignation_detail.html'
    context_object_name = 'resignation'

    def get_queryset(self):
        return Resignation.all_objects.filter(tenant=self.request.tenant)


class ResignationApproveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        resignation = get_object_or_404(
            Resignation.all_objects, pk=pk, tenant=request.tenant
        )
        return render(request, 'offboarding/resignation_approve.html', {
            'resignation': resignation,
        })

    def post(self, request, pk):
        resignation = get_object_or_404(
            Resignation.all_objects, pk=pk, tenant=request.tenant
        )
        action = request.POST.get('action', '')
        if action == 'approve':
            resignation.status = 'approved'
            resignation.approved_by = request.user
            resignation.approved_date = timezone.now().date()
            resignation.save()
            messages.success(
                request,
                f'Resignation for {resignation.employee} has been approved.'
            )
        elif action == 'reject':
            resignation.status = 'rejected'
            resignation.save()
            messages.warning(
                request,
                f'Resignation for {resignation.employee} has been rejected.'
            )
        return redirect('offboarding:resignation_detail', pk=resignation.pk)


# ---------------------------------------------------------------------------
# Exit Interview Views
# ---------------------------------------------------------------------------

class ExitInterviewListView(LoginRequiredMixin, ListView):
    model = ExitInterview
    template_name = 'offboarding/exitinterview_list.html'
    context_object_name = 'interviews'
    paginate_by = 20

    def get_queryset(self):
        qs = ExitInterview.all_objects.filter(tenant=self.request.tenant)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs


class ExitInterviewCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ExitInterviewForm(tenant=request.tenant)
        return render(request, 'offboarding/exitinterview_form.html', {
            'form': form,
            'title': 'Schedule Exit Interview',
        })

    def post(self, request):
        form = ExitInterviewForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.tenant = request.tenant
            interview.save()
            messages.success(
                request,
                f'Exit interview scheduled for {interview.employee}.'
            )
            return redirect('offboarding:exitinterview_detail', pk=interview.pk)
        return render(request, 'offboarding/exitinterview_form.html', {
            'form': form,
            'title': 'Schedule Exit Interview',
        })


class ExitInterviewDetailView(LoginRequiredMixin, DetailView):
    model = ExitInterview
    template_name = 'offboarding/exitinterview_detail.html'
    context_object_name = 'interview'

    def get_queryset(self):
        return ExitInterview.all_objects.filter(tenant=self.request.tenant)


class ExitInterviewFeedbackView(LoginRequiredMixin, View):
    def get(self, request, pk):
        interview = get_object_or_404(
            ExitInterview.all_objects, pk=pk, tenant=request.tenant
        )
        form = ExitInterviewFeedbackForm(instance=interview)
        return render(request, 'offboarding/exitinterview_feedback.html', {
            'form': form,
            'interview': interview,
            'title': 'Exit Interview Feedback',
        })

    def post(self, request, pk):
        interview = get_object_or_404(
            ExitInterview.all_objects, pk=pk, tenant=request.tenant
        )
        form = ExitInterviewFeedbackForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.status = 'completed'
            interview.save()
            messages.success(request, 'Exit interview feedback recorded.')
            return redirect('offboarding:exitinterview_detail', pk=interview.pk)
        return render(request, 'offboarding/exitinterview_feedback.html', {
            'form': form,
            'interview': interview,
            'title': 'Exit Interview Feedback',
        })


# ---------------------------------------------------------------------------
# Clearance Views
# ---------------------------------------------------------------------------

class ClearanceListView(LoginRequiredMixin, ListView):
    model = ClearanceProcess
    template_name = 'offboarding/clearance_list.html'
    context_object_name = 'clearances'
    paginate_by = 20

    def get_queryset(self):
        qs = ClearanceProcess.all_objects.filter(tenant=self.request.tenant)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs


class ClearanceInitiateView(LoginRequiredMixin, View):
    def get(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = ClearanceProcessForm(tenant=request.tenant)
        form.initial['employee'] = employee.pk
        form.initial['initiated_date'] = timezone.now().date()
        return render(request, 'offboarding/clearance_form.html', {
            'form': form,
            'employee': employee,
            'title': 'Initiate Clearance',
        })

    def post(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = ClearanceProcessForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            clearance = form.save(commit=False)
            clearance.tenant = request.tenant
            clearance.save()
            # Create checklist items from clearance items
            clearance_items = ClearanceItem.all_objects.filter(tenant=request.tenant)
            for item in clearance_items:
                ClearanceChecklistItem.objects.create(
                    tenant=request.tenant,
                    process=clearance,
                    clearance_item=item,
                )
            messages.success(
                request,
                f'Clearance process initiated for {employee.full_name}.'
            )
            return redirect('offboarding:clearance_detail', pk=clearance.pk)
        return render(request, 'offboarding/clearance_form.html', {
            'form': form,
            'employee': employee,
            'title': 'Initiate Clearance',
        })


class ClearanceDetailView(LoginRequiredMixin, DetailView):
    model = ClearanceProcess
    template_name = 'offboarding/clearance_detail.html'
    context_object_name = 'clearance'

    def get_queryset(self):
        return ClearanceProcess.all_objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['checklist_items'] = self.object.checklist_items.select_related(
            'clearance_item'
        ).all()
        return context


# ---------------------------------------------------------------------------
# F&F Settlement Views
# ---------------------------------------------------------------------------

class FnFListView(LoginRequiredMixin, ListView):
    model = FnFSettlement
    template_name = 'offboarding/fnf_list.html'
    context_object_name = 'settlements'
    paginate_by = 20

    def get_queryset(self):
        qs = FnFSettlement.all_objects.filter(tenant=self.request.tenant)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs


class FnFCreateView(LoginRequiredMixin, View):
    def get(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = FnFSettlementForm()
        form.initial['settlement_date'] = timezone.now().date()
        form.initial['basic_salary'] = employee.salary or 0
        return render(request, 'offboarding/fnf_form.html', {
            'form': form,
            'employee': employee,
            'title': 'Create F&F Settlement',
        })

    def post(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = FnFSettlementForm(request.POST)
        if form.is_valid():
            settlement = form.save(commit=False)
            settlement.tenant = request.tenant
            settlement.employee = employee
            settlement.save()
            messages.success(
                request,
                f'F&F settlement created for {employee.full_name}.'
            )
            return redirect('offboarding:fnf_detail', pk=settlement.pk)
        return render(request, 'offboarding/fnf_form.html', {
            'form': form,
            'employee': employee,
            'title': 'Create F&F Settlement',
        })


class FnFDetailView(LoginRequiredMixin, DetailView):
    model = FnFSettlement
    template_name = 'offboarding/fnf_detail.html'
    context_object_name = 'settlement'

    def get_queryset(self):
        return FnFSettlement.all_objects.filter(tenant=self.request.tenant)


# ---------------------------------------------------------------------------
# Experience Letter Views
# ---------------------------------------------------------------------------

class ExperienceLetterListView(LoginRequiredMixin, ListView):
    model = ExperienceLetter
    template_name = 'offboarding/letter_list.html'
    context_object_name = 'letters'
    paginate_by = 20

    def get_queryset(self):
        return ExperienceLetter.all_objects.filter(tenant=self.request.tenant)


class ExperienceLetterGenerateView(LoginRequiredMixin, View):
    def get(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = ExperienceLetterForm(tenant=request.tenant)
        form.initial['employee'] = employee.pk
        form.initial['letter_date'] = timezone.now().date()
        return render(request, 'offboarding/letter_form.html', {
            'form': form,
            'employee': employee,
            'title': 'Generate Letter',
        })

    def post(self, request, employee_id):
        employee = get_object_or_404(
            Employee.all_objects, pk=employee_id, tenant=request.tenant
        )
        form = ExperienceLetterForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            letter = form.save(commit=False)
            letter.tenant = request.tenant
            letter.generated_by = request.user
            letter.save()
            messages.success(
                request,
                f'{letter.get_letter_type_display()} generated for {employee.full_name}.'
            )
            return redirect('offboarding:letter_detail', pk=letter.pk)
        return render(request, 'offboarding/letter_form.html', {
            'form': form,
            'employee': employee,
            'title': 'Generate Letter',
        })


class ExperienceLetterDetailView(LoginRequiredMixin, DetailView):
    model = ExperienceLetter
    template_name = 'offboarding/letter_detail.html'
    context_object_name = 'letter'

    def get_queryset(self):
        return ExperienceLetter.all_objects.filter(tenant=self.request.tenant)
