from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from .models import (
    LaborLaw, LaborLawCompliance,
    EmploymentContract, ContractAmendment,
    CompliancePolicy, PolicyVersion, PolicyAcknowledgment,
    DisciplinaryIncident, WarningRecord, DisciplinaryAppeal,
    Grievance, GrievanceInvestigation,
    MusterRoll, WageRegister, InspectionReport,
)
from .forms import (
    LaborLawForm, LaborLawComplianceForm,
    EmploymentContractForm, ContractAmendmentForm,
    CompliancePolicyForm, PolicyVersionForm, PolicyAcknowledgmentForm,
    DisciplinaryIncidentForm, WarningRecordForm, DisciplinaryAppealForm,
    GrievanceForm, GrievanceInvestigationForm,
    MusterRollForm, WageRegisterForm, InspectionReportForm,
)


# ===========================================================================
# Labor Law Compliance Views
# ===========================================================================

class LaborLawListView(LoginRequiredMixin, ListView):
    model = LaborLaw
    template_name = 'compliance/labor_law_list.html'
    context_object_name = 'laws'
    paginate_by = 20

    def get_queryset(self):
        qs = LaborLaw.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(jurisdiction__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = LaborLaw.CATEGORY_CHOICES
        context['status_choices'] = LaborLaw.STATUS_CHOICES
        return context


class LaborLawDetailView(LoginRequiredMixin, DetailView):
    model = LaborLaw
    template_name = 'compliance/labor_law_detail.html'
    context_object_name = 'law'

    def get_queryset(self):
        return LaborLaw.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compliance_records'] = LaborLawCompliance.objects.filter(
            tenant=self.request.tenant, labor_law=self.object
        ).select_related('department', 'responsible_person')
        return context


class LaborLawCreateView(LoginRequiredMixin, CreateView):
    model = LaborLaw
    form_class = LaborLawForm
    template_name = 'compliance/labor_law_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Labor Law'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Labor law created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:labor_law_detail', kwargs={'pk': self.object.pk})


class LaborLawUpdateView(LoginRequiredMixin, UpdateView):
    model = LaborLaw
    form_class = LaborLawForm
    template_name = 'compliance/labor_law_form.html'

    def get_queryset(self):
        return LaborLaw.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Labor Law'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Labor law updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:labor_law_detail', kwargs={'pk': self.object.pk})


class LaborLawDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        law = get_object_or_404(LaborLaw, pk=pk, tenant=request.tenant)
        law.delete()
        messages.success(request, 'Labor law deleted successfully.')
        return redirect('compliance:labor_law_list')


class LaborLawComplianceCreateView(LoginRequiredMixin, CreateView):
    model = LaborLawCompliance
    form_class = LaborLawComplianceForm
    template_name = 'compliance/labor_law_compliance_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Compliance Record'
        context['labor_law'] = get_object_or_404(LaborLaw, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.labor_law = get_object_or_404(LaborLaw, pk=self.kwargs['pk'], tenant=self.request.tenant)
        messages.success(self.request, 'Compliance record created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:labor_law_detail', kwargs={'pk': self.kwargs['pk']})


class LaborLawComplianceUpdateView(LoginRequiredMixin, UpdateView):
    model = LaborLawCompliance
    form_class = LaborLawComplianceForm
    template_name = 'compliance/labor_law_compliance_form.html'

    def get_queryset(self):
        return LaborLawCompliance.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Compliance Record'
        context['labor_law'] = self.object.labor_law
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Compliance record updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:labor_law_detail', kwargs={'pk': self.object.labor_law.pk})


class LaborLawComplianceDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        record = get_object_or_404(LaborLawCompliance, pk=pk, tenant=request.tenant)
        law_pk = record.labor_law.pk
        record.delete()
        messages.success(request, 'Compliance record deleted successfully.')
        return redirect('compliance:labor_law_detail', pk=law_pk)


# ===========================================================================
# Contract Management Views
# ===========================================================================

class EmploymentContractListView(LoginRequiredMixin, ListView):
    model = EmploymentContract
    template_name = 'compliance/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20

    def get_queryset(self):
        qs = EmploymentContract.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'signed_by')
        search = self.request.GET.get('search', '').strip()
        contract_type = self.request.GET.get('contract_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(contract_number__icontains=search)
            )
        if contract_type:
            qs = qs.filter(contract_type=contract_type)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_type_choices'] = EmploymentContract.CONTRACT_TYPE_CHOICES
        context['status_choices'] = EmploymentContract.STATUS_CHOICES
        return context


