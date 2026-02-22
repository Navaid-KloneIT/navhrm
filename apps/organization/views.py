from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy

from .models import Company, Department, Designation, CostCenter
from .forms import CompanyForm, DepartmentForm, DesignationForm, CostCenterForm


# ---------------------------------------------------------------------------
# Company Views
# ---------------------------------------------------------------------------

class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'organization/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20

    def get_queryset(self):
        qs = Company.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(legal_name__icontains=search) |
                Q(email__icontains=search) |
                Q(industry__icontains=search) |
                Q(city__icontains=search)
            )
        return qs


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'organization/company_form.html'
    success_url = reverse_lazy('organization:company_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Company "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Company'
        return context


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'organization/company_detail.html'
    context_object_name = 'company'

    def get_queryset(self):
        return Company.objects.filter(tenant=self.request.tenant)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'organization/company_form.html'
    success_url = reverse_lazy('organization:company_list')

    def get_queryset(self):
        return Company.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Company "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Company'
        return context


class CompanyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk, tenant=request.tenant)
        name = company.name
        company.delete()
        messages.success(request, f'Company "{name}" deleted successfully.')
        return redirect('organization:company_list')


# ---------------------------------------------------------------------------
# Department Views
# ---------------------------------------------------------------------------

class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'organization/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20

    def get_queryset(self):
        qs = Department.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        return qs


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'organization/department_form.html'
    success_url = reverse_lazy('organization:department_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Department "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Department'
        return context


class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'organization/department_form.html'
    success_url = reverse_lazy('organization:department_list')

    def get_queryset(self):
        return Department.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Department "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Department'
        return context


class DepartmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        department = get_object_or_404(Department, pk=pk, tenant=request.tenant)
        name = department.name
        department.delete()
        messages.success(request, f'Department "{name}" deleted successfully.')
        return redirect('organization:department_list')


# ---------------------------------------------------------------------------
# Designation Views
# ---------------------------------------------------------------------------

class DesignationListView(LoginRequiredMixin, ListView):
    model = Designation
    template_name = 'organization/designation_list.html'
    context_object_name = 'designations'
    paginate_by = 20

    def get_queryset(self):
        qs = Designation.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        return qs


class DesignationCreateView(LoginRequiredMixin, CreateView):
    model = Designation
    form_class = DesignationForm
    template_name = 'organization/designation_form.html'
    success_url = reverse_lazy('organization:designation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Designation "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Designation'
        return context


class DesignationUpdateView(LoginRequiredMixin, UpdateView):
    model = Designation
    form_class = DesignationForm
    template_name = 'organization/designation_form.html'
    success_url = reverse_lazy('organization:designation_list')

    def get_queryset(self):
        return Designation.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Designation "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Designation'
        return context


class DesignationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        designation = get_object_or_404(Designation, pk=pk, tenant=request.tenant)
        name = designation.name
        designation.delete()
        messages.success(request, f'Designation "{name}" deleted successfully.')
        return redirect('organization:designation_list')


# ---------------------------------------------------------------------------
# Org Chart View
# ---------------------------------------------------------------------------

class OrgChartView(LoginRequiredMixin, View):
    def get(self, request):
        if request.GET.get('format') != 'json':
            return render(request, 'organization/org_chart.html')

        departments = Department.objects.filter(
            tenant=request.tenant,
            is_active=True,
        ).select_related('parent', 'head', 'company')

        nodes = []
        for dept in departments:
            node = {
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'parent_id': dept.parent_id,
                'company': dept.company.name if dept.company else None,
                'head_name': str(dept.head) if dept.head else None,
                'employee_count': dept.employee_count,
            }
            nodes.append(node)

        return JsonResponse(nodes, safe=False)


# ---------------------------------------------------------------------------
# Cost Center Views
# ---------------------------------------------------------------------------

class CostCenterListView(LoginRequiredMixin, ListView):
    model = CostCenter
    template_name = 'organization/costcenter_list.html'
    context_object_name = 'cost_centers'
    paginate_by = 20

    def get_queryset(self):
        qs = CostCenter.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        return qs


class CostCenterCreateView(LoginRequiredMixin, CreateView):
    model = CostCenter
    form_class = CostCenterForm
    template_name = 'organization/costcenter_form.html'
    success_url = reverse_lazy('organization:costcenter_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, f'Cost center "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Cost Center'
        return context


class CostCenterUpdateView(LoginRequiredMixin, UpdateView):
    model = CostCenter
    form_class = CostCenterForm
    template_name = 'organization/costcenter_form.html'
    success_url = reverse_lazy('organization:costcenter_list')

    def get_queryset(self):
        return CostCenter.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Cost center "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Cost Center'
        return context


class CostCenterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cost_center = get_object_or_404(CostCenter, pk=pk, tenant=request.tenant)
        name = cost_center.name
        cost_center.delete()
        messages.success(request, f'Cost center "{name}" deleted successfully.')
        return redirect('organization:costcenter_list')
