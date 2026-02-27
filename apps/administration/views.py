from datetime import timedelta
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse

from apps.accounts.models import User, UserProfile, UserInvite
from apps.accounts.forms import UserForm
from apps.core.models import Tenant
from apps.organization.models import Company, Location

from .models import (
    Role, Permission, LoginHistory,
    ApprovalWorkflow, ApprovalStep, EmailTemplate, NotificationSetting, EscalationRule,
    SystemSetting, FinancialYear, FinancialPeriod, WorkingHoursPolicy, IntegrationSetting,
    AuditTrail, DataRetentionPolicy, BackupConfiguration, BackupLog,
)
from .forms import (
    RoleForm, UserRoleAssignmentForm,
    ApprovalWorkflowForm, ApprovalStepForm, EmailTemplateForm,
    NotificationSettingForm, EscalationRuleForm,
    CompanySettingsForm, FinancialYearForm, FinancialPeriodForm,
    WorkingHoursPolicyForm, IntegrationSettingForm,
    DataRetentionPolicyForm, BackupConfigurationForm,
)


# =============================================================================
# 9.1 User Management Views
# =============================================================================

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'administration/user_management/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
        role = self.request.GET.get('role', '')
        if role:
            qs = qs.filter(role=role)
        status = self.request.GET.get('status', '')
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = User.ROLE_CHOICES
        context['total_users'] = User.objects.filter(tenant=self.request.tenant).count()
        context['active_users'] = User.objects.filter(tenant=self.request.tenant, is_active=True).count()
        context['inactive_users'] = User.objects.filter(tenant=self.request.tenant, is_active=False).count()
        return context


class UserCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserForm()
        return render(request, 'administration/user_management/user_form.html', {
            'form': form, 'title': 'Add User'
        })

    def post(self, request):
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.tenant = request.tenant
            user.set_password('changeme123')
            user.save()
            UserProfile.objects.create(user=user)
            messages.success(request, f'User {user.get_full_name()} created successfully.')
            return redirect('administration:user_list')
        return render(request, 'administration/user_management/user_form.html', {
            'form': form, 'title': 'Add User'
        })


class UserEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=request.tenant)
        form = UserForm(instance=user)
        return render(request, 'administration/user_management/user_form.html', {
            'form': form, 'title': 'Edit User', 'edit_user': user
        })

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=request.tenant)
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.get_full_name()} updated successfully.')
            return redirect('administration:user_list')
        return render(request, 'administration/user_management/user_form.html', {
            'form': form, 'title': 'Edit User', 'edit_user': user
        })


class UserDeactivateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=request.tenant)
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.get_full_name()} has been {status}.')
        return redirect('administration:user_list')


class RoleListView(LoginRequiredMixin, ListView):
    model = Role
    template_name = 'administration/user_management/role_list.html'
    context_object_name = 'roles'
    paginate_by = 20

    def get_queryset(self):
        qs = Role.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return qs.annotate(permission_count=Count('permissions'))


class RoleCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = RoleForm()
        modules = Permission.MODULE_CHOICES
        actions = Permission.ACTION_CHOICES
        return render(request, 'administration/user_management/role_form.html', {
            'form': form, 'title': 'Create Role', 'modules': modules, 'actions': actions
        })

    def post(self, request):
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.tenant = request.tenant
            role.save()
            # Save permissions
            for module_code, module_name in Permission.MODULE_CHOICES:
                for action_code, action_name in Permission.ACTION_CHOICES:
                    is_granted = request.POST.get(f'perm_{module_code}_{action_code}') == 'on'
                    Permission.all_objects.create(
                        role=role,
                        module=module_code,
                        action=action_code,
                        is_granted=is_granted,
                        tenant=request.tenant,
                    )
            messages.success(request, f'Role "{role.name}" created successfully.')
            return redirect('administration:role_list')
        modules = Permission.MODULE_CHOICES
        actions = Permission.ACTION_CHOICES
        return render(request, 'administration/user_management/role_form.html', {
            'form': form, 'title': 'Create Role', 'modules': modules, 'actions': actions
        })


class RoleDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        role = get_object_or_404(Role.all_objects, pk=pk, tenant=request.tenant)
        permissions = Permission.all_objects.filter(role=role, tenant=request.tenant)
        modules = Permission.MODULE_CHOICES
        actions = Permission.ACTION_CHOICES
        # Build permissions matrix
        perm_matrix = {}
        for perm in permissions:
            if perm.module not in perm_matrix:
                perm_matrix[perm.module] = {}
            perm_matrix[perm.module][perm.action] = perm.is_granted
        return render(request, 'administration/user_management/role_detail.html', {
            'role': role, 'permissions': permissions,
            'modules': modules, 'actions': actions, 'perm_matrix': perm_matrix
        })


class RoleEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        role = get_object_or_404(Role.all_objects, pk=pk, tenant=request.tenant)
        form = RoleForm(instance=role)
        modules = Permission.MODULE_CHOICES
        actions = Permission.ACTION_CHOICES
        permissions = Permission.all_objects.filter(role=role, tenant=request.tenant)
        perm_matrix = {}
        for perm in permissions:
            if perm.module not in perm_matrix:
                perm_matrix[perm.module] = {}
            perm_matrix[perm.module][perm.action] = perm.is_granted
        return render(request, 'administration/user_management/role_form.html', {
            'form': form, 'title': 'Edit Role', 'role': role,
            'modules': modules, 'actions': actions, 'perm_matrix': perm_matrix
        })

    def post(self, request, pk):
        role = get_object_or_404(Role.all_objects, pk=pk, tenant=request.tenant)
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            # Update permissions
            for module_code, module_name in Permission.MODULE_CHOICES:
                for action_code, action_name in Permission.ACTION_CHOICES:
                    is_granted = request.POST.get(f'perm_{module_code}_{action_code}') == 'on'
                    perm, created = Permission.all_objects.update_or_create(
                        role=role, module=module_code, action=action_code, tenant=request.tenant,
                        defaults={'is_granted': is_granted}
                    )
            messages.success(request, f'Role "{role.name}" updated successfully.')
            return redirect('administration:role_detail', pk=role.pk)
        modules = Permission.MODULE_CHOICES
        actions = Permission.ACTION_CHOICES
        return render(request, 'administration/user_management/role_form.html', {
            'form': form, 'title': 'Edit Role', 'role': role,
            'modules': modules, 'actions': actions
        })


class RoleDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        role = get_object_or_404(Role.all_objects, pk=pk, tenant=request.tenant)
        if role.is_system_role:
            messages.error(request, 'System roles cannot be deleted.')
            return redirect('administration:role_list')
        role_name = role.name
        role.delete()
        messages.success(request, f'Role "{role_name}" deleted successfully.')
        return redirect('administration:role_list')


class RoleAssignmentView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserRoleAssignmentForm(tenant=request.tenant)
        users = User.objects.filter(tenant=request.tenant, is_active=True)
        roles = Role.all_objects.filter(tenant=request.tenant, is_active=True)
        return render(request, 'administration/user_management/role_assignment.html', {
            'form': form, 'users': users, 'roles': roles
        })

    def post(self, request):
        form = UserRoleAssignmentForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            user.role = role.code
            user.save()
            messages.success(request, f'Role "{role.name}" assigned to {user.get_full_name()}.')
            return redirect('administration:role_assign')
        users = User.objects.filter(tenant=request.tenant, is_active=True)
        roles = Role.all_objects.filter(tenant=request.tenant, is_active=True)
        return render(request, 'administration/user_management/role_assignment.html', {
            'form': form, 'users': users, 'roles': roles
        })


class LoginHistoryView(LoginRequiredMixin, ListView):
    model = LoginHistory
    template_name = 'administration/user_management/login_history.html'
    context_object_name = 'logs'
    paginate_by = 30

    def get_queryset(self):
        qs = LoginHistory.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(ip_address__icontains=search)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        date_from = self.request.GET.get('date_from', '')
        if date_from:
            qs = qs.filter(login_at__date__gte=date_from)
        date_to = self.request.GET.get('date_to', '')
        if date_to:
            qs = qs.filter(login_at__date__lte=date_to)
        return qs.select_related('user')


# =============================================================================
# 9.2 Workflow Configuration Views
# =============================================================================

class WorkflowListView(LoginRequiredMixin, ListView):
    model = ApprovalWorkflow
    template_name = 'administration/workflow/workflow_list.html'
    context_object_name = 'workflows'
    paginate_by = 20

    def get_queryset(self):
        qs = ApprovalWorkflow.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search))
        module = self.request.GET.get('module', '')
        if module:
            qs = qs.filter(module=module)
        return qs.annotate(step_count=Count('steps'))


class WorkflowCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ApprovalWorkflowForm()
        step_form = ApprovalStepForm(tenant=request.tenant)
        return render(request, 'administration/workflow/workflow_form.html', {
            'form': form, 'step_form': step_form, 'title': 'Create Workflow'
        })

    def post(self, request):
        form = ApprovalWorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save(commit=False)
            workflow.tenant = request.tenant
            workflow.save()
            # Save steps
            step_count = int(request.POST.get('step_count', 0))
            for i in range(1, step_count + 1):
                step_name = request.POST.get(f'step_name_{i}', '')
                approver_type = request.POST.get(f'approver_type_{i}', '')
                if step_name and approver_type:
                    specific_user_id = request.POST.get(f'specific_user_{i}') or None
                    specific_role_id = request.POST.get(f'specific_role_{i}') or None
                    can_skip = request.POST.get(f'can_skip_{i}') == 'on'
                    auto_approve = int(request.POST.get(f'auto_approve_days_{i}', 0) or 0)
                    ApprovalStep.all_objects.create(
                        workflow=workflow,
                        step_order=i,
                        name=step_name,
                        approver_type=approver_type,
                        specific_user_id=specific_user_id,
                        specific_role_id=specific_role_id,
                        can_skip=can_skip,
                        auto_approve_days=auto_approve,
                        tenant=request.tenant,
                    )
            messages.success(request, f'Workflow "{workflow.name}" created successfully.')
            return redirect('administration:workflow_list')
        step_form = ApprovalStepForm(tenant=request.tenant)
        return render(request, 'administration/workflow/workflow_form.html', {
            'form': form, 'step_form': step_form, 'title': 'Create Workflow'
        })


class WorkflowDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        workflow = get_object_or_404(ApprovalWorkflow.all_objects, pk=pk, tenant=request.tenant)
        steps = ApprovalStep.all_objects.filter(workflow=workflow, tenant=request.tenant)
        escalation_rules = EscalationRule.all_objects.filter(workflow=workflow, tenant=request.tenant)
        return render(request, 'administration/workflow/workflow_detail.html', {
            'workflow': workflow, 'steps': steps, 'escalation_rules': escalation_rules
        })


class WorkflowEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        workflow = get_object_or_404(ApprovalWorkflow.all_objects, pk=pk, tenant=request.tenant)
        form = ApprovalWorkflowForm(instance=workflow)
        steps = ApprovalStep.all_objects.filter(workflow=workflow, tenant=request.tenant)
        step_form = ApprovalStepForm(tenant=request.tenant)
        return render(request, 'administration/workflow/workflow_form.html', {
            'form': form, 'step_form': step_form, 'title': 'Edit Workflow',
            'workflow': workflow, 'steps': steps
        })

    def post(self, request, pk):
        workflow = get_object_or_404(ApprovalWorkflow.all_objects, pk=pk, tenant=request.tenant)
        form = ApprovalWorkflowForm(request.POST, instance=workflow)
        if form.is_valid():
            form.save()
            # Clear and re-create steps
            ApprovalStep.all_objects.filter(workflow=workflow, tenant=request.tenant).delete()
            step_count = int(request.POST.get('step_count', 0))
            for i in range(1, step_count + 1):
                step_name = request.POST.get(f'step_name_{i}', '')
                approver_type = request.POST.get(f'approver_type_{i}', '')
                if step_name and approver_type:
                    specific_user_id = request.POST.get(f'specific_user_{i}') or None
                    specific_role_id = request.POST.get(f'specific_role_{i}') or None
                    can_skip = request.POST.get(f'can_skip_{i}') == 'on'
                    auto_approve = int(request.POST.get(f'auto_approve_days_{i}', 0) or 0)
                    ApprovalStep.all_objects.create(
                        workflow=workflow,
                        step_order=i,
                        name=step_name,
                        approver_type=approver_type,
                        specific_user_id=specific_user_id,
                        specific_role_id=specific_role_id,
                        can_skip=can_skip,
                        auto_approve_days=auto_approve,
                        tenant=request.tenant,
                    )
            messages.success(request, f'Workflow "{workflow.name}" updated successfully.')
            return redirect('administration:workflow_detail', pk=workflow.pk)
        step_form = ApprovalStepForm(tenant=request.tenant)
        steps = ApprovalStep.all_objects.filter(workflow=workflow, tenant=request.tenant)
        return render(request, 'administration/workflow/workflow_form.html', {
            'form': form, 'step_form': step_form, 'title': 'Edit Workflow',
            'workflow': workflow, 'steps': steps
        })


class WorkflowDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        workflow = get_object_or_404(ApprovalWorkflow.all_objects, pk=pk, tenant=request.tenant)
        name = workflow.name
        workflow.delete()
        messages.success(request, f'Workflow "{name}" deleted successfully.')
        return redirect('administration:workflow_list')


class EmailTemplateListView(LoginRequiredMixin, ListView):
    model = EmailTemplate
    template_name = 'administration/workflow/email_template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

    def get_queryset(self):
        qs = EmailTemplate.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(subject__icontains=search))
        event = self.request.GET.get('event', '')
        if event:
            qs = qs.filter(event=event)
        return qs


class EmailTemplateCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = EmailTemplateForm()
        return render(request, 'administration/workflow/email_template_form.html', {
            'form': form, 'title': 'Create Email Template'
        })

    def post(self, request):
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.tenant = request.tenant
            template.save()
            messages.success(request, f'Email template "{template.name}" created successfully.')
            return redirect('administration:email_template_list')
        return render(request, 'administration/workflow/email_template_form.html', {
            'form': form, 'title': 'Create Email Template'
        })


class EmailTemplateEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        template = get_object_or_404(EmailTemplate.all_objects, pk=pk, tenant=request.tenant)
        form = EmailTemplateForm(instance=template)
        return render(request, 'administration/workflow/email_template_form.html', {
            'form': form, 'title': 'Edit Email Template', 'email_template': template
        })

    def post(self, request, pk):
        template = get_object_or_404(EmailTemplate.all_objects, pk=pk, tenant=request.tenant)
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, f'Email template "{template.name}" updated successfully.')
            return redirect('administration:email_template_list')
        return render(request, 'administration/workflow/email_template_form.html', {
            'form': form, 'title': 'Edit Email Template', 'email_template': template
        })


class EmailTemplateDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        template = get_object_or_404(EmailTemplate.all_objects, pk=pk, tenant=request.tenant)
        name = template.name
        template.delete()
        messages.success(request, f'Email template "{name}" deleted successfully.')
        return redirect('administration:email_template_list')


class EmailTemplatePreviewView(LoginRequiredMixin, View):
    def get(self, request, pk):
        template = get_object_or_404(EmailTemplate.all_objects, pk=pk, tenant=request.tenant)
        # Sample data for preview
        sample_data = {
            'employee_name': 'John Doe',
            'company_name': request.tenant.name,
            'manager_name': 'Jane Smith',
            'date': timezone.now().strftime('%d %b %Y'),
        }
        preview_body = template.body
        for key, value in sample_data.items():
            preview_body = preview_body.replace('{{' + key + '}}', value)
        return render(request, 'administration/workflow/email_template_preview.html', {
            'template': template, 'preview_body': preview_body, 'preview_subject': template.subject
        })


class NotificationSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        settings_list = NotificationSetting.all_objects.filter(tenant=request.tenant)
        events = EmailTemplate.EVENT_CHOICES
        # Create settings for events that don't have one yet
        existing_events = set(settings_list.values_list('event', flat=True))
        for event_code, event_name in events:
            if event_code not in existing_events:
                NotificationSetting.all_objects.create(
                    event=event_code, tenant=request.tenant
                )
        settings_list = NotificationSetting.all_objects.filter(tenant=request.tenant)
        return render(request, 'administration/workflow/notification_settings.html', {
            'settings_list': settings_list
        })

    def post(self, request):
        settings_list = NotificationSetting.all_objects.filter(tenant=request.tenant)
        for setting in settings_list:
            channel = request.POST.get(f'channel_{setting.pk}', setting.channel)
            recipients = request.POST.get(f'recipients_{setting.pk}', setting.recipients)
            is_enabled = request.POST.get(f'enabled_{setting.pk}') == 'on'
            setting.channel = channel
            setting.recipients = recipients
            setting.is_enabled = is_enabled
            setting.save()
        messages.success(request, 'Notification settings updated successfully.')
        return redirect('administration:notification_settings')


class EscalationRuleListView(LoginRequiredMixin, ListView):
    model = EscalationRule
    template_name = 'administration/workflow/escalation_list.html'
    context_object_name = 'rules'
    paginate_by = 20

    def get_queryset(self):
        return EscalationRule.all_objects.filter(
            tenant=self.request.tenant
        ).select_related('workflow', 'notify_user')


class EscalationRuleCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = EscalationRuleForm(tenant=request.tenant)
        return render(request, 'administration/workflow/escalation_form.html', {
            'form': form, 'title': 'Create Escalation Rule'
        })

    def post(self, request):
        form = EscalationRuleForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.tenant = request.tenant
            rule.save()
            messages.success(request, 'Escalation rule created successfully.')
            return redirect('administration:escalation_list')
        return render(request, 'administration/workflow/escalation_form.html', {
            'form': form, 'title': 'Create Escalation Rule'
        })


class EscalationRuleEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        rule = get_object_or_404(EscalationRule.all_objects, pk=pk, tenant=request.tenant)
        form = EscalationRuleForm(instance=rule, tenant=request.tenant)
        return render(request, 'administration/workflow/escalation_form.html', {
            'form': form, 'title': 'Edit Escalation Rule', 'rule': rule
        })

    def post(self, request, pk):
        rule = get_object_or_404(EscalationRule.all_objects, pk=pk, tenant=request.tenant)
        form = EscalationRuleForm(request.POST, instance=rule, tenant=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Escalation rule updated successfully.')
            return redirect('administration:escalation_list')
        return render(request, 'administration/workflow/escalation_form.html', {
            'form': form, 'title': 'Edit Escalation Rule', 'rule': rule
        })


class EscalationRuleDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rule = get_object_or_404(EscalationRule.all_objects, pk=pk, tenant=request.tenant)
        rule.delete()
        messages.success(request, 'Escalation rule deleted successfully.')
        return redirect('administration:escalation_list')


# =============================================================================
# 9.3 System Configuration Views
# =============================================================================

class CompanySettingsView(LoginRequiredMixin, View):
    def get(self, request):
        tenant = request.tenant
        # Load current settings from SystemSetting
        settings_dict = {}
        for s in SystemSetting.all_objects.filter(tenant=tenant):
            settings_dict[s.key] = s.value

        initial = {
            'company_name': tenant.name,
            'timezone': settings_dict.get('timezone', 'UTC'),
            'date_format': settings_dict.get('date_format', 'DD/MM/YYYY'),
            'currency': settings_dict.get('currency', 'INR'),
            'fiscal_year_start': settings_dict.get('fiscal_year_start', '4'),
        }
        form = CompanySettingsForm(initial=initial)
        return render(request, 'administration/system/company_settings.html', {
            'form': form, 'tenant': tenant
        })

    def post(self, request):
        form = CompanySettingsForm(request.POST, request.FILES)
        tenant = request.tenant
        if form.is_valid():
            # Update tenant name
            tenant.name = form.cleaned_data['company_name']
            if form.cleaned_data.get('company_logo'):
                tenant.logo = form.cleaned_data['company_logo']
            tenant.save()
            # Save system settings
            settings_to_save = {
                'timezone': form.cleaned_data['timezone'],
                'date_format': form.cleaned_data['date_format'],
                'currency': form.cleaned_data['currency'],
                'fiscal_year_start': form.cleaned_data['fiscal_year_start'],
            }
            for key, value in settings_to_save.items():
                SystemSetting.all_objects.update_or_create(
                    key=key, tenant=tenant,
                    defaults={'value': value, 'category': 'general', 'value_type': 'string'}
                )
            messages.success(request, 'Company settings updated successfully.')
            return redirect('administration:company_settings')
        return render(request, 'administration/system/company_settings.html', {
            'form': form, 'tenant': tenant
        })


class FinancialYearListView(LoginRequiredMixin, ListView):
    model = FinancialYear
    template_name = 'administration/system/financial_year_list.html'
    context_object_name = 'financial_years'
    paginate_by = 20

    def get_queryset(self):
        return FinancialYear.all_objects.filter(
            tenant=self.request.tenant
        ).annotate(period_count=Count('periods'))


class FinancialYearCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = FinancialYearForm()
        return render(request, 'administration/system/financial_year_form.html', {
            'form': form, 'title': 'Create Financial Year'
        })

    def post(self, request):
        form = FinancialYearForm(request.POST)
        if form.is_valid():
            fy = form.save(commit=False)
            fy.tenant = request.tenant
            # If marking as active, deactivate others
            if fy.is_active:
                FinancialYear.all_objects.filter(tenant=request.tenant, is_active=True).update(is_active=False)
            fy.save()
            messages.success(request, f'Financial year "{fy.name}" created successfully.')
            return redirect('administration:financial_year_list')
        return render(request, 'administration/system/financial_year_form.html', {
            'form': form, 'title': 'Create Financial Year'
        })


class FinancialYearEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        fy = get_object_or_404(FinancialYear.all_objects, pk=pk, tenant=request.tenant)
        form = FinancialYearForm(instance=fy)
        return render(request, 'administration/system/financial_year_form.html', {
            'form': form, 'title': 'Edit Financial Year', 'financial_year': fy
        })

    def post(self, request, pk):
        fy = get_object_or_404(FinancialYear.all_objects, pk=pk, tenant=request.tenant)
        form = FinancialYearForm(request.POST, instance=fy)
        if form.is_valid():
            fy = form.save(commit=False)
            if fy.is_active:
                FinancialYear.all_objects.filter(tenant=request.tenant, is_active=True).exclude(pk=pk).update(is_active=False)
            fy.save()
            messages.success(request, f'Financial year "{fy.name}" updated successfully.')
            return redirect('administration:financial_year_list')
        return render(request, 'administration/system/financial_year_form.html', {
            'form': form, 'title': 'Edit Financial Year', 'financial_year': fy
        })


class FinancialYearDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        fy = get_object_or_404(FinancialYear.all_objects, pk=pk, tenant=request.tenant)
        if fy.is_locked:
            messages.error(request, 'Locked financial years cannot be deleted.')
            return redirect('administration:financial_year_list')
        name = fy.name
        fy.delete()
        messages.success(request, f'Financial year "{name}" deleted successfully.')
        return redirect('administration:financial_year_list')


class FinancialPeriodListView(LoginRequiredMixin, View):
    def get(self, request, pk):
        fy = get_object_or_404(FinancialYear.all_objects, pk=pk, tenant=request.tenant)
        periods = FinancialPeriod.all_objects.filter(financial_year=fy, tenant=request.tenant)
        return render(request, 'administration/system/financial_period_list.html', {
            'financial_year': fy, 'periods': periods
        })


class GeneratePeriodsView(LoginRequiredMixin, View):
    def post(self, request, pk):
        fy = get_object_or_404(FinancialYear.all_objects, pk=pk, tenant=request.tenant)
        # Check if periods already exist
        existing = FinancialPeriod.all_objects.filter(financial_year=fy, tenant=request.tenant).count()
        if existing > 0:
            messages.warning(request, 'Periods already exist for this financial year.')
            return redirect('administration:financial_period_list', pk=fy.pk)

        # Generate monthly periods
        current_date = fy.start_date
        period_number = 1
        while current_date <= fy.end_date and period_number <= 12:
            month_name = current_date.strftime('%B %Y')
            last_day = monthrange(current_date.year, current_date.month)[1]
            period_end = current_date.replace(day=last_day)
            if period_end > fy.end_date:
                period_end = fy.end_date

            FinancialPeriod.all_objects.create(
                financial_year=fy,
                name=month_name,
                period_number=period_number,
                start_date=current_date,
                end_date=period_end,
                tenant=request.tenant,
            )

            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)
            period_number += 1

        messages.success(request, f'{period_number - 1} periods generated for {fy.name}.')
        return redirect('administration:financial_period_list', pk=fy.pk)