class EmploymentContractDetailView(LoginRequiredMixin, DetailView):
    model = EmploymentContract
    template_name = 'compliance/contract_detail.html'
    context_object_name = 'contract'

    def get_queryset(self):
        return EmploymentContract.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'signed_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amendments'] = self.object.amendments.select_related('approved_by')
        return context


class EmploymentContractCreateView(LoginRequiredMixin, CreateView):
    model = EmploymentContract
    form_class = EmploymentContractForm
    template_name = 'compliance/contract_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Employment Contract'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Employment contract created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:contract_detail', kwargs={'pk': self.object.pk})


class EmploymentContractUpdateView(LoginRequiredMixin, UpdateView):
    model = EmploymentContract
    form_class = EmploymentContractForm
    template_name = 'compliance/contract_form.html'

    def get_queryset(self):
        return EmploymentContract.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Employment Contract'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Employment contract updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:contract_detail', kwargs={'pk': self.object.pk})


class EmploymentContractDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        contract = get_object_or_404(EmploymentContract, pk=pk, tenant=request.tenant)
        contract.delete()
        messages.success(request, 'Employment contract deleted successfully.')
        return redirect('compliance:contract_list')


class ContractAmendmentCreateView(LoginRequiredMixin, CreateView):
    model = ContractAmendment
    form_class = ContractAmendmentForm
    template_name = 'compliance/contract_amendment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Amendment'
        context['contract'] = get_object_or_404(EmploymentContract, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.contract = get_object_or_404(EmploymentContract, pk=self.kwargs['pk'], tenant=self.request.tenant)
        messages.success(self.request, 'Contract amendment created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:contract_detail', kwargs={'pk': self.kwargs['pk']})


class ContractAmendmentUpdateView(LoginRequiredMixin, UpdateView):
    model = ContractAmendment
    form_class = ContractAmendmentForm
    template_name = 'compliance/contract_amendment_form.html'

    def get_queryset(self):
        return ContractAmendment.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Amendment'
        context['contract'] = self.object.contract
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Contract amendment updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:contract_detail', kwargs={'pk': self.object.contract.pk})


class ContractAmendmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        amendment = get_object_or_404(ContractAmendment, pk=pk, tenant=request.tenant)
        contract_pk = amendment.contract.pk
        amendment.delete()
        messages.success(request, 'Contract amendment deleted successfully.')
        return redirect('compliance:contract_detail', pk=contract_pk)


# ===========================================================================
# Policy Management Views
# ===========================================================================

class CompliancePolicyListView(LoginRequiredMixin, ListView):
    model = CompliancePolicy
    template_name = 'compliance/policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        qs = CompliancePolicy.objects.filter(
            tenant=self.request.tenant
        ).select_related('approved_by', 'department')
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = CompliancePolicy.CATEGORY_CHOICES
        context['status_choices'] = CompliancePolicy.STATUS_CHOICES
        return context


class CompliancePolicyDetailView(LoginRequiredMixin, DetailView):
    model = CompliancePolicy
    template_name = 'compliance/policy_detail.html'
    context_object_name = 'policy'

    def get_queryset(self):
        return CompliancePolicy.objects.filter(
            tenant=self.request.tenant
        ).select_related('approved_by', 'department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['versions'] = self.object.versions.select_related('created_by')
        context['acknowledgments'] = self.object.acknowledgments.select_related('employee')
        return context


class CompliancePolicyCreateView(LoginRequiredMixin, CreateView):
    model = CompliancePolicy
    form_class = CompliancePolicyForm
    template_name = 'compliance/policy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Policy'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Policy created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:policy_detail', kwargs={'pk': self.object.pk})


class CompliancePolicyUpdateView(LoginRequiredMixin, UpdateView):
    model = CompliancePolicy
    form_class = CompliancePolicyForm
    template_name = 'compliance/policy_form.html'

    def get_queryset(self):
        return CompliancePolicy.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Policy'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Policy updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:policy_detail', kwargs={'pk': self.object.pk})


class CompliancePolicyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        policy = get_object_or_404(CompliancePolicy, pk=pk, tenant=request.tenant)
        policy.delete()
        messages.success(request, 'Policy deleted successfully.')
        return redirect('compliance:policy_list')


