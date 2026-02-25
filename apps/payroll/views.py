from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, TemplateView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce
from django.http import FileResponse, HttpResponse, Http404
from django.template.loader import get_template
from decimal import Decimal
from io import BytesIO

from .models import (
    PayComponent, SalaryStructure, SalaryStructureComponent,
    EmployeeSalaryStructure, EmployeeSalaryComponent,
    PayrollPeriod, PayrollEntry, PayrollEntryComponent,
    SalaryHold, SalaryRevision,
    PFConfiguration, ESIConfiguration, ProfessionalTaxSlab,
    LWFConfiguration, StatutoryContribution,
    TaxRegimeChoice, InvestmentDeclaration, InvestmentProof, TaxComputation,
    BankFile, Payslip, PaymentRegister, Reimbursement,
)

from .forms import (
    PayComponentForm, SalaryStructureForm, SalaryStructureComponentForm,
    EmployeeSalaryStructureForm,
    PayrollPeriodForm, SalaryHoldForm, SalaryHoldReleaseForm,
    SalaryRevisionForm, SalaryRevisionApprovalForm,
    PayrollApprovalForm, PayrollEntryHoldForm,
    PFConfigurationForm, ESIConfigurationForm, ProfessionalTaxSlabForm,
    LWFConfigurationForm,
    TaxRegimeChoiceForm, InvestmentDeclarationForm,
    InvestmentDeclarationVerifyForm, InvestmentProofForm,
    BankFileGenerateForm, PaymentReconcileForm,
    ReimbursementForm, ReimbursementApprovalForm,
)

from apps.employees.models import Employee


# =============================================================================
# Dashboard
# =============================================================================

class PayrollDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'payroll/payroll_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant

        context['total_active_salary_structures'] = (
            EmployeeSalaryStructure.all_objects
            .filter(tenant=tenant, status='active')
            .count()
        )

        context['total_monthly_salary_cost'] = (
            EmployeeSalaryStructure.all_objects
            .filter(tenant=tenant, status='active')
            .aggregate(
                total=Coalesce(Sum('gross_salary'), Decimal('0'), output_field=DecimalField())
            )['total']
        )

        context['pending_approvals'] = (
            PayrollPeriod.all_objects
            .filter(tenant=tenant, status='processed')
            .count()
        )

        context['recent_payroll_periods'] = (
            PayrollPeriod.all_objects
            .filter(tenant=tenant)
            .order_by('-start_date')[:5]
        )

        context['pending_revisions'] = (
            SalaryRevision.all_objects
            .filter(tenant=tenant, status='pending')
            .count()
        )

        context['active_holds'] = (
            SalaryHold.all_objects
            .filter(tenant=tenant, status='active')
            .count()
        )

        return context


# =============================================================================
# Pay Components (CRUD)
# =============================================================================