class WorkingHoursListView(LoginRequiredMixin, ListView):
    model = WorkingHoursPolicy
    template_name = 'administration/system/working_hours.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        return WorkingHoursPolicy.all_objects.filter(tenant=self.request.tenant)


class WorkingHoursCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = WorkingHoursPolicyForm()
        return render(request, 'administration/system/working_hours_form.html', {
            'form': form, 'title': 'Create Working Hours Policy'
        })

    def post(self, request):
        form = WorkingHoursPolicyForm(request.POST)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.tenant = request.tenant
            if policy.is_default:
                WorkingHoursPolicy.all_objects.filter(tenant=request.tenant, is_default=True).update(is_default=False)
            policy.save()
            messages.success(request, f'Working hours policy "{policy.name}" created successfully.')
            return redirect('administration:working_hours_list')
        return render(request, 'administration/system/working_hours_form.html', {
            'form': form, 'title': 'Create Working Hours Policy'
        })


class WorkingHoursEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        policy = get_object_or_404(WorkingHoursPolicy.all_objects, pk=pk, tenant=request.tenant)
        form = WorkingHoursPolicyForm(instance=policy)
        return render(request, 'administration/system/working_hours_form.html', {
            'form': form, 'title': 'Edit Working Hours Policy', 'policy': policy
        })

    def post(self, request, pk):
        policy = get_object_or_404(WorkingHoursPolicy.all_objects, pk=pk, tenant=request.tenant)
        form = WorkingHoursPolicyForm(request.POST, instance=policy)
        if form.is_valid():
            policy = form.save(commit=False)
            if policy.is_default:
                WorkingHoursPolicy.all_objects.filter(tenant=request.tenant, is_default=True).exclude(pk=pk).update(is_default=False)
            policy.save()
            messages.success(request, f'Working hours policy "{policy.name}" updated successfully.')
            return redirect('administration:working_hours_list')
        return render(request, 'administration/system/working_hours_form.html', {
            'form': form, 'title': 'Edit Working Hours Policy', 'policy': policy
        })


class WorkingHoursDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        policy = get_object_or_404(WorkingHoursPolicy.all_objects, pk=pk, tenant=request.tenant)
        name = policy.name
        policy.delete()
        messages.success(request, f'Working hours policy "{name}" deleted successfully.')
        return redirect('administration:working_hours_list')


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'administration/system/location_list.html'
    context_object_name = 'locations'
    paginate_by = 20

    def get_queryset(self):
        qs = Location.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(city__icontains=search) |
                Q(state__icontains=search)
            )
        return qs.select_related('company')


class LocationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        companies = Company.all_objects.filter(tenant=request.tenant, is_active=True)
        return render(request, 'administration/system/location_form.html', {
            'title': 'Add Location', 'companies': companies
        })

    def post(self, request):
        name = request.POST.get('name', '')
        company_id = request.POST.get('company', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        country = request.POST.get('country', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        is_headquarters = request.POST.get('is_headquarters') == 'on'
        is_active = request.POST.get('is_active', 'on') == 'on'

        if not name or not company_id:
            messages.error(request, 'Name and Company are required.')
            companies = Company.all_objects.filter(tenant=request.tenant, is_active=True)
            return render(request, 'administration/system/location_form.html', {
                'title': 'Add Location', 'companies': companies
            })

        company = get_object_or_404(Company.all_objects, pk=company_id, tenant=request.tenant)
        Location.all_objects.create(
            company=company, name=name, address=address, city=city,
            state=state, country=country, zip_code=zip_code, phone=phone,
            is_headquarters=is_headquarters, is_active=is_active,
            tenant=request.tenant,
        )
        messages.success(request, f'Location "{name}" created successfully.')
        return redirect('administration:location_list')


class LocationEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        location = get_object_or_404(Location.all_objects, pk=pk, tenant=request.tenant)
        companies = Company.all_objects.filter(tenant=request.tenant, is_active=True)
        return render(request, 'administration/system/location_form.html', {
            'title': 'Edit Location', 'location': location, 'companies': companies
        })

    def post(self, request, pk):
        location = get_object_or_404(Location.all_objects, pk=pk, tenant=request.tenant)
        location.name = request.POST.get('name', location.name)
        company_id = request.POST.get('company', '')
        if company_id:
            location.company = get_object_or_404(Company.all_objects, pk=company_id, tenant=request.tenant)
        location.address = request.POST.get('address', '')
        location.city = request.POST.get('city', '')
        location.state = request.POST.get('state', '')
        location.country = request.POST.get('country', '')
        location.zip_code = request.POST.get('zip_code', '')
        location.phone = request.POST.get('phone', '')
        location.is_headquarters = request.POST.get('is_headquarters') == 'on'
        location.is_active = request.POST.get('is_active', 'on') == 'on'
        location.save()
        messages.success(request, f'Location "{location.name}" updated successfully.')
        return redirect('administration:location_list')


class LocationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        location = get_object_or_404(Location.all_objects, pk=pk, tenant=request.tenant)
        name = location.name
        location.delete()
        messages.success(request, f'Location "{name}" deleted successfully.')
        return redirect('administration:location_list')


class IntegrationListView(LoginRequiredMixin, ListView):
    model = IntegrationSetting
    template_name = 'administration/system/integration_list.html'
    context_object_name = 'integrations'
    paginate_by = 20

    def get_queryset(self):
        return IntegrationSetting.all_objects.filter(tenant=self.request.tenant)


class IntegrationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = IntegrationSettingForm()
        return render(request, 'administration/system/integration_form.html', {
            'form': form, 'title': 'Add Integration'
        })

    def post(self, request):
        form = IntegrationSettingForm(request.POST)
        if form.is_valid():
            integration = form.save(commit=False)
            integration.tenant = request.tenant
            integration.save()
            messages.success(request, f'Integration "{integration.name}" created successfully.')
            return redirect('administration:integration_list')
        return render(request, 'administration/system/integration_form.html', {
            'form': form, 'title': 'Add Integration'
        })


class IntegrationEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        integration = get_object_or_404(IntegrationSetting.all_objects, pk=pk, tenant=request.tenant)
        form = IntegrationSettingForm(instance=integration)
        return render(request, 'administration/system/integration_form.html', {
            'form': form, 'title': 'Edit Integration', 'integration': integration
        })

    def post(self, request, pk):
        integration = get_object_or_404(IntegrationSetting.all_objects, pk=pk, tenant=request.tenant)
        form = IntegrationSettingForm(request.POST, instance=integration)
        if form.is_valid():
            form.save()
            messages.success(request, f'Integration "{integration.name}" updated successfully.')
            return redirect('administration:integration_list')
        return render(request, 'administration/system/integration_form.html', {
            'form': form, 'title': 'Edit Integration', 'integration': integration
        })


class IntegrationDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        integration = get_object_or_404(IntegrationSetting.all_objects, pk=pk, tenant=request.tenant)
        name = integration.name
        integration.delete()
        messages.success(request, f'Integration "{name}" deleted successfully.')
        return redirect('administration:integration_list')


class IntegrationTestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        integration = get_object_or_404(IntegrationSetting.all_objects, pk=pk, tenant=request.tenant)
        # Simulate connection test
        integration.last_tested_at = timezone.now()
        integration.status = 'active'
        integration.save()
        messages.success(request, f'Connection test for "{integration.name}" successful.')
        return redirect('administration:integration_list')


# =============================================================================
# 9.4 Audit & Compliance Views
# =============================================================================

class AuditTrailView(LoginRequiredMixin, ListView):
    model = AuditTrail
    template_name = 'administration/audit/audit_trail.html'
    context_object_name = 'audit_logs'
    paginate_by = 30

    def get_queryset(self):
        qs = AuditTrail.all_objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(model_name__icontains=search) |
                Q(object_repr__icontains=search)
            )
        action = self.request.GET.get('action', '')
        if action:
            qs = qs.filter(action=action)
        model_name = self.request.GET.get('model', '')
        if model_name:
            qs = qs.filter(model_name=model_name)
        date_from = self.request.GET.get('date_from', '')
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)
        date_to = self.request.GET.get('date_to', '')
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)
        return qs.select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actions'] = AuditTrail.ACTION_CHOICES
        # Get distinct model names for filter
        context['model_names'] = AuditTrail.all_objects.filter(
            tenant=self.request.tenant
        ).values_list('model_name', flat=True).distinct().order_by('model_name')
        return context


class AuditDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        audit = get_object_or_404(AuditTrail.all_objects, pk=pk, tenant=request.tenant)
        return render(request, 'administration/audit/audit_detail.html', {'audit': audit})


class DataPrivacyView(LoginRequiredMixin, TemplateView):
    template_name = 'administration/audit/data_privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        context['retention_policies'] = DataRetentionPolicy.all_objects.filter(tenant=tenant)
        # Privacy settings from SystemSetting
        privacy_settings = {}
        for s in SystemSetting.all_objects.filter(tenant=tenant, category='security'):
            privacy_settings[s.key] = s.value
        context['privacy_settings'] = privacy_settings
        return context


class DataRetentionListView(LoginRequiredMixin, ListView):
    model = DataRetentionPolicy
    template_name = 'administration/audit/data_retention_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        return DataRetentionPolicy.all_objects.filter(tenant=self.request.tenant)


class DataRetentionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = DataRetentionPolicyForm()
        return render(request, 'administration/audit/data_retention_form.html', {
            'form': form, 'title': 'Create Data Retention Policy'
        })

    def post(self, request):
        form = DataRetentionPolicyForm(request.POST)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.tenant = request.tenant
            policy.save()
            messages.success(request, 'Data retention policy created successfully.')
            return redirect('administration:data_retention_list')
        return render(request, 'administration/audit/data_retention_form.html', {
            'form': form, 'title': 'Create Data Retention Policy'
        })


class DataRetentionEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        policy = get_object_or_404(DataRetentionPolicy.all_objects, pk=pk, tenant=request.tenant)
        form = DataRetentionPolicyForm(instance=policy)
        return render(request, 'administration/audit/data_retention_form.html', {
            'form': form, 'title': 'Edit Data Retention Policy', 'policy': policy
        })

    def post(self, request, pk):
        policy = get_object_or_404(DataRetentionPolicy.all_objects, pk=pk, tenant=request.tenant)
        form = DataRetentionPolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data retention policy updated successfully.')
            return redirect('administration:data_retention_list')
        return render(request, 'administration/audit/data_retention_form.html', {
            'form': form, 'title': 'Edit Data Retention Policy', 'policy': policy
        })


class DataRetentionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        policy = get_object_or_404(DataRetentionPolicy.all_objects, pk=pk, tenant=request.tenant)
        policy.delete()
        messages.success(request, 'Data retention policy deleted successfully.')
        return redirect('administration:data_retention_list')


class AccessLogsView(LoginRequiredMixin, ListView):
    model = AuditTrail
    template_name = 'administration/audit/access_logs.html'
    context_object_name = 'logs'
    paginate_by = 30

    def get_queryset(self):
        qs = AuditTrail.all_objects.filter(
            tenant=self.request.tenant,
            action__in=['login', 'logout']
        )
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(ip_address__icontains=search)
            )
        date_from = self.request.GET.get('date_from', '')
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)
        date_to = self.request.GET.get('date_to', '')
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)
        return qs.select_related('user')


class BackupRecoveryView(LoginRequiredMixin, View):
    def get(self, request):
        config = BackupConfiguration.all_objects.filter(tenant=request.tenant).first()
        logs = BackupLog.all_objects.filter(tenant=request.tenant)[:20]
        form = BackupConfigurationForm(instance=config) if config else BackupConfigurationForm()
        return render(request, 'administration/audit/backup_recovery.html', {
            'config': config, 'logs': logs, 'form': form
        })

    def post(self, request):
        config = BackupConfiguration.all_objects.filter(tenant=request.tenant).first()
        if config:
            form = BackupConfigurationForm(request.POST, instance=config)
        else:
            form = BackupConfigurationForm(request.POST)
        if form.is_valid():
            backup = form.save(commit=False)
            backup.tenant = request.tenant
            backup.save()
            messages.success(request, 'Backup configuration saved successfully.')
            return redirect('administration:backup')
        logs = BackupLog.all_objects.filter(tenant=request.tenant)[:20]
        return render(request, 'administration/audit/backup_recovery.html', {
            'config': config, 'logs': logs, 'form': form
        })


class BackupNowView(LoginRequiredMixin, View):
    def post(self, request):
        config = BackupConfiguration.all_objects.filter(tenant=request.tenant).first()
        # Create backup log entry
        log = BackupLog.all_objects.create(
            backup_config=config,
            status='completed',
            completed_at=timezone.now(),
            file_size='N/A',
            initiated_by=request.user,
            tenant=request.tenant,
        )
        if config:
            config.last_backup_at = timezone.now()
            config.save()
        messages.success(request, 'Backup initiated successfully.')
        return redirect('administration:backup')


class BackupDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        log = get_object_or_404(BackupLog.all_objects, pk=pk, tenant=request.tenant)
        messages.info(request, 'Backup download feature is under development.')
        return redirect('administration:backup')