class PolicyVersionCreateView(LoginRequiredMixin, CreateView):
    model = PolicyVersion
    form_class = PolicyVersionForm
    template_name = 'compliance/policy_version_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Version'
        context['policy'] = get_object_or_404(CompliancePolicy, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.policy = get_object_or_404(CompliancePolicy, pk=self.kwargs['pk'], tenant=self.request.tenant)
        messages.success(self.request, 'Policy version created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:policy_detail', kwargs={'pk': self.kwargs['pk']})


class PolicyVersionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        version = get_object_or_404(PolicyVersion, pk=pk, tenant=request.tenant)
        policy_pk = version.policy.pk
        version.delete()
        messages.success(request, 'Policy version deleted successfully.')
        return redirect('compliance:policy_detail', pk=policy_pk)


class PolicyAcknowledgmentCreateView(LoginRequiredMixin, CreateView):
    model = PolicyAcknowledgment
    form_class = PolicyAcknowledgmentForm
    template_name = 'compliance/policy_acknowledgment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Acknowledgment'
        context['policy'] = get_object_or_404(CompliancePolicy, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.policy = get_object_or_404(CompliancePolicy, pk=self.kwargs['pk'], tenant=self.request.tenant)
        if form.instance.is_acknowledged:
            form.instance.acknowledged_date = timezone.now()
        messages.success(self.request, 'Policy acknowledgment added successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:policy_detail', kwargs={'pk': self.kwargs['pk']})


# ===========================================================================
# Disciplinary Actions Views
# ===========================================================================

class DisciplinaryIncidentListView(LoginRequiredMixin, ListView):
    model = DisciplinaryIncident
    template_name = 'compliance/incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 20

    def get_queryset(self):
        qs = DisciplinaryIncident.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'reported_by')
        search = self.request.GET.get('search', '').strip()
        incident_type = self.request.GET.get('incident_type', '').strip()
        severity = self.request.GET.get('severity', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(description__icontains=search)
            )
        if incident_type:
            qs = qs.filter(incident_type=incident_type)
        if severity:
            qs = qs.filter(severity=severity)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incident_type_choices'] = DisciplinaryIncident.INCIDENT_TYPE_CHOICES
        context['severity_choices'] = DisciplinaryIncident.SEVERITY_CHOICES
        context['status_choices'] = DisciplinaryIncident.STATUS_CHOICES
        return context


class DisciplinaryIncidentDetailView(LoginRequiredMixin, DetailView):
    model = DisciplinaryIncident
    template_name = 'compliance/incident_detail.html'
    context_object_name = 'incident'

    def get_queryset(self):
        return DisciplinaryIncident.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'reported_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warnings'] = self.object.warnings.select_related('employee', 'issued_by')
        return context


class DisciplinaryIncidentCreateView(LoginRequiredMixin, CreateView):
    model = DisciplinaryIncident
    form_class = DisciplinaryIncidentForm
    template_name = 'compliance/incident_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Report Incident'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Incident reported successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:incident_detail', kwargs={'pk': self.object.pk})


class DisciplinaryIncidentUpdateView(LoginRequiredMixin, UpdateView):
    model = DisciplinaryIncident
    form_class = DisciplinaryIncidentForm
    template_name = 'compliance/incident_form.html'

    def get_queryset(self):
        return DisciplinaryIncident.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Incident'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Incident updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:incident_detail', kwargs={'pk': self.object.pk})


class DisciplinaryIncidentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        incident = get_object_or_404(DisciplinaryIncident, pk=pk, tenant=request.tenant)
        incident.delete()
        messages.success(request, 'Incident deleted successfully.')
        return redirect('compliance:incident_list')