class PayComponentListView(LoginRequiredMixin, ListView):
    model = PayComponent
    template_name = 'payroll/component_list.html'
    context_object_name = 'components'
    paginate_by = 20

    def get_queryset(self):
        qs = PayComponent.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
        component_type = self.request.GET.get('component_type', '')
        if component_type:
            qs = qs.filter(component_type=component_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_component_type'] = self.request.GET.get('component_type', '')
        return context


class PayComponentCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PayComponentForm(tenant=request.tenant)
        return render(request, 'payroll/component_form.html', {'form': form})

    def post(self, request):
        form = PayComponentForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Pay component created successfully.')
            return redirect('payroll:component_list')
        return render(request, 'payroll/component_form.html', {'form': form})


class PayComponentUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(PayComponent.all_objects, pk=pk, tenant=request.tenant)
        form = PayComponentForm(instance=obj, tenant=request.tenant)
        return render(request, 'payroll/component_form.html', {'form': form, 'object': obj})

    def post(self, request, pk):
        obj = get_object_or_404(PayComponent.all_objects, pk=pk, tenant=request.tenant)
        form = PayComponentForm(request.POST, instance=obj, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pay component updated successfully.')
            return redirect('payroll:component_list')
        return render(request, 'payroll/component_form.html', {'form': form, 'object': obj})


# =============================================================================
# Salary Structures (CRUD + Detail)
# =============================================================================

class SalaryStructureListView(LoginRequiredMixin, ListView):
    model = SalaryStructure
    template_name = 'payroll/structure_list.html'
    context_object_name = 'structures'
    paginate_by = 20

    def get_queryset(self):
        qs = SalaryStructure.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
        is_active = self.request.GET.get('is_active', '')
        if is_active:
            qs = qs.filter(is_active=is_active == 'true')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_is_active'] = self.request.GET.get('is_active', '')
        return context


class SalaryStructureCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = SalaryStructureForm(tenant=request.tenant)
        return render(request, 'payroll/structure_form.html', {'form': form})

    def post(self, request):
        form = SalaryStructureForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Salary structure created successfully.')
            return redirect('payroll:structure_detail', pk=obj.pk)
        return render(request, 'payroll/structure_form.html', {'form': form})


class SalaryStructureDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            SalaryStructure.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        components = (
            SalaryStructureComponent.all_objects
            .filter(tenant=request.tenant, salary_structure=obj)
            .select_related('component')
            .order_by('order')
        )
        return render(request, 'payroll/structure_detail.html', {
            'object': obj,
            'components': components,
        })


class SalaryStructureUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(SalaryStructure.all_objects, pk=pk, tenant=request.tenant)
        form = SalaryStructureForm(instance=obj, tenant=request.tenant)
        return render(request, 'payroll/structure_form.html', {'form': form, 'object': obj})

    def post(self, request, pk):
        obj = get_object_or_404(SalaryStructure.all_objects, pk=pk, tenant=request.tenant)
        form = SalaryStructureForm(request.POST, instance=obj, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary structure updated successfully.')
            return redirect('payroll:structure_detail', pk=obj.pk)
        return render(request, 'payroll/structure_form.html', {'form': form, 'object': obj})


# =============================================================================
# Employee Salary (CRUD + Detail)
# =============================================================================

class EmployeeSalaryListView(LoginRequiredMixin, ListView):
    model = EmployeeSalaryStructure
    template_name = 'payroll/employee_salary_list.html'
    context_object_name = 'salaries'
    paginate_by = 20

    def get_queryset(self):
        qs = EmployeeSalaryStructure.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee', 'salary_structure')

        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        department = self.request.GET.get('department', '')
        if department:
            qs = qs.filter(employee__department_id=department)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_department'] = self.request.GET.get('department', '')
        return context


class EmployeeSalaryCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = EmployeeSalaryStructureForm(tenant=request.tenant)
        return render(request, 'payroll/employee_salary_form.html', {'form': form})

    def post(self, request):
        form = EmployeeSalaryStructureForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Employee salary structure created successfully.')
            return redirect('payroll:employee_salary_list')
        return render(request, 'payroll/employee_salary_form.html', {'form': form})


class EmployeeSalaryDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            EmployeeSalaryStructure.all_objects.select_related(
                'employee', 'salary_structure',
            ),
            pk=pk,
            tenant=request.tenant,
        )
        components = (
            EmployeeSalaryComponent.all_objects
            .filter(tenant=request.tenant, employee_salary_structure=obj)
            .select_related('component')
            .order_by('component__component_type', 'component__name')
        )
        return render(request, 'payroll/employee_salary_detail.html', {
            'object': obj,
            'components': components,
        })


class EmployeeSalaryUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            EmployeeSalaryStructure.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        form = EmployeeSalaryStructureForm(instance=obj, tenant=request.tenant)
        return render(request, 'payroll/employee_salary_form.html', {'form': form, 'object': obj})

    def post(self, request, pk):
        obj = get_object_or_404(
            EmployeeSalaryStructure.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        form = EmployeeSalaryStructureForm(request.POST, instance=obj, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee salary structure updated successfully.')
            return redirect('payroll:employee_salary_detail', pk=obj.pk)
        return render(request, 'payroll/employee_salary_form.html', {'form': form, 'object': obj})


# =============================================================================
# Payroll Periods (CRUD + Process + Approve)
# =============================================================================

class PayrollPeriodListView(LoginRequiredMixin, ListView):
    model = PayrollPeriod
    template_name = 'payroll/period_list.html'
    context_object_name = 'periods'
    paginate_by = 20

    def get_queryset(self):
        qs = PayrollPeriod.all_objects.filter(tenant=self.request.tenant)
        year = self.request.GET.get('year', '')
        if year:
            qs = qs.filter(start_date__year=year)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_year'] = self.request.GET.get('year', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class PayrollPeriodCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PayrollPeriodForm(tenant=request.tenant)
        return render(request, 'payroll/period_form.html', {'form': form})

    def post(self, request):
        form = PayrollPeriodForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Payroll period created successfully.')
            return redirect('payroll:period_list')
        return render(request, 'payroll/period_form.html', {'form': form})


class PayrollPeriodDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        period = get_object_or_404(
            PayrollPeriod.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        entries = (
            PayrollEntry.all_objects
            .filter(tenant=request.tenant, payroll_period=period)
            .select_related('employee')
            .order_by('employee__first_name', 'employee__last_name')
        )
        totals = entries.aggregate(
            total_gross=Coalesce(Sum('gross_earnings'), Decimal('0'), output_field=DecimalField()),
            total_deductions=Coalesce(Sum('total_deductions'), Decimal('0'), output_field=DecimalField()),
            total_net=Coalesce(Sum('net_pay'), Decimal('0'), output_field=DecimalField()),
        )
        return render(request, 'payroll/period_detail.html', {
            'object': period,
            'entries': entries,
            'totals': totals,
        })


class PayrollProcessView(LoginRequiredMixin, View):
    """Processes payroll for a given period. POST only."""

    def post(self, request, pk):
        period = get_object_or_404(
            PayrollPeriod.all_objects,
            pk=pk,
            tenant=request.tenant,
        )

        if period.status != 'draft':
            messages.error(request, 'Only draft payroll periods can be processed.')
            return redirect('payroll:period_detail', pk=period.pk)

        # Get all active employees with active salary structures
        active_salary_structures = (
            EmployeeSalaryStructure.all_objects
            .filter(tenant=request.tenant, status='active')
            .select_related('employee', 'salary_structure')
        )

        if not active_salary_structures.exists():
            messages.warning(request, 'No active salary structures found to process.')
            return redirect('payroll:period_detail', pk=period.pk)

        entries_created = 0
        total_gross = Decimal('0')
        total_deductions = Decimal('0')
        total_net = Decimal('0')

        for emp_salary in active_salary_structures:
            # Check if entry already exists for this employee in this period
            if PayrollEntry.all_objects.filter(
                tenant=request.tenant,
                payroll_period=period,
                employee=emp_salary.employee,
            ).exists():
                continue

            # Check for active salary holds
            has_hold = SalaryHold.all_objects.filter(
                tenant=request.tenant,
                employee=emp_salary.employee,
                status='active',
            ).exists()

            # Calculate component totals
            components = (
                EmployeeSalaryComponent.all_objects
                .filter(tenant=request.tenant, employee_salary_structure=emp_salary)
                .select_related('component')
            )

            entry_gross = Decimal('0')
            entry_deductions = Decimal('0')

            for comp in components:
                if comp.component.component_type == 'earning':
                    entry_gross += comp.amount
                elif comp.component.component_type == 'deduction':
                    entry_deductions += comp.amount

            entry_net = entry_gross - entry_deductions

            # Create payroll entry
            entry = PayrollEntry.all_objects.create(
                tenant=request.tenant,
                payroll_period=period,
                employee=emp_salary.employee,
                employee_salary_structure=emp_salary,
                gross_earnings=entry_gross,
                total_deductions=entry_deductions,
                net_pay=entry_net,
                status='on_hold' if has_hold else 'processed',
            )

            # Create payroll entry components
            for comp in components:
                PayrollEntryComponent.all_objects.create(
                    tenant=request.tenant,
                    payroll_entry=entry,
                    component=comp.component,
                    amount=comp.amount,
                )

            total_gross += entry_gross
            total_deductions += entry_deductions
            total_net += entry_net
            entries_created += 1

        # Update period totals and status
        period.total_gross_pay = total_gross
        period.total_deductions = total_deductions
        period.total_net_pay = total_net
        period.total_employees = entries_created
        period.status = 'processed'
        period.processed_date = timezone.now()
        period.save()

        messages.success(
            request,
            f'Payroll processed successfully. {entries_created} entries created.',
        )
        return redirect('payroll:period_detail', pk=period.pk)


class PayrollApproveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        period = get_object_or_404(
            PayrollPeriod.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        form = PayrollApprovalForm(tenant=request.tenant)
        entries = (
            PayrollEntry.all_objects
            .filter(tenant=request.tenant, payroll_period=period)
            .select_related('employee')
            .order_by('employee__first_name', 'employee__last_name')
        )
        totals = entries.aggregate(
            total_gross=Coalesce(Sum('gross_earnings'), Decimal('0'), output_field=DecimalField()),
            total_deductions=Coalesce(Sum('total_deductions'), Decimal('0'), output_field=DecimalField()),
            total_net=Coalesce(Sum('net_pay'), Decimal('0'), output_field=DecimalField()),
        )
        return render(request, 'payroll/period_detail.html', {
            'object': period,
            'entries': entries,
            'totals': totals,
            'approval_form': form,
        })

    def post(self, request, pk):
        period = get_object_or_404(
            PayrollPeriod.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        form = PayrollApprovalForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            period.status = 'approved'
            period.approved_by = request.user
            period.approved_date = timezone.now()
            period.save()
            messages.success(request, 'Payroll period approved successfully.')
            return redirect('payroll:period_detail', pk=period.pk)

        entries = (
            PayrollEntry.all_objects
            .filter(tenant=request.tenant, payroll_period=period)
            .select_related('employee')
            .order_by('employee__first_name', 'employee__last_name')
        )
        totals = entries.aggregate(
            total_gross=Coalesce(Sum('gross_earnings'), Decimal('0'), output_field=DecimalField()),
            total_deductions=Coalesce(Sum('total_deductions'), Decimal('0'), output_field=DecimalField()),
            total_net=Coalesce(Sum('net_pay'), Decimal('0'), output_field=DecimalField()),
        )
        return render(request, 'payroll/period_detail.html', {
            'object': period,
            'entries': entries,
            'totals': totals,
            'approval_form': form,
        })


# =============================================================================
# Payroll Entries
# =============================================================================

class PayrollEntryDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        entry = get_object_or_404(
            PayrollEntry.all_objects.select_related(
                'employee', 'payroll_period', 'employee_salary',
            ),
            pk=pk,
            tenant=request.tenant,
        )
        components = (
            PayrollEntryComponent.all_objects
            .filter(tenant=request.tenant, payroll_entry=entry)
            .select_related('component')
            .order_by('component__component_type', 'component__name')
        )
        return render(request, 'payroll/entry_detail.html', {
            'object': entry,
            'components': components,
        })


class PayrollEntryHoldView(LoginRequiredMixin, View):
    def get(self, request, pk):
        entry = get_object_or_404(
            PayrollEntry.all_objects.select_related('employee', 'payroll_period'),
            pk=pk,
            tenant=request.tenant,
        )
        form = PayrollEntryHoldForm(tenant=request.tenant)
        return render(request, 'payroll/entry_detail.html', {
            'object': entry,
            'hold_form': form,
        })

    def post(self, request, pk):
        entry = get_object_or_404(
            PayrollEntry.all_objects.select_related('employee', 'payroll_period'),
            pk=pk,
            tenant=request.tenant,
        )
        form = PayrollEntryHoldForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            entry.status = 'on_hold'
            entry.save()
            messages.success(request, 'Payroll entry placed on hold.')
            return redirect('payroll:entry_detail', pk=entry.pk)
        return render(request, 'payroll/entry_detail.html', {
            'object': entry,
            'hold_form': form,
        })


# =============================================================================
# Salary Holds (CRUD + Release)
# =============================================================================

class SalaryHoldListView(LoginRequiredMixin, ListView):
    model = SalaryHold
    template_name = 'payroll/hold_list.html'
    context_object_name = 'holds'
    paginate_by = 20

    def get_queryset(self):
        qs = SalaryHold.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee')
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class SalaryHoldCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = SalaryHoldForm(tenant=request.tenant)
        return render(request, 'payroll/hold_form.html', {'form': form})

    def post(self, request):
        form = SalaryHoldForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Salary hold created successfully.')
            return redirect('payroll:hold_list')
        return render(request, 'payroll/hold_form.html', {'form': form})


class SalaryHoldReleaseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        hold = get_object_or_404(
            SalaryHold.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        hold.status = 'released'
        hold.released_date = timezone.now()
        hold.released_by = request.user
        hold.save()
        messages.success(request, 'Salary hold released successfully.')
        return redirect('payroll:hold_list')


# =============================================================================
# Salary Revisions (CRUD + Approve)
# =============================================================================

class SalaryRevisionListView(LoginRequiredMixin, ListView):
    model = SalaryRevision
    template_name = 'payroll/revision_list.html'
    context_object_name = 'revisions'
    paginate_by = 20

    def get_queryset(self):
        qs = SalaryRevision.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee')
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class SalaryRevisionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = SalaryRevisionForm(tenant=request.tenant)
        return render(request, 'payroll/revision_form.html', {'form': form})

    def post(self, request):
        form = SalaryRevisionForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Salary revision created successfully.')
            return redirect('payroll:revision_list')
        return render(request, 'payroll/revision_form.html', {'form': form})


class SalaryRevisionDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            SalaryRevision.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        return render(request, 'payroll/revision_detail.html', {'object': obj})


class SalaryRevisionApproveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        revision = get_object_or_404(
            SalaryRevision.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        form = SalaryRevisionApprovalForm(tenant=request.tenant)
        return render(request, 'payroll/revision_detail.html', {
            'object': revision,
            'approval_form': form,
        })

    def post(self, request, pk):
        revision = get_object_or_404(
            SalaryRevision.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        form = SalaryRevisionApprovalForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            revision.status = 'approved'
            revision.approved_by = request.user
            revision.approved_date = timezone.now()
            revision.save()
            messages.success(request, 'Salary revision approved successfully.')
            return redirect('payroll:revision_detail', pk=revision.pk)
        return render(request, 'payroll/revision_detail.html', {
            'object': revision,
            'approval_form': form,
        })


# =============================================================================
# Statutory - PF Configuration (CRUD)
# =============================================================================

class PFConfigListView(LoginRequiredMixin, ListView):
    model = PFConfiguration
    template_name = 'payroll/pf_config_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = PFConfiguration.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class PFConfigCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PFConfigurationForm(tenant=request.tenant)
        return render(request, 'payroll/pf_config_form.html', {'form': form})

    def post(self, request):
        form = PFConfigurationForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'PF configuration created successfully.')
            return redirect('payroll:pf_config_list')
        return render(request, 'payroll/pf_config_form.html', {'form': form})


class PFConfigUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(PFConfiguration.all_objects, pk=pk, tenant=request.tenant)
        form = PFConfigurationForm(instance=obj, tenant=request.tenant)
        return render(request, 'payroll/pf_config_form.html', {'form': form, 'object': obj})

    def post(self, request, pk):
        obj = get_object_or_404(PFConfiguration.all_objects, pk=pk, tenant=request.tenant)
        form = PFConfigurationForm(request.POST, instance=obj, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'PF configuration updated successfully.')
            return redirect('payroll:pf_config_list')
        return render(request, 'payroll/pf_config_form.html', {'form': form, 'object': obj})


# =============================================================================
# Statutory - ESI Configuration (CRUD)
# =============================================================================

class ESIConfigListView(LoginRequiredMixin, ListView):
    model = ESIConfiguration
    template_name = 'payroll/esi_config_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = ESIConfiguration.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class ESIConfigCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ESIConfigurationForm(tenant=request.tenant)
        return render(request, 'payroll/esi_config_form.html', {'form': form})

    def post(self, request):
        form = ESIConfigurationForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'ESI configuration created successfully.')
            return redirect('payroll:esi_config_list')
        return render(request, 'payroll/esi_config_form.html', {'form': form})


class ESIConfigUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(ESIConfiguration.all_objects, pk=pk, tenant=request.tenant)
        form = ESIConfigurationForm(instance=obj, tenant=request.tenant)
        return render(request, 'payroll/esi_config_form.html', {'form': form, 'object': obj})

    def post(self, request, pk):
        obj = get_object_or_404(ESIConfiguration.all_objects, pk=pk, tenant=request.tenant)
        form = ESIConfigurationForm(request.POST, instance=obj, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'ESI configuration updated successfully.')
            return redirect('payroll:esi_config_list')
        return render(request, 'payroll/esi_config_form.html', {'form': form, 'object': obj})


# =============================================================================
# Statutory - Professional Tax Slabs (CRUD)
# =============================================================================

class PTSlabListView(LoginRequiredMixin, ListView):
    model = ProfessionalTaxSlab
    template_name = 'payroll/pt_slab_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = ProfessionalTaxSlab.all_objects.filter(tenant=self.request.tenant)
        state = self.request.GET.get('state', '')
        if state:
            qs = qs.filter(state=state)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_state'] = self.request.GET.get('state', '')
        return context


class PTSlabCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfessionalTaxSlabForm(tenant=request.tenant)
        return render(request, 'payroll/pt_slab_form.html', {'form': form})

    def post(self, request):
        form = ProfessionalTaxSlabForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Professional tax slab created successfully.')
            return redirect('payroll:pt_slab_list')
        return render(request, 'payroll/pt_slab_form.html', {'form': form})


class PTSlabUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(ProfessionalTaxSlab.all_objects, pk=pk, tenant=request.tenant)
        form = ProfessionalTaxSlabForm(instance=obj, tenant=request.tenant)
        return render(request, 'payroll/pt_slab_form.html', {'form': form, 'object': obj})

    def post(self, request, pk):
        obj = get_object_or_404(ProfessionalTaxSlab.all_objects, pk=pk, tenant=request.tenant)
        form = ProfessionalTaxSlabForm(request.POST, instance=obj, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professional tax slab updated successfully.')
            return redirect('payroll:pt_slab_list')
        return render(request, 'payroll/pt_slab_form.html', {'form': form, 'object': obj})


# =============================================================================
# Statutory - LWF Configuration (CRUD)
# =============================================================================

class LWFConfigListView(LoginRequiredMixin, ListView):
    model = LWFConfiguration
    template_name = 'payroll/lwf_config_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = LWFConfiguration.all_objects.filter(tenant=self.request.tenant)
        state = self.request.GET.get('state', '')
        if state:
            qs = qs.filter(state=state)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_state'] = self.request.GET.get('state', '')
        return context


class LWFConfigCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = LWFConfigurationForm(tenant=request.tenant)
        return render(request, 'payroll/lwf_config_form.html', {'form': form})

    def post(self, request):
        form = LWFConfigurationForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'LWF configuration created successfully.')
            return redirect('payroll:lwf_config_list')
        return render(request, 'payroll/lwf_config_form.html', {'form': form})


class LWFConfigUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(LWFConfiguration.all_objects, pk=pk, tenant=request.tenant)
        form = LWFConfigurationForm(instance=obj, tenant=request.tenant)
        return render(request, 'payroll/lwf_config_form.html', {'form': form, 'object': obj})

    def post(self, request, pk):
        obj = get_object_or_404(LWFConfiguration.all_objects, pk=pk, tenant=request.tenant)
        form = LWFConfigurationForm(request.POST, instance=obj, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'LWF configuration updated successfully.')
            return redirect('payroll:lwf_config_list')
        return render(request, 'payroll/lwf_config_form.html', {'form': form, 'object': obj})


# =============================================================================
# Statutory Contributions
# =============================================================================

class StatutoryContributionListView(LoginRequiredMixin, ListView):
    model = StatutoryContribution
    template_name = 'payroll/statutory_contribution_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = StatutoryContribution.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee', 'payroll_period')
        contribution_type = self.request.GET.get('contribution_type', '')
        if contribution_type:
            qs = qs.filter(contribution_type=contribution_type)
        period = self.request.GET.get('payroll_period', '')
        if period:
            qs = qs.filter(payroll_period_id=period)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_type'] = self.request.GET.get('contribution_type', '')
        context['selected_period'] = self.request.GET.get('payroll_period', '')
        context['contribution_types'] = StatutoryContribution.CONTRIBUTION_TYPE_CHOICES
        context['payroll_periods'] = (
            PayrollPeriod.all_objects
            .filter(tenant=self.request.tenant)
            .order_by('-start_date')
        )
        return context


# =============================================================================
# Tax Regime
# =============================================================================

class TaxRegimeListView(LoginRequiredMixin, ListView):
    model = TaxRegimeChoice
    template_name = 'payroll/tax_regime_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = TaxRegimeChoice.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee')
        financial_year = self.request.GET.get('financial_year', '')
        if financial_year:
            qs = qs.filter(financial_year=financial_year)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        return qs.order_by('-financial_year', 'employee__first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_financial_year'] = self.request.GET.get('financial_year', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class TaxRegimeSetView(LoginRequiredMixin, View):
    def get(self, request):
        form = TaxRegimeChoiceForm(tenant=request.tenant)
        return render(request, 'payroll/tax_regime_form.html', {'form': form})

    def post(self, request):
        form = TaxRegimeChoiceForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Tax regime choice saved successfully.')
            return redirect('payroll:tax_regime_list')
        return render(request, 'payroll/tax_regime_form.html', {'form': form})


# =============================================================================
# Investment Declarations
# =============================================================================

class InvestmentDeclarationListView(LoginRequiredMixin, ListView):
    model = InvestmentDeclaration
    template_name = 'payroll/declaration_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = InvestmentDeclaration.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee')
        financial_year = self.request.GET.get('financial_year', '')
        if financial_year:
            qs = qs.filter(financial_year=financial_year)
        section = self.request.GET.get('section', '')
        if section:
            qs = qs.filter(section=section)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_financial_year'] = self.request.GET.get('financial_year', '')
        context['selected_section'] = self.request.GET.get('section', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class InvestmentDeclarationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = InvestmentDeclarationForm(tenant=request.tenant)
        return render(request, 'payroll/declaration_form.html', {'form': form})

    def post(self, request):
        form = InvestmentDeclarationForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Investment declaration created successfully.')
            return redirect('payroll:declaration_list')
        return render(request, 'payroll/declaration_form.html', {'form': form})


class InvestmentDeclarationDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            InvestmentDeclaration.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        proofs = (
            InvestmentProof.all_objects
            .filter(tenant=request.tenant, declaration=obj)
            .order_by('-uploaded_at')
        )
        return render(request, 'payroll/declaration_detail.html', {
            'object': obj,
            'proofs': proofs,
        })


class InvestmentDeclarationVerifyView(LoginRequiredMixin, View):
    def get(self, request, pk):
        declaration = get_object_or_404(
            InvestmentDeclaration.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        form = InvestmentDeclarationVerifyForm(tenant=request.tenant)
        proofs = (
            InvestmentProof.all_objects
            .filter(tenant=request.tenant, declaration=declaration)
            .order_by('-uploaded_at')
        )
        return render(request, 'payroll/declaration_detail.html', {
            'object': declaration,
            'proofs': proofs,
            'verify_form': form,
        })

    def post(self, request, pk):
        declaration = get_object_or_404(
            InvestmentDeclaration.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        form = InvestmentDeclarationVerifyForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            declaration.status = form.cleaned_data.get('status', 'verified')
            declaration.verified_by = request.user
            declaration.verified_date = timezone.now()
            declaration.verification_remarks = form.cleaned_data.get('remarks', '')
            declaration.save()
            messages.success(request, 'Investment declaration verified successfully.')
            return redirect('payroll:declaration_detail', pk=declaration.pk)

        proofs = (
            InvestmentProof.all_objects
            .filter(tenant=request.tenant, declaration=declaration)
            .order_by('-uploaded_at')
        )
        return render(request, 'payroll/declaration_detail.html', {
            'object': declaration,
            'proofs': proofs,
            'verify_form': form,
        })


# =============================================================================
# Investment Proofs
# =============================================================================

class InvestmentProofUploadView(LoginRequiredMixin, View):
    def get(self, request):
        form = InvestmentProofForm(tenant=request.tenant)
        return render(request, 'payroll/proof_upload_form.html', {'form': form})

    def post(self, request):
        form = InvestmentProofForm(request.POST, request.FILES, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Investment proof uploaded successfully.')
            return redirect('payroll:declaration_detail', pk=obj.declaration.pk)
        return render(request, 'payroll/proof_upload_form.html', {'form': form})


# =============================================================================
# Tax Computation
# =============================================================================

class TaxComputationListView(LoginRequiredMixin, ListView):
    model = TaxComputation
    template_name = 'payroll/tax_computation_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = TaxComputation.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee')
        financial_year = self.request.GET.get('financial_year', '')
        if financial_year:
            qs = qs.filter(financial_year=financial_year)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        return qs.order_by('-financial_year', 'employee__first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_financial_year'] = self.request.GET.get('financial_year', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class TaxComputationDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            TaxComputation.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        return render(request, 'payroll/tax_computation_detail.html', {'object': obj})


class TaxComputationRecalculateView(LoginRequiredMixin, View):
    """Recalculates tax computation for employees. POST only."""

    def post(self, request):
        tenant = request.tenant
        financial_year = request.POST.get('financial_year', '')
        if not financial_year:
            messages.error(request, 'Financial year is required for recalculation.')
            return redirect('payroll:tax_computation_list')

        # Get all active employees with salary structures
        active_employees = (
            EmployeeSalaryStructure.all_objects
            .filter(tenant=tenant, status='active')
            .select_related('employee')
        )

        recalculated = 0
        for emp_salary in active_employees:
            # Get or create tax computation
            computation, created = TaxComputation.all_objects.get_or_create(
                tenant=tenant,
                employee=emp_salary.employee,
                financial_year=financial_year,
                defaults={
                    'gross_income': emp_salary.gross_salary * 12 if emp_salary.gross_salary else Decimal('0'),
                },
            )
            if not created:
                computation.gross_income = (
                    emp_salary.gross_salary * 12 if emp_salary.gross_salary else Decimal('0')
                )
                computation.save()
            recalculated += 1

        messages.success(
            request,
            f'Tax computation recalculated for {recalculated} employees.',
        )
        return redirect('payroll:tax_computation_list')


# =============================================================================
# Bank Files
# =============================================================================

class BankFileListView(LoginRequiredMixin, ListView):
    model = BankFile
    template_name = 'payroll/bank_file_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = BankFile.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('payroll_period')
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        period = self.request.GET.get('period', '')
        if period:
            qs = qs.filter(payroll_period_id=period)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(file_name__icontains=search))
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['statuses'] = BankFile.STATUS_CHOICES
        context['payroll_periods'] = (
            PayrollPeriod.all_objects
            .filter(tenant=self.request.tenant)
            .order_by('-start_date')
        )
        return context


class BankFileGenerateView(LoginRequiredMixin, View):
    def get(self, request):
        form = BankFileGenerateForm(tenant=request.tenant)
        return render(request, 'payroll/bank_file_generate_form.html', {'form': form})

    def post(self, request):
        form = BankFileGenerateForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.generated_by = request.user
            obj.generated_date = timezone.now()
            obj.save()
            messages.success(request, 'Bank file generated successfully.')
            return redirect('payroll:bank_file_detail', pk=obj.pk)
        return render(request, 'payroll/bank_file_generate_form.html', {'form': form})


class BankFileDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            BankFile.all_objects.select_related('payroll_period'),
            pk=pk,
            tenant=request.tenant,
        )
        return render(request, 'payroll/bank_file_detail.html', {'object': obj})


# =============================================================================
# Payslips
# =============================================================================

class PayslipListView(LoginRequiredMixin, ListView):
    model = Payslip
    template_name = 'payroll/payslip_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = Payslip.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee', 'payroll_period')
        period = self.request.GET.get('payroll_period', '')
        if period:
            qs = qs.filter(payroll_period_id=period)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_period'] = self.request.GET.get('payroll_period', '')
        context['search'] = self.request.GET.get('search', '')
        context['payroll_periods'] = (
            PayrollPeriod.all_objects
            .filter(tenant=self.request.tenant)
            .order_by('-start_date')
        )
        return context


class PayslipDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            Payslip.all_objects.select_related(
                'employee', 'payroll_period', 'payroll_entry',
                'payroll_entry__employee_salary',
            ),
            pk=pk,
            tenant=request.tenant,
        )
        entry = obj.payroll_entry
        components = PayrollEntryComponent.all_objects.filter(
            tenant=request.tenant, payroll_entry=entry,
        ).select_related('pay_component').order_by('pay_component__display_order')
        earnings = [c for c in components if c.pay_component.component_type == 'earning']
        deductions = [c for c in components if c.pay_component.component_type == 'deduction']
        company = getattr(request, 'tenant', None)
        return render(request, 'payroll/payslip_detail.html', {
            'object': obj,
            'entry': entry,
            'earnings': earnings,
            'deductions': deductions,
            'company': company,
        })


class PayslipDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        payslip = get_object_or_404(
            Payslip.all_objects.select_related(
                'employee', 'payroll_period', 'payroll_entry',
                'payroll_entry__employee_salary',
            ),
            pk=pk,
            tenant=request.tenant,
        )
        # If a pre-generated file exists, serve it directly
        if payslip.file and hasattr(payslip.file, 'path'):
            return FileResponse(
                open(payslip.file.path, 'rb'),
                as_attachment=True,
                filename=f'payslip_{payslip.pk}.pdf',
            )
        # Otherwise generate PDF on the fly
        from xhtml2pdf import pisa

        entry = payslip.payroll_entry
        components = PayrollEntryComponent.all_objects.filter(
            tenant=request.tenant, payroll_entry=entry,
        ).select_related('pay_component').order_by('pay_component__display_order')
        earnings = [c for c in components if c.pay_component.component_type == 'earning']
        deductions = [c for c in components if c.pay_component.component_type == 'deduction']
        tenant = getattr(request, 'tenant', None)

        template = get_template('payroll/payslip_pdf.html')
        html = template.render({
            'payslip': payslip,
            'entry': entry,
            'earnings': earnings,
            'deductions': deductions,
            'company_name': tenant.name if tenant else 'Company',
            'company_address': getattr(tenant, 'address', ''),
        })

        buf = BytesIO()
        pdf = pisa.CreatePDF(html, dest=buf)
        if pdf.err:
            messages.error(request, 'Error generating payslip PDF.')
            return redirect('payroll:payslip_detail', pk=payslip.pk)

        buf.seek(0)
        emp_id = payslip.employee.employee_id or payslip.employee.pk
        period = f"{payslip.payroll_period.month:02d}_{payslip.payroll_period.year}"
        filename = f"payslip_{emp_id}_{period}.pdf"

        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class PayslipBulkGenerateView(LoginRequiredMixin, View):
    """Generates payslips for all entries in a payroll period. POST only."""

    def post(self, request, pk):
        period = get_object_or_404(
            PayrollPeriod.all_objects,
            pk=pk,
            tenant=request.tenant,
        )
        entries = (
            PayrollEntry.all_objects
            .filter(tenant=request.tenant, payroll_period=period, status='processed')
            .select_related('employee')
        )

        generated = 0
        for entry in entries:
            # Skip if payslip already exists
            if Payslip.all_objects.filter(
                tenant=request.tenant,
                payroll_entry=entry,
            ).exists():
                continue

            Payslip.all_objects.create(
                tenant=request.tenant,
                employee=entry.employee,
                payroll_period=period,
                payroll_entry=entry,
                gross_earnings=entry.gross_earnings,
                total_deductions=entry.total_deductions,
                net_pay=entry.net_pay,
                generated_date=timezone.now(),
            )
            generated += 1

        messages.success(
            request,
            f'{generated} payslips generated successfully.',
        )
        return redirect('payroll:period_detail', pk=period.pk)


# =============================================================================
# Payment Register
# =============================================================================

class PaymentRegisterListView(LoginRequiredMixin, ListView):
    model = PaymentRegister
    template_name = 'payroll/payment_register_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = PaymentRegister.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee', 'payroll_period')
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        period = self.request.GET.get('period', '')
        if period:
            qs = qs.filter(payroll_period_id=period)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_period'] = self.request.GET.get('period', '')
        context['search'] = self.request.GET.get('search', '')
        context['statuses'] = PaymentRegister.STATUS_CHOICES
        context['payroll_periods'] = (
            PayrollPeriod.all_objects
            .filter(tenant=self.request.tenant)
            .order_by('-start_date')
        )
        return context


class PaymentReconcileView(LoginRequiredMixin, View):
    def get(self, request, pk):
        register = get_object_or_404(
            PaymentRegister.all_objects.select_related('employee', 'payroll_period'),
            pk=pk,
            tenant=request.tenant,
        )
        form = PaymentReconcileForm(tenant=request.tenant)
        return render(request, 'payroll/payment_register_list.html', {
            'object': register,
            'reconcile_form': form,
        })

    def post(self, request, pk):
        register = get_object_or_404(
            PaymentRegister.all_objects.select_related('employee', 'payroll_period'),
            pk=pk,
            tenant=request.tenant,
        )
        form = PaymentReconcileForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            register.status = 'reconciled'
            register.reconciled_by = request.user
            register.reconciled_date = timezone.now()
            register.save()
            messages.success(request, 'Payment reconciled successfully.')
            return redirect('payroll:payment_register_list')
        return render(request, 'payroll/payment_register_list.html', {
            'object': register,
            'reconcile_form': form,
        })


# =============================================================================
# Reimbursements
# =============================================================================

class ReimbursementListView(LoginRequiredMixin, ListView):
    model = Reimbursement
    template_name = 'payroll/reimbursement_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = Reimbursement.all_objects.filter(
            tenant=self.request.tenant,
        ).select_related('employee')
        category = self.request.GET.get('category', '')
        if category:
            qs = qs.filter(category=category)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_id__icontains=search)
                | Q(description__icontains=search)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        context['categories'] = Reimbursement.CATEGORY_CHOICES
        context['statuses'] = Reimbursement.STATUS_CHOICES
        return context


class ReimbursementCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ReimbursementForm(tenant=request.tenant)
        return render(request, 'payroll/reimbursement_form.html', {'form': form})

    def post(self, request):
        form = ReimbursementForm(request.POST, request.FILES, tenant=request.tenant)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.tenant = request.tenant
            obj.save()
            messages.success(request, 'Reimbursement request created successfully.')
            return redirect('payroll:reimbursement_list')
        return render(request, 'payroll/reimbursement_form.html', {'form': form})


class ReimbursementDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        obj = get_object_or_404(
            Reimbursement.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        return render(request, 'payroll/reimbursement_detail.html', {'object': obj})


class ReimbursementApproveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        reimbursement = get_object_or_404(
            Reimbursement.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        form = ReimbursementApprovalForm(tenant=request.tenant)
        return render(request, 'payroll/reimbursement_detail.html', {
            'object': reimbursement,
            'approval_form': form,
        })

    def post(self, request, pk):
        reimbursement = get_object_or_404(
            Reimbursement.all_objects.select_related('employee'),
            pk=pk,
            tenant=request.tenant,
        )
        form = ReimbursementApprovalForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            reimbursement.status = form.cleaned_data.get('status', 'approved')
            reimbursement.approved_by = request.user
            reimbursement.approved_date = timezone.now()
            reimbursement.approval_remarks = form.cleaned_data.get('remarks', '')
            reimbursement.save()
            messages.success(request, 'Reimbursement request updated successfully.')
            return redirect('payroll:reimbursement_detail', pk=reimbursement.pk)
        return render(request, 'payroll/reimbursement_detail.html', {
            'object': reimbursement,
            'approval_form': form,
        })
