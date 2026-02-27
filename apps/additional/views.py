from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from .models import (
    AssetCategory, Asset, AssetAllocation, AssetMaintenance,
    ExpenseCategory, ExpensePolicy, ExpenseClaim,
    TravelPolicy, TravelRequest, TravelExpense, TravelSettlement,
    TicketCategory, Ticket, TicketComment, KnowledgeBase,
)
from .forms import (
    AssetCategoryForm, AssetForm, AssetAllocationForm, AssetReturnForm, AssetMaintenanceForm,
    ExpenseCategoryForm, ExpensePolicyForm, ExpenseClaimForm,
    TravelPolicyForm, TravelRequestForm, TravelExpenseForm, TravelSettlementForm,
    TicketCategoryForm, TicketForm, TicketCommentForm, KnowledgeBaseForm,
)


# ===========================================================================
# Asset Category Views
# ===========================================================================

class AssetCategoryListView(LoginRequiredMixin, ListView):
    model = AssetCategory
    template_name = 'additional/asset_category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = AssetCategory.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class AssetCategoryCreateView(LoginRequiredMixin, CreateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = 'additional/asset_category_form.html'
    success_url = reverse_lazy('additional:asset_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Asset Category'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Asset category created successfully.')
        return super().form_valid(form)


class AssetCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = 'additional/asset_category_form.html'
    success_url = reverse_lazy('additional:asset_category_list')

    def get_queryset(self):
        return AssetCategory.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Asset Category'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Asset category updated successfully.')
        return super().form_valid(form)


class AssetCategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(AssetCategory, pk=pk, tenant=request.tenant)
        category.delete()
        messages.success(request, 'Asset category deleted successfully.')
        return redirect('additional:asset_category_list')


# ===========================================================================
# Asset Views
# ===========================================================================

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'additional/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20

    def get_queryset(self):
        qs = Asset.objects.filter(tenant=self.request.tenant).select_related('category')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        category = self.request.GET.get('category', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(asset_id__icontains=search) | Q(serial_number__icontains=search))
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['categories'] = AssetCategory.objects.filter(tenant=self.request.tenant, is_active=True)
        context['status_choices'] = Asset.STATUS_CHOICES
        return context


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'additional/asset_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Asset'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Asset created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:asset_detail', kwargs={'pk': self.object.pk})


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'additional/asset_detail.html'
    context_object_name = 'asset'

    def get_queryset(self):
        return Asset.objects.filter(tenant=self.request.tenant).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allocations'] = self.object.allocations.select_related('employee', 'allocated_by').all()[:10]
        context['maintenance_records'] = self.object.maintenance_records.all()[:10]
        return context


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'additional/asset_form.html'

    def get_queryset(self):
        return Asset.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Asset'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Asset updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:asset_detail', kwargs={'pk': self.object.pk})


class AssetDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk, tenant=request.tenant)
        asset.delete()
        messages.success(request, 'Asset deleted successfully.')
        return redirect('additional:asset_list')


# ===========================================================================
# Asset Allocation Views
# ===========================================================================