class WarningRecordCreateView(LoginRequiredMixin, CreateView):
    model = WarningRecord
    form_class = WarningRecordForm
    template_name = 'compliance/warning_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Issue Warning'
        context['incident'] = get_object_or_404(DisciplinaryIncident, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.incident = get_object_or_404(DisciplinaryIncident, pk=self.kwargs['pk'], tenant=self.request.tenant)
        messages.success(self.request, 'Warning record created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:incident_detail', kwargs={'pk': self.kwargs['pk']})


class WarningRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = WarningRecord
    form_class = WarningRecordForm
    template_name = 'compliance/warning_form.html'

    def get_queryset(self):
        return WarningRecord.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Warning'
        context['incident'] = self.object.incident
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Warning record updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:incident_detail', kwargs={'pk': self.object.incident.pk})


class WarningRecordDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        warning = get_object_or_404(WarningRecord, pk=pk, tenant=request.tenant)
        incident_pk = warning.incident.pk
        warning.delete()
        messages.success(request, 'Warning record deleted successfully.')
        return redirect('compliance:incident_detail', pk=incident_pk)


class DisciplinaryAppealCreateView(LoginRequiredMixin, CreateView):
    model = DisciplinaryAppeal
    form_class = DisciplinaryAppealForm
    template_name = 'compliance/appeal_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'File Appeal'
        context['warning'] = get_object_or_404(WarningRecord, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.warning = get_object_or_404(WarningRecord, pk=self.kwargs['pk'], tenant=self.request.tenant)
        messages.success(self.request, 'Appeal filed successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        warning = get_object_or_404(WarningRecord, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return reverse('compliance:incident_detail', kwargs={'pk': warning.incident.pk})


class DisciplinaryAppealUpdateView(LoginRequiredMixin, UpdateView):
    model = DisciplinaryAppeal
    form_class = DisciplinaryAppealForm
    template_name = 'compliance/appeal_form.html'

    def get_queryset(self):
        return DisciplinaryAppeal.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Appeal'
        context['warning'] = self.object.warning
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Appeal updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:incident_detail', kwargs={'pk': self.object.warning.incident.pk})


# ===========================================================================
# Grievance Handling Views
# ===========================================================================

class GrievanceListView(LoginRequiredMixin, ListView):
    model = Grievance
    template_name = 'compliance/grievance_list.html'
    context_object_name = 'grievances'
    paginate_by = 20

    def get_queryset(self):
        qs = Grievance.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'assigned_to')
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '').strip()
        priority = self.request.GET.get('priority', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(subject__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if priority:
            qs = qs.filter(priority=priority)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = Grievance.CATEGORY_CHOICES
        context['priority_choices'] = Grievance.PRIORITY_CHOICES
        context['status_choices'] = Grievance.STATUS_CHOICES
        return context


class GrievanceDetailView(LoginRequiredMixin, DetailView):
    model = Grievance
    template_name = 'compliance/grievance_detail.html'
    context_object_name = 'grievance'

    def get_queryset(self):
        return Grievance.objects.filter(
            tenant=self.request.tenant
        ).select_related('employee', 'assigned_to')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['investigations'] = self.object.investigations.select_related('investigator')
        return context


class GrievanceCreateView(LoginRequiredMixin, CreateView):
    model = Grievance
    form_class = GrievanceForm
    template_name = 'compliance/grievance_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register Grievance'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Grievance registered successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:grievance_detail', kwargs={'pk': self.object.pk})


class GrievanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Grievance
    form_class = GrievanceForm
    template_name = 'compliance/grievance_form.html'

    def get_queryset(self):
        return Grievance.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Grievance'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Grievance updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:grievance_detail', kwargs={'pk': self.object.pk})


class GrievanceDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        grievance = get_object_or_404(Grievance, pk=pk, tenant=request.tenant)
        grievance.delete()
        messages.success(request, 'Grievance deleted successfully.')
        return redirect('compliance:grievance_list')


class GrievanceInvestigationCreateView(LoginRequiredMixin, CreateView):
    model = GrievanceInvestigation
    form_class = GrievanceInvestigationForm
    template_name = 'compliance/grievance_investigation_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Start Investigation'
        context['grievance'] = get_object_or_404(Grievance, pk=self.kwargs['pk'], tenant=self.request.tenant)
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.grievance = get_object_or_404(Grievance, pk=self.kwargs['pk'], tenant=self.request.tenant)
        messages.success(self.request, 'Investigation started successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:grievance_detail', kwargs={'pk': self.kwargs['pk']})


class GrievanceInvestigationUpdateView(LoginRequiredMixin, UpdateView):
    model = GrievanceInvestigation
    form_class = GrievanceInvestigationForm
    template_name = 'compliance/grievance_investigation_form.html'

    def get_queryset(self):
        return GrievanceInvestigation.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Investigation'
        context['grievance'] = self.object.grievance
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Investigation updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:grievance_detail', kwargs={'pk': self.object.grievance.pk})


class GrievanceInvestigationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        investigation = get_object_or_404(GrievanceInvestigation, pk=pk, tenant=request.tenant)
        grievance_pk = investigation.grievance.pk
        investigation.delete()
        messages.success(request, 'Investigation deleted successfully.')
        return redirect('compliance:grievance_detail', pk=grievance_pk)


# ===========================================================================
# Statutory Registers Views
# ===========================================================================

class MusterRollListView(LoginRequiredMixin, ListView):
    model = MusterRoll
    template_name = 'compliance/muster_roll_list.html'
    context_object_name = 'rolls'
    paginate_by = 20

    def get_queryset(self):
        qs = MusterRoll.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'generated_by')
        year = self.request.GET.get('year', '').strip()
        status = self.request.GET.get('status', '').strip()
        if year:
            qs = qs.filter(year=year)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = MusterRoll.STATUS_CHOICES
        return context


class MusterRollDetailView(LoginRequiredMixin, DetailView):
    model = MusterRoll
    template_name = 'compliance/muster_roll_detail.html'
    context_object_name = 'roll'

    def get_queryset(self):
        return MusterRoll.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'generated_by')


class MusterRollCreateView(LoginRequiredMixin, CreateView):
    model = MusterRoll
    form_class = MusterRollForm
    template_name = 'compliance/muster_roll_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Muster Roll'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Muster roll created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:muster_roll_detail', kwargs={'pk': self.object.pk})


class MusterRollUpdateView(LoginRequiredMixin, UpdateView):
    model = MusterRoll
    form_class = MusterRollForm
    template_name = 'compliance/muster_roll_form.html'

    def get_queryset(self):
        return MusterRoll.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Muster Roll'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Muster roll updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:muster_roll_detail', kwargs={'pk': self.object.pk})


class MusterRollDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        roll = get_object_or_404(MusterRoll, pk=pk, tenant=request.tenant)
        roll.delete()
        messages.success(request, 'Muster roll deleted successfully.')
        return redirect('compliance:muster_roll_list')


class WageRegisterListView(LoginRequiredMixin, ListView):
    model = WageRegister
    template_name = 'compliance/wage_register_list.html'
    context_object_name = 'registers'
    paginate_by = 20

    def get_queryset(self):
        qs = WageRegister.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'generated_by')
        year = self.request.GET.get('year', '').strip()
        status = self.request.GET.get('status', '').strip()
        if year:
            qs = qs.filter(year=year)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = WageRegister.STATUS_CHOICES
        return context


class WageRegisterDetailView(LoginRequiredMixin, DetailView):
    model = WageRegister
    template_name = 'compliance/wage_register_detail.html'
    context_object_name = 'register'

    def get_queryset(self):
        return WageRegister.objects.filter(
            tenant=self.request.tenant
        ).select_related('department', 'generated_by')


class WageRegisterCreateView(LoginRequiredMixin, CreateView):
    model = WageRegister
    form_class = WageRegisterForm
    template_name = 'compliance/wage_register_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Wage Register'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Wage register created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:wage_register_detail', kwargs={'pk': self.object.pk})


class WageRegisterUpdateView(LoginRequiredMixin, UpdateView):
    model = WageRegister
    form_class = WageRegisterForm
    template_name = 'compliance/wage_register_form.html'

    def get_queryset(self):
        return WageRegister.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Wage Register'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Wage register updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:wage_register_detail', kwargs={'pk': self.object.pk})


class WageRegisterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        register = get_object_or_404(WageRegister, pk=pk, tenant=request.tenant)
        register.delete()
        messages.success(request, 'Wage register deleted successfully.')
        return redirect('compliance:wage_register_list')


class InspectionReportListView(LoginRequiredMixin, ListView):
    model = InspectionReport
    template_name = 'compliance/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 20

    def get_queryset(self):
        qs = InspectionReport.objects.filter(
            tenant=self.request.tenant
        ).select_related('department')
        search = self.request.GET.get('search', '').strip()
        inspection_type = self.request.GET.get('inspection_type', '').strip()
        compliance_status = self.request.GET.get('compliance_status', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(inspector_name__icontains=search) |
                Q(areas_inspected__icontains=search)
            )
        if inspection_type:
            qs = qs.filter(inspection_type=inspection_type)
        if compliance_status:
            qs = qs.filter(compliance_status=compliance_status)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inspection_type_choices'] = InspectionReport.INSPECTION_TYPE_CHOICES
        context['compliance_status_choices'] = InspectionReport.COMPLIANCE_STATUS_CHOICES
        context['status_choices'] = InspectionReport.STATUS_CHOICES
        return context


class InspectionReportDetailView(LoginRequiredMixin, DetailView):
    model = InspectionReport
    template_name = 'compliance/inspection_detail.html'
    context_object_name = 'inspection'

    def get_queryset(self):
        return InspectionReport.objects.filter(
            tenant=self.request.tenant
        ).select_related('department')


class InspectionReportCreateView(LoginRequiredMixin, CreateView):
    model = InspectionReport
    form_class = InspectionReportForm
    template_name = 'compliance/inspection_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Inspection Report'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Inspection report created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:inspection_detail', kwargs={'pk': self.object.pk})


class InspectionReportUpdateView(LoginRequiredMixin, UpdateView):
    model = InspectionReport
    form_class = InspectionReportForm
    template_name = 'compliance/inspection_form.html'

    def get_queryset(self):
        return InspectionReport.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Inspection Report'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Inspection report updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('compliance:inspection_detail', kwargs={'pk': self.object.pk})


class InspectionReportDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        inspection = get_object_or_404(InspectionReport, pk=pk, tenant=request.tenant)
        inspection.delete()
        messages.success(request, 'Inspection report deleted successfully.')
        return redirect('compliance:inspection_list')