class AssetAllocationListView(LoginRequiredMixin, ListView):
    model = AssetAllocation
    template_name = 'additional/asset_allocation_list.html'
    context_object_name = 'allocations'
    paginate_by = 20

    def get_queryset(self):
        qs = AssetAllocation.objects.filter(tenant=self.request.tenant).select_related('asset', 'employee', 'allocated_by')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(asset__name__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = AssetAllocation.STATUS_CHOICES
        return context


class AssetAllocationCreateView(LoginRequiredMixin, CreateView):
    model = AssetAllocation
    form_class = AssetAllocationForm
    template_name = 'additional/asset_allocation_form.html'
    success_url = reverse_lazy('additional:asset_allocation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Allocate Asset'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.allocated_by = self.request.user
        asset = form.instance.asset
        asset.status = 'allocated'
        asset.save()
        messages.success(self.request, 'Asset allocated successfully.')
        return super().form_valid(form)


class AssetReturnView(LoginRequiredMixin, View):
    def get(self, request, pk):
        allocation = get_object_or_404(AssetAllocation, pk=pk, tenant=request.tenant, status='active')
        form = AssetReturnForm(instance=allocation)
        return self._render(request, form, allocation)

    def post(self, request, pk):
        allocation = get_object_or_404(AssetAllocation, pk=pk, tenant=request.tenant, status='active')
        form = AssetReturnForm(request.POST, instance=allocation)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.status = 'returned'
            allocation.save()
            asset = allocation.asset
            asset.status = 'available'
            if allocation.condition_at_return:
                asset.condition = allocation.condition_at_return
            asset.save()
            messages.success(request, 'Asset returned successfully.')
            return redirect('additional:asset_allocation_list')
        return self._render(request, form, allocation)

    def _render(self, request, form, allocation):
        from django.shortcuts import render
        return render(request, 'additional/asset_return_form.html', {
            'form': form,
            'allocation': allocation,
            'title': 'Return Asset',
        })


# ===========================================================================
# Asset Maintenance Views
# ===========================================================================

class AssetMaintenanceListView(LoginRequiredMixin, ListView):
    model = AssetMaintenance
    template_name = 'additional/asset_maintenance_list.html'
    context_object_name = 'maintenance_records'
    paginate_by = 20

    def get_queryset(self):
        qs = AssetMaintenance.objects.filter(tenant=self.request.tenant).select_related('asset')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(Q(asset__name__icontains=search) | Q(vendor__icontains=search))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = AssetMaintenance.STATUS_CHOICES
        return context


class AssetMaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = AssetMaintenance
    form_class = AssetMaintenanceForm
    template_name = 'additional/asset_maintenance_form.html'
    success_url = reverse_lazy('additional:asset_maintenance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Maintenance Record'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Maintenance record created successfully.')
        return super().form_valid(form)


class AssetMaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetMaintenance
    form_class = AssetMaintenanceForm
    template_name = 'additional/asset_maintenance_form.html'
    success_url = reverse_lazy('additional:asset_maintenance_list')

    def get_queryset(self):
        return AssetMaintenance.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Maintenance Record'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Maintenance record updated successfully.')
        return super().form_valid(form)


# ===========================================================================
# Expense Category Views
# ===========================================================================

class ExpenseCategoryListView(LoginRequiredMixin, ListView):
    model = ExpenseCategory
    template_name = 'additional/expense_category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = ExpenseCategory.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'additional/expense_category_form.html'
    success_url = reverse_lazy('additional:expense_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Expense Category'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Expense category created successfully.')
        return super().form_valid(form)


class ExpenseCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'additional/expense_category_form.html'
    success_url = reverse_lazy('additional:expense_category_list')

    def get_queryset(self):
        return ExpenseCategory.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Expense Category'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Expense category updated successfully.')
        return super().form_valid(form)


class ExpenseCategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(ExpenseCategory, pk=pk, tenant=request.tenant)
        category.delete()
        messages.success(request, 'Expense category deleted successfully.')
        return redirect('additional:expense_category_list')


# ===========================================================================
# Expense Policy Views
# ===========================================================================

class ExpensePolicyListView(LoginRequiredMixin, ListView):
    model = ExpensePolicy
    template_name = 'additional/expense_policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        qs = ExpensePolicy.objects.filter(tenant=self.request.tenant).select_related('department', 'designation')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class ExpensePolicyCreateView(LoginRequiredMixin, CreateView):
    model = ExpensePolicy
    form_class = ExpensePolicyForm
    template_name = 'additional/expense_policy_form.html'
    success_url = reverse_lazy('additional:expense_policy_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Expense Policy'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Expense policy created successfully.')
        return super().form_valid(form)


class ExpensePolicyUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpensePolicy
    form_class = ExpensePolicyForm
    template_name = 'additional/expense_policy_form.html'
    success_url = reverse_lazy('additional:expense_policy_list')

    def get_queryset(self):
        return ExpensePolicy.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Expense Policy'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Expense policy updated successfully.')
        return super().form_valid(form)


class ExpensePolicyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        policy = get_object_or_404(ExpensePolicy, pk=pk, tenant=request.tenant)
        policy.delete()
        messages.success(request, 'Expense policy deleted successfully.')
        return redirect('additional:expense_policy_list')


# ===========================================================================
# Expense Claim Views
# ===========================================================================

class ExpenseClaimListView(LoginRequiredMixin, ListView):
    model = ExpenseClaim
    template_name = 'additional/expense_claim_list.html'
    context_object_name = 'claims'
    paginate_by = 20

    def get_queryset(self):
        qs = ExpenseClaim.objects.filter(tenant=self.request.tenant).select_related('employee', 'category')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(claim_number__icontains=search) |
                Q(title__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = ExpenseClaim.STATUS_CHOICES
        return context


class ExpenseClaimCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseClaim
    form_class = ExpenseClaimForm
    template_name = 'additional/expense_claim_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Expense Claim'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Expense claim created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:expense_claim_detail', kwargs={'pk': self.object.pk})


class ExpenseClaimDetailView(LoginRequiredMixin, DetailView):
    model = ExpenseClaim
    template_name = 'additional/expense_claim_detail.html'
    context_object_name = 'claim'

    def get_queryset(self):
        return ExpenseClaim.objects.filter(tenant=self.request.tenant).select_related('employee', 'category', 'approved_by')


class ExpenseClaimUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseClaim
    form_class = ExpenseClaimForm
    template_name = 'additional/expense_claim_form.html'

    def get_queryset(self):
        return ExpenseClaim.objects.filter(tenant=self.request.tenant, status='draft')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Expense Claim'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Expense claim updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:expense_claim_detail', kwargs={'pk': self.object.pk})


class ExpenseClaimDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        claim = get_object_or_404(ExpenseClaim, pk=pk, tenant=request.tenant, status='draft')
        claim.delete()
        messages.success(request, 'Expense claim deleted successfully.')
        return redirect('additional:expense_claim_list')


class ExpenseClaimSubmitView(LoginRequiredMixin, View):
    def post(self, request, pk):
        claim = get_object_or_404(ExpenseClaim, pk=pk, tenant=request.tenant, status='draft')
        claim.status = 'submitted'
        claim.submitted_date = timezone.now().date()
        claim.save()
        messages.success(request, 'Expense claim submitted successfully.')
        return redirect('additional:expense_claim_detail', pk=pk)


class ExpenseClaimApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        claim = get_object_or_404(ExpenseClaim, pk=pk, tenant=request.tenant, status='submitted')
        claim.status = 'approved'
        claim.approved_by = request.user
        claim.approved_date = timezone.now().date()
        claim.save()
        messages.success(request, 'Expense claim approved successfully.')
        return redirect('additional:expense_claim_detail', pk=pk)


class ExpenseClaimRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        claim = get_object_or_404(ExpenseClaim, pk=pk, tenant=request.tenant, status='submitted')
        claim.status = 'rejected'
        claim.rejection_reason = request.POST.get('rejection_reason', '')
        claim.save()
        messages.success(request, 'Expense claim rejected.')
        return redirect('additional:expense_claim_detail', pk=pk)


# ===========================================================================
# Travel Policy Views
# ===========================================================================

class TravelPolicyListView(LoginRequiredMixin, ListView):
    model = TravelPolicy
    template_name = 'additional/travel_policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        qs = TravelPolicy.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class TravelPolicyCreateView(LoginRequiredMixin, CreateView):
    model = TravelPolicy
    form_class = TravelPolicyForm
    template_name = 'additional/travel_policy_form.html'
    success_url = reverse_lazy('additional:travel_policy_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Travel Policy'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Travel policy created successfully.')
        return super().form_valid(form)


class TravelPolicyUpdateView(LoginRequiredMixin, UpdateView):
    model = TravelPolicy
    form_class = TravelPolicyForm
    template_name = 'additional/travel_policy_form.html'
    success_url = reverse_lazy('additional:travel_policy_list')

    def get_queryset(self):
        return TravelPolicy.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Travel Policy'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Travel policy updated successfully.')
        return super().form_valid(form)


class TravelPolicyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        policy = get_object_or_404(TravelPolicy, pk=pk, tenant=request.tenant)
        policy.delete()
        messages.success(request, 'Travel policy deleted successfully.')
        return redirect('additional:travel_policy_list')


# ===========================================================================
# Travel Request Views
# ===========================================================================

class TravelRequestListView(LoginRequiredMixin, ListView):
    model = TravelRequest
    template_name = 'additional/travel_request_list.html'
    context_object_name = 'travel_requests'
    paginate_by = 20

    def get_queryset(self):
        qs = TravelRequest.objects.filter(tenant=self.request.tenant).select_related('employee')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        travel_type = self.request.GET.get('travel_type', '').strip()
        if search:
            qs = qs.filter(
                Q(request_number__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(from_location__icontains=search) |
                Q(to_location__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if travel_type:
            qs = qs.filter(travel_type=travel_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_travel_type'] = self.request.GET.get('travel_type', '')
        context['status_choices'] = TravelRequest.STATUS_CHOICES
        context['travel_type_choices'] = TravelRequest.TRAVEL_TYPE_CHOICES
        return context


class TravelRequestCreateView(LoginRequiredMixin, CreateView):
    model = TravelRequest
    form_class = TravelRequestForm
    template_name = 'additional/travel_request_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Travel Request'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Travel request created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:travel_request_detail', kwargs={'pk': self.object.pk})


class TravelRequestDetailView(LoginRequiredMixin, DetailView):
    model = TravelRequest
    template_name = 'additional/travel_request_detail.html'
    context_object_name = 'travel_request'

    def get_queryset(self):
        return TravelRequest.objects.filter(tenant=self.request.tenant).select_related('employee', 'approved_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expenses'] = self.object.expenses.all()
        context['expense_form'] = TravelExpenseForm()
        try:
            context['settlement'] = self.object.settlement
        except TravelSettlement.DoesNotExist:
            context['settlement'] = None
        return context


class TravelRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = TravelRequest
    form_class = TravelRequestForm
    template_name = 'additional/travel_request_form.html'

    def get_queryset(self):
        return TravelRequest.objects.filter(tenant=self.request.tenant, status='draft')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Travel Request'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Travel request updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:travel_request_detail', kwargs={'pk': self.object.pk})


class TravelRequestDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        travel_request = get_object_or_404(TravelRequest, pk=pk, tenant=request.tenant, status='draft')
        travel_request.delete()
        messages.success(request, 'Travel request deleted successfully.')
        return redirect('additional:travel_request_list')


class TravelRequestSubmitView(LoginRequiredMixin, View):
    def post(self, request, pk):
        travel_request = get_object_or_404(TravelRequest, pk=pk, tenant=request.tenant, status='draft')
        travel_request.status = 'submitted'
        travel_request.save()
        messages.success(request, 'Travel request submitted successfully.')
        return redirect('additional:travel_request_detail', pk=pk)


class TravelRequestApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        travel_request = get_object_or_404(TravelRequest, pk=pk, tenant=request.tenant, status='submitted')
        travel_request.status = 'approved'
        travel_request.approved_by = request.user
        travel_request.approved_date = timezone.now().date()
        travel_request.save()
        messages.success(request, 'Travel request approved successfully.')
        return redirect('additional:travel_request_detail', pk=pk)


# ===========================================================================
# Travel Expense Views
# ===========================================================================

class TravelExpenseCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        travel_request = get_object_or_404(TravelRequest, pk=pk, tenant=request.tenant)
        form = TravelExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.tenant = request.tenant
            expense.travel_request = travel_request
            expense.save()
            messages.success(request, 'Travel expense added successfully.')
        else:
            messages.error(request, 'Error adding travel expense. Please check the form.')
        return redirect('additional:travel_request_detail', pk=pk)


# ===========================================================================
# Travel Settlement Views
# ===========================================================================

class TravelSettlementCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        travel_request = get_object_or_404(TravelRequest, pk=pk, tenant=request.tenant)
        total_expenses = travel_request.total_expenses
        advance_given = travel_request.advance_amount if travel_request.advance_required else 0
        settlement_amount = total_expenses - advance_given
        form = TravelSettlementForm(initial={
            'total_expenses': total_expenses,
            'advance_given': advance_given,
            'settlement_amount': settlement_amount,
        })
        return self._render(request, form, travel_request)

    def post(self, request, pk):
        travel_request = get_object_or_404(TravelRequest, pk=pk, tenant=request.tenant)
        form = TravelSettlementForm(request.POST)
        if form.is_valid():
            settlement = form.save(commit=False)
            settlement.tenant = request.tenant
            settlement.travel_request = travel_request
            settlement.save()
            messages.success(request, 'Travel settlement created successfully.')
            return redirect('additional:travel_request_detail', pk=pk)
        return self._render(request, form, travel_request)

    def _render(self, request, form, travel_request):
        from django.shortcuts import render
        return render(request, 'additional/travel_settlement_form.html', {
            'form': form,
            'travel_request': travel_request,
            'title': 'Create Settlement',
        })


class TravelSettlementUpdateView(LoginRequiredMixin, UpdateView):
    model = TravelSettlement
    form_class = TravelSettlementForm
    template_name = 'additional/travel_settlement_form.html'

    def get_queryset(self):
        return TravelSettlement.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Settlement'
        context['travel_request'] = self.object.travel_request
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Travel settlement updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:travel_request_detail', kwargs={'pk': self.object.travel_request.pk})


# ===========================================================================
# Ticket Category Views
# ===========================================================================

class TicketCategoryListView(LoginRequiredMixin, ListView):
    model = TicketCategory
    template_name = 'additional/ticket_category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = TicketCategory.objects.filter(tenant=self.request.tenant).select_related('department')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class TicketCategoryCreateView(LoginRequiredMixin, CreateView):
    model = TicketCategory
    form_class = TicketCategoryForm
    template_name = 'additional/ticket_category_form.html'
    success_url = reverse_lazy('additional:ticket_category_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Ticket Category'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Ticket category created successfully.')
        return super().form_valid(form)


class TicketCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = TicketCategory
    form_class = TicketCategoryForm
    template_name = 'additional/ticket_category_form.html'
    success_url = reverse_lazy('additional:ticket_category_list')

    def get_queryset(self):
        return TicketCategory.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Ticket Category'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Ticket category updated successfully.')
        return super().form_valid(form)


class TicketCategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(TicketCategory, pk=pk, tenant=request.tenant)
        category.delete()
        messages.success(request, 'Ticket category deleted successfully.')
        return redirect('additional:ticket_category_list')


# ===========================================================================
# Ticket Views
# ===========================================================================

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'additional/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 20

    def get_queryset(self):
        qs = Ticket.objects.filter(tenant=self.request.tenant).select_related('employee', 'category', 'assigned_to')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        priority = self.request.GET.get('priority', '').strip()
        if search:
            qs = qs.filter(
                Q(ticket_number__icontains=search) |
                Q(subject__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search)
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
        context['status_choices'] = Ticket.STATUS_CHOICES
        context['priority_choices'] = Ticket.PRIORITY_CHOICES
        return context


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'additional/ticket_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Ticket'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        if form.instance.category and form.instance.category.default_assignee:
            if not form.instance.assigned_to:
                form.instance.assigned_to = form.instance.category.default_assignee
                form.instance.status = 'assigned'
        messages.success(self.request, 'Ticket created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:ticket_detail', kwargs={'pk': self.object.pk})


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'additional/ticket_detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        return Ticket.objects.filter(tenant=self.request.tenant).select_related('employee', 'category', 'assigned_to')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('user').all()
        context['comment_form'] = TicketCommentForm()
        return context


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'additional/ticket_form.html'

    def get_queryset(self):
        return Ticket.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Ticket'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Ticket updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:ticket_detail', kwargs={'pk': self.object.pk})


class TicketCloseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk, tenant=request.tenant)
        ticket.status = 'closed'
        ticket.closed_date = timezone.now()
        ticket.save()
        messages.success(request, 'Ticket closed successfully.')
        return redirect('additional:ticket_detail', pk=pk)


class TicketReopenView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk, tenant=request.tenant, status='closed')
        ticket.status = 'reopened'
        ticket.closed_date = None
        ticket.save()
        messages.success(request, 'Ticket reopened successfully.')
        return redirect('additional:ticket_detail', pk=pk)


class TicketCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk, tenant=request.tenant)
        form = TicketCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tenant = request.tenant
            comment.ticket = ticket
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
        else:
            messages.error(request, 'Error adding comment. Please check the form.')
        return redirect('additional:ticket_detail', pk=pk)


# ===========================================================================
# Knowledge Base Views
# ===========================================================================

class KnowledgeBaseListView(LoginRequiredMixin, ListView):
    model = KnowledgeBase
    template_name = 'additional/knowledge_base_list.html'
    context_object_name = 'articles'
    paginate_by = 20

    def get_queryset(self):
        qs = KnowledgeBase.objects.filter(tenant=self.request.tenant).select_related('category', 'author')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class KnowledgeBaseCreateView(LoginRequiredMixin, CreateView):
    model = KnowledgeBase
    form_class = KnowledgeBaseForm
    template_name = 'additional/knowledge_base_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Article'
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.author = self.request.user
        messages.success(self.request, 'Article created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:knowledge_base_detail', kwargs={'pk': self.object.pk})


class KnowledgeBaseDetailView(LoginRequiredMixin, DetailView):
    model = KnowledgeBase
    template_name = 'additional/knowledge_base_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return KnowledgeBase.objects.filter(tenant=self.request.tenant).select_related('category', 'author')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj


class KnowledgeBaseUpdateView(LoginRequiredMixin, UpdateView):
    model = KnowledgeBase
    form_class = KnowledgeBaseForm
    template_name = 'additional/knowledge_base_form.html'

    def get_queryset(self):
        return KnowledgeBase.objects.filter(tenant=self.request.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Article'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Article updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('additional:knowledge_base_detail', kwargs={'pk': self.object.pk})


class KnowledgeBaseDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(KnowledgeBase, pk=pk, tenant=request.tenant)
        article.delete()
        messages.success(request, 'Article deleted successfully.')
        return redirect('additional:knowledge_base_list')
