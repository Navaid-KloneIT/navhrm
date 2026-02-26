from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.employees.models import Employee, EmergencyContact, EmployeeDocument
from apps.attendance.models import LeaveApplication, LeaveType, AttendanceRegularization

from .models import (
    FamilyMember, DocumentRequest, IDCardRequest, AssetRequest,
    Announcement, BirthdayWish, Survey, SurveyQuestion, SurveyResponse,
    Suggestion, HelpDeskTicket, TicketComment,
)
from .forms import (
    PersonalInfoForm, ContactInfoForm, BankDetailsForm, AvatarForm,
    EmergencyContactForm, FamilyMemberForm,
    EssLeaveApplicationForm, EssRegularizationForm,
    DocumentRequestForm, IDCardRequestForm, AssetRequestForm,
    BirthdayWishForm, SuggestionForm, TicketForm, TicketCommentForm,
)


# ===========================================================================
# Mixin: ensures logged-in user has an employee record
# ===========================================================================

class EmployeeSelfServiceMixin(LoginRequiredMixin):
    """Ensures the logged-in user has a linked Employee profile."""

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employee') or request.user.employee is None:
            messages.error(request, 'No employee profile linked to your account.')
            return redirect('dashboard')
        self.employee = request.user.employee
        return super().dispatch(request, *args, **kwargs)


# ===========================================================================
# Dashboard
# ===========================================================================

class EssDashboardView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        employee = self.employee
        today = date.today()

        pending_leaves = LeaveApplication.objects.filter(
            tenant=request.tenant, employee=employee, status='pending').count()
        pending_regularizations = AttendanceRegularization.objects.filter(
            tenant=request.tenant, employee=employee, status='pending').count()
        pending_doc_requests = DocumentRequest.objects.filter(
            tenant=request.tenant, employee=employee, status='pending').count()
        pending_asset_requests = AssetRequest.objects.filter(
            tenant=request.tenant, employee=employee, status='pending').count()
        pending_idcard_requests = IDCardRequest.objects.filter(
            tenant=request.tenant, employee=employee, status='pending').count()
        open_tickets = HelpDeskTicket.objects.filter(
            tenant=request.tenant, employee=employee,
            status__in=['open', 'in_progress', 'waiting_on_employee']).count()

        recent_announcements = Announcement.objects.filter(
            tenant=request.tenant, is_active=True,
            publish_date__lte=timezone.now()
        ).filter(
            Q(target_departments__isnull=True) |
            Q(target_departments=employee.department)
        ).distinct()[:5]

        # Birthdays this month
        birthdays = Employee.objects.filter(
            tenant=request.tenant, status='active',
            date_of_birth__month=today.month
        ).order_by('date_of_birth__day')[:10]

        # Work anniversaries this month
        anniversaries = Employee.objects.filter(
            tenant=request.tenant, status='active',
            date_of_joining__month=today.month
        ).exclude(date_of_joining__year=today.year).order_by('date_of_joining__day')[:10]

        active_surveys = Survey.objects.filter(
            tenant=request.tenant, status='active',
            start_date__lte=today, end_date__gte=today
        ).filter(
            Q(target_departments__isnull=True) |
            Q(target_departments=employee.department)
        ).distinct().count()

        return render(request, 'ess/dashboard.html', {
            'employee': employee,
            'pending_leaves': pending_leaves,
            'pending_regularizations': pending_regularizations,
            'pending_doc_requests': pending_doc_requests,
            'pending_asset_requests': pending_asset_requests,
            'pending_idcard_requests': pending_idcard_requests,
            'open_tickets': open_tickets,
            'recent_announcements': recent_announcements,
            'birthdays': birthdays,
            'anniversaries': anniversaries,
            'active_surveys': active_surveys,
        })


# ===========================================================================
# 7.1 Personal Information — Profile
# ===========================================================================

class MyProfileView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        employee = self.employee
        emergency_contacts = EmergencyContact.objects.filter(
            tenant=request.tenant, employee=employee)
        family_members = FamilyMember.objects.filter(
            tenant=request.tenant, employee=employee)
        documents = EmployeeDocument.objects.filter(
            tenant=request.tenant, employee=employee)
        return render(request, 'ess/profile.html', {
            'employee': employee,
            'emergency_contacts': emergency_contacts,
            'family_members': family_members,
            'documents': documents,
        })


class ProfilePersonalEditView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = PersonalInfoForm(instance=self.employee)
        return render(request, 'ess/profile_personal_form.html', {
            'form': form, 'title': 'Edit Personal Details'})

    def post(self, request):
        form = PersonalInfoForm(request.POST, instance=self.employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal details updated successfully.')
            return redirect('ess:profile')
        return render(request, 'ess/profile_personal_form.html', {
            'form': form, 'title': 'Edit Personal Details'})


class ProfileContactEditView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = ContactInfoForm(instance=self.employee)
        return render(request, 'ess/profile_contact_form.html', {
            'form': form, 'title': 'Edit Contact Details'})

    def post(self, request):
        form = ContactInfoForm(request.POST, instance=self.employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact details updated successfully.')
            return redirect('ess:profile')
        return render(request, 'ess/profile_contact_form.html', {
            'form': form, 'title': 'Edit Contact Details'})


class ProfileBankEditView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = BankDetailsForm(instance=self.employee)
        return render(request, 'ess/profile_bank_form.html', {
            'form': form, 'title': 'Edit Bank Details'})

    def post(self, request):
        form = BankDetailsForm(request.POST, instance=self.employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank details updated successfully.')
            return redirect('ess:profile')
        return render(request, 'ess/profile_bank_form.html', {
            'form': form, 'title': 'Edit Bank Details'})


class ProfileAvatarEditView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = AvatarForm(instance=self.employee)
        return render(request, 'ess/profile_avatar_form.html', {
            'form': form, 'title': 'Update Avatar'})

    def post(self, request):
        form = AvatarForm(request.POST, request.FILES, instance=self.employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avatar updated successfully.')
            return redirect('ess:profile')
        return render(request, 'ess/profile_avatar_form.html', {
            'form': form, 'title': 'Update Avatar'})


# ===========================================================================
# 7.1 Emergency Contacts
# ===========================================================================

class EmergencyContactListView(EmployeeSelfServiceMixin, ListView):
    model = EmergencyContact
    template_name = 'ess/emergency_contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        qs = EmergencyContact.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        search = self.request.GET.get('search', '').strip()
        relationship = self.request.GET.get('relationship', '')
        primary = self.request.GET.get('primary', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search))
        if relationship:
            qs = qs.filter(relationship=relationship)
        if primary == 'yes':
            qs = qs.filter(is_primary=True)
        elif primary == 'no':
            qs = qs.filter(is_primary=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['relationship_choices'] = EmergencyContact.RELATIONSHIP_CHOICES
        return ctx


class EmergencyContactCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = EmergencyContactForm()
        return render(request, 'ess/emergency_contact_form.html', {
            'form': form, 'title': 'Add Emergency Contact'})

    def post(self, request):
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.employee = self.employee
            contact.tenant = request.tenant
            contact.save()
            messages.success(request, 'Emergency contact added successfully.')
            return redirect('ess:emergency_contact_list')
        return render(request, 'ess/emergency_contact_form.html', {
            'form': form, 'title': 'Add Emergency Contact'})


class EmergencyContactEditView(EmployeeSelfServiceMixin, View):
    def get(self, request, pk):
        contact = get_object_or_404(
            EmergencyContact, pk=pk, tenant=request.tenant, employee=self.employee)
        form = EmergencyContactForm(instance=contact)
        return render(request, 'ess/emergency_contact_form.html', {
            'form': form, 'title': 'Edit Emergency Contact'})

    def post(self, request, pk):
        contact = get_object_or_404(
            EmergencyContact, pk=pk, tenant=request.tenant, employee=self.employee)
        form = EmergencyContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency contact updated successfully.')
            return redirect('ess:emergency_contact_list')
        return render(request, 'ess/emergency_contact_form.html', {
            'form': form, 'title': 'Edit Emergency Contact'})


class EmergencyContactDeleteView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        contact = get_object_or_404(
            EmergencyContact, pk=pk, tenant=request.tenant, employee=self.employee)
        contact.delete()
        messages.success(request, 'Emergency contact deleted successfully.')
        return redirect('ess:emergency_contact_list')


# ===========================================================================
# 7.1 Family Members
# ===========================================================================

class FamilyMemberListView(EmployeeSelfServiceMixin, ListView):
    model = FamilyMember
    template_name = 'ess/family_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        qs = FamilyMember.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        search = self.request.GET.get('search', '').strip()
        relationship = self.request.GET.get('relationship', '')
        dependent = self.request.GET.get('dependent', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(occupation__icontains=search))
        if relationship:
            qs = qs.filter(relationship=relationship)
        if dependent == 'yes':
            qs = qs.filter(is_dependent=True)
        elif dependent == 'no':
            qs = qs.filter(is_dependent=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['relationship_choices'] = FamilyMember.RELATIONSHIP_CHOICES
        return ctx


class FamilyMemberCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = FamilyMemberForm()
        return render(request, 'ess/family_form.html', {
            'form': form, 'title': 'Add Family Member'})

    def post(self, request):
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.employee = self.employee
            member.tenant = request.tenant
            member.save()
            messages.success(request, 'Family member added successfully.')
            return redirect('ess:family_list')
        return render(request, 'ess/family_form.html', {
            'form': form, 'title': 'Add Family Member'})


class FamilyMemberEditView(EmployeeSelfServiceMixin, View):
    def get(self, request, pk):
        member = get_object_or_404(
            FamilyMember, pk=pk, tenant=request.tenant, employee=self.employee)
        form = FamilyMemberForm(instance=member)
        return render(request, 'ess/family_form.html', {
            'form': form, 'title': 'Edit Family Member'})

    def post(self, request, pk):
        member = get_object_or_404(
            FamilyMember, pk=pk, tenant=request.tenant, employee=self.employee)
        form = FamilyMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Family member updated successfully.')
            return redirect('ess:family_list')
        return render(request, 'ess/family_form.html', {
            'form': form, 'title': 'Edit Family Member'})


class FamilyMemberDeleteView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(
            FamilyMember, pk=pk, tenant=request.tenant, employee=self.employee)
        member.delete()
        messages.success(request, 'Family member deleted successfully.')
        return redirect('ess:family_list')


# ===========================================================================
# 7.1 My Documents (read-only)
# ===========================================================================

class MyDocumentsView(EmployeeSelfServiceMixin, ListView):
    model = EmployeeDocument
    template_name = 'ess/my_documents.html'
    context_object_name = 'documents'

    def get_queryset(self):
        qs = EmployeeDocument.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        search = self.request.GET.get('search', '').strip()
        doc_type = self.request.GET.get('type', '')
        status = self.request.GET.get('status', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(document_number__icontains=search))
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        if status == 'verified':
            qs = qs.filter(is_verified=True)
        elif status == 'pending':
            qs = qs.filter(is_verified=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['document_type_choices'] = EmployeeDocument.DOCUMENT_TYPES
        return ctx


# ===========================================================================
# 7.2 Leave Requests (self-service wrapper for attendance.LeaveApplication)
# ===========================================================================

class MyLeaveListView(EmployeeSelfServiceMixin, ListView):
    model = LeaveApplication
    template_name = 'ess/leave_list.html'
    context_object_name = 'leaves'
    paginate_by = 20

    def get_queryset(self):
        qs = LeaveApplication.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '')
        leave_type = self.request.GET.get('leave_type', '')
        if search:
            qs = qs.filter(Q(reason__icontains=search) | Q(leave_type__name__icontains=search))
        if status:
            qs = qs.filter(status=status)
        if leave_type:
            qs = qs.filter(leave_type_id=leave_type)
        return qs.select_related('leave_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = LeaveApplication.STATUS_CHOICES
        context['leave_types'] = LeaveType.objects.filter(tenant=self.request.tenant, is_active=True)
        return context


class MyLeaveApplyView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = EssLeaveApplicationForm(tenant=request.tenant)
        return render(request, 'ess/leave_form.html', {
            'form': form, 'title': 'Apply for Leave'})

    def post(self, request):
        form = EssLeaveApplicationForm(request.POST, request.FILES, tenant=request.tenant)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = self.employee
            leave.tenant = request.tenant
            leave.status = 'pending'
            leave.save()
            messages.success(request, 'Leave application submitted successfully.')
            return redirect('ess:leave_list')
        return render(request, 'ess/leave_form.html', {
            'form': form, 'title': 'Apply for Leave'})


class MyLeaveDetailView(EmployeeSelfServiceMixin, DetailView):
    model = LeaveApplication
    template_name = 'ess/leave_detail.html'
    context_object_name = 'leave'

    def get_queryset(self):
        return LeaveApplication.objects.filter(
            tenant=self.request.tenant, employee=self.employee
        ).select_related('leave_type', 'approved_by')


class MyLeaveCancelView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        leave = get_object_or_404(
            LeaveApplication, pk=pk, tenant=request.tenant, employee=self.employee)
        if leave.status in ('pending', 'approved'):
            leave.status = 'cancelled'
            leave.cancellation_reason = request.POST.get('cancellation_reason', '')
            leave.cancelled_at = timezone.now()
            leave.save()
            messages.success(request, 'Leave application cancelled successfully.')
        else:
            messages.error(request, 'This leave application cannot be cancelled.')
        return redirect('ess:leave_detail', pk=pk)


# ===========================================================================
# 7.2 Attendance Regularization
# ===========================================================================

class MyRegularizationListView(EmployeeSelfServiceMixin, ListView):
    model = AttendanceRegularization
    template_name = 'ess/regularization_list.html'
    context_object_name = 'regularizations'
    paginate_by = 20

    def get_queryset(self):
        qs = AttendanceRegularization.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '')
        reason = self.request.GET.get('reason', '')
        if search:
            qs = qs.filter(Q(reason_detail__icontains=search))
        if status:
            qs = qs.filter(status=status)
        if reason:
            qs = qs.filter(reason=reason)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = AttendanceRegularization.STATUS_CHOICES
        context['reason_choices'] = AttendanceRegularization.REASON_CHOICES
        return context


class MyRegularizationCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = EssRegularizationForm()
        return render(request, 'ess/regularization_form.html', {
            'form': form, 'title': 'Request Attendance Regularization'})

    def post(self, request):
        form = EssRegularizationForm(request.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.employee = self.employee
            reg.tenant = request.tenant
            reg.save()
            messages.success(request, 'Regularization request submitted successfully.')
            return redirect('ess:regularization_list')
        return render(request, 'ess/regularization_form.html', {
            'form': form, 'title': 'Request Attendance Regularization'})


class MyRegularizationDetailView(EmployeeSelfServiceMixin, DetailView):
    model = AttendanceRegularization
    template_name = 'ess/regularization_detail.html'
    context_object_name = 'regularization'

    def get_queryset(self):
        return AttendanceRegularization.objects.filter(
            tenant=self.request.tenant, employee=self.employee)


# ===========================================================================
# 7.2 Document Requests
# ===========================================================================

class DocumentRequestListView(EmployeeSelfServiceMixin, ListView):
    model = DocumentRequest
    template_name = 'ess/document_request_list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        qs = DocumentRequest.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '')
        doc_type = self.request.GET.get('type', '')
        if search:
            qs = qs.filter(Q(purpose__icontains=search) | Q(additional_notes__icontains=search))
        if status:
            qs = qs.filter(status=status)
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = DocumentRequest.STATUS_CHOICES
        context['document_type_choices'] = DocumentRequest.DOCUMENT_TYPE_CHOICES
        return context


class DocumentRequestCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = DocumentRequestForm()
        return render(request, 'ess/document_request_form.html', {
            'form': form, 'title': 'Request Document'})

    def post(self, request):
        form = DocumentRequestForm(request.POST)
        if form.is_valid():
            doc_req = form.save(commit=False)
            doc_req.employee = self.employee
            doc_req.tenant = request.tenant
            doc_req.save()
            messages.success(request, 'Document request submitted successfully.')
            return redirect('ess:document_request_list')
        return render(request, 'ess/document_request_form.html', {
            'form': form, 'title': 'Request Document'})


class DocumentRequestDetailView(EmployeeSelfServiceMixin, DetailView):
    model = DocumentRequest
    template_name = 'ess/document_request_detail.html'
    context_object_name = 'doc_request'

    def get_queryset(self):
        return DocumentRequest.objects.filter(
            tenant=self.request.tenant, employee=self.employee)


class DocumentRequestCancelView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        doc_req = get_object_or_404(
            DocumentRequest, pk=pk, tenant=request.tenant, employee=self.employee)
        if doc_req.status == 'pending':
            doc_req.status = 'cancelled'
            doc_req.save()
            messages.success(request, 'Document request cancelled.')
        else:
            messages.error(request, 'This request cannot be cancelled.')
        return redirect('ess:document_request_detail', pk=pk)


# ===========================================================================
# 7.2 ID Card Requests
# ===========================================================================

class IDCardRequestListView(EmployeeSelfServiceMixin, ListView):
    model = IDCardRequest
    template_name = 'ess/idcard_request_list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        qs = IDCardRequest.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        status = self.request.GET.get('status', '')
        request_type = self.request.GET.get('type', '')
        if status:
            qs = qs.filter(status=status)
        if request_type:
            qs = qs.filter(request_type=request_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = IDCardRequest.STATUS_CHOICES
        context['request_type_choices'] = IDCardRequest.REQUEST_TYPE_CHOICES
        return context


class IDCardRequestCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = IDCardRequestForm()
        return render(request, 'ess/idcard_request_form.html', {
            'form': form, 'title': 'Request ID Card'})

    def post(self, request):
        form = IDCardRequestForm(request.POST, request.FILES)
        if form.is_valid():
            idcard = form.save(commit=False)
            idcard.employee = self.employee
            idcard.tenant = request.tenant
            idcard.save()
            messages.success(request, 'ID card request submitted successfully.')
            return redirect('ess:idcard_request_list')
        return render(request, 'ess/idcard_request_form.html', {
            'form': form, 'title': 'Request ID Card'})


class IDCardRequestDetailView(EmployeeSelfServiceMixin, DetailView):
    model = IDCardRequest
    template_name = 'ess/idcard_request_detail.html'
    context_object_name = 'idcard_request'

    def get_queryset(self):
        return IDCardRequest.objects.filter(
            tenant=self.request.tenant, employee=self.employee)


# ===========================================================================
# 7.2 Asset Requests
# ===========================================================================

class AssetRequestListView(EmployeeSelfServiceMixin, ListView):
    model = AssetRequest
    template_name = 'ess/asset_request_list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        qs = AssetRequest.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '')
        asset_type = self.request.GET.get('type', '')
        priority = self.request.GET.get('priority', '')
        if search:
            qs = qs.filter(Q(asset_name__icontains=search) | Q(reason__icontains=search))
        if status:
            qs = qs.filter(status=status)
        if asset_type:
            qs = qs.filter(asset_type=asset_type)
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = AssetRequest.STATUS_CHOICES
        context['asset_type_choices'] = AssetRequest.ASSET_TYPE_CHOICES
        context['priority_choices'] = AssetRequest.PRIORITY_CHOICES
        return context


class AssetRequestCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = AssetRequestForm()
        return render(request, 'ess/asset_request_form.html', {
            'form': form, 'title': 'Request Asset'})

    def post(self, request):
        form = AssetRequestForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.employee = self.employee
            asset.tenant = request.tenant
            asset.save()
            messages.success(request, 'Asset request submitted successfully.')
            return redirect('ess:asset_request_list')
        return render(request, 'ess/asset_request_form.html', {
            'form': form, 'title': 'Request Asset'})


class AssetRequestDetailView(EmployeeSelfServiceMixin, DetailView):
    model = AssetRequest
    template_name = 'ess/asset_request_detail.html'
    context_object_name = 'asset_request'

    def get_queryset(self):
        return AssetRequest.objects.filter(
            tenant=self.request.tenant, employee=self.employee)


class AssetRequestCancelView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(
            AssetRequest, pk=pk, tenant=request.tenant, employee=self.employee)
        if asset.status == 'pending':
            asset.status = 'cancelled'
            asset.save()
            messages.success(request, 'Asset request cancelled.')
        else:
            messages.error(request, 'This request cannot be cancelled.')
        return redirect('ess:asset_request_detail', pk=pk)


# ===========================================================================
# 7.3 Announcements
# ===========================================================================

class AnnouncementListView(EmployeeSelfServiceMixin, ListView):
    model = Announcement
    template_name = 'ess/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        return Announcement.objects.filter(
            tenant=self.request.tenant, is_active=True,
            publish_date__lte=timezone.now()
        ).filter(
            Q(target_departments__isnull=True) |
            Q(target_departments=self.employee.department)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = Announcement.CATEGORY_CHOICES
        return context


class AnnouncementDetailView(EmployeeSelfServiceMixin, DetailView):
    model = Announcement
    template_name = 'ess/announcement_detail.html'
    context_object_name = 'announcement'

    def get_queryset(self):
        return Announcement.objects.filter(
            tenant=self.request.tenant, is_active=True)


# ===========================================================================
# 7.3 Celebrations (Birthday / Work Anniversary)
# ===========================================================================

class CelebrationListView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        today = date.today()
        month = int(request.GET.get('month', today.month))

        birthdays = Employee.objects.filter(
            tenant=request.tenant, status='active',
            date_of_birth__month=month
        ).exclude(date_of_birth__isnull=True).order_by('date_of_birth__day')

        anniversaries = Employee.objects.filter(
            tenant=request.tenant, status='active',
            date_of_joining__month=month
        ).exclude(date_of_joining__year=today.year).order_by('date_of_joining__day')

        # Get wishes sent by current user this month
        sent_wishes = BirthdayWish.objects.filter(
            tenant=request.tenant, wished_by=self.employee,
            occasion_date__month=month, occasion_date__year=today.year
        ).values_list('employee_id', 'occasion')
        sent_wish_set = set((eid, occ) for eid, occ in sent_wishes)

        return render(request, 'ess/celebration_list.html', {
            'birthdays': birthdays,
            'anniversaries': anniversaries,
            'current_month': month,
            'sent_wish_set': sent_wish_set,
            'today': today,
        })


class SendWishView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        target_employee = get_object_or_404(
            Employee, pk=pk, tenant=request.tenant)
        occasion = request.POST.get('occasion', 'birthday')
        message = request.POST.get('message', '').strip()
        if not message:
            messages.error(request, 'Please write a message.')
            return redirect('ess:celebration_list')

        today = date.today()
        BirthdayWish.objects.get_or_create(
            tenant=request.tenant,
            employee=target_employee,
            wished_by=self.employee,
            occasion=occasion,
            occasion_date=today,
            defaults={'message': message}
        )
        messages.success(request, f'Wish sent to {target_employee}!')
        return redirect('ess:celebration_list')


# ===========================================================================
# 7.3 Surveys
# ===========================================================================

class SurveyListView(EmployeeSelfServiceMixin, ListView):
    model = Survey
    template_name = 'ess/survey_list.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        today = date.today()
        return Survey.objects.filter(
            tenant=self.request.tenant, status='active',
            start_date__lte=today, end_date__gte=today
        ).filter(
            Q(target_departments__isnull=True) |
            Q(target_departments=self.employee.department)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        responded_surveys = SurveyResponse.objects.filter(
            tenant=self.request.tenant, respondent=self.employee
        ).values_list('survey_id', flat=True).distinct()
        context['responded_surveys'] = set(responded_surveys)
        return context


class SurveyDetailView(EmployeeSelfServiceMixin, DetailView):
    model = Survey
    template_name = 'ess/survey_detail.html'
    context_object_name = 'survey'

    def get_queryset(self):
        return Survey.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        has_responded = SurveyResponse.objects.filter(
            tenant=self.request.tenant,
            survey=self.object,
            respondent=self.employee
        ).exists()
        context['has_responded'] = has_responded
        return context


class SurveyRespondView(EmployeeSelfServiceMixin, View):
    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk, tenant=request.tenant, status='active')
        already_responded = SurveyResponse.objects.filter(
            tenant=request.tenant, survey=survey, respondent=self.employee).exists()
        if already_responded:
            messages.info(request, 'You have already responded to this survey.')
            return redirect('ess:survey_detail', pk=pk)
        questions = survey.questions.all()
        return render(request, 'ess/survey_respond.html', {
            'survey': survey, 'questions': questions})

    def post(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk, tenant=request.tenant, status='active')
        questions = survey.questions.all()

        for question in questions:
            answer_key = f'question_{question.pk}'
            answer = request.POST.get(answer_key, '').strip()

            if question.question_type == 'rating':
                SurveyResponse.objects.create(
                    tenant=request.tenant, survey=survey,
                    question=question, respondent=self.employee,
                    answer_rating=int(answer) if answer else None)
            else:
                if question.question_type == 'multiple_choice':
                    answer = ', '.join(request.POST.getlist(answer_key))
                SurveyResponse.objects.create(
                    tenant=request.tenant, survey=survey,
                    question=question, respondent=self.employee,
                    answer_text=answer)

        messages.success(request, 'Survey response submitted. Thank you!')
        return redirect('ess:survey_list')


# ===========================================================================
# 7.3 Suggestions
# ===========================================================================

class SuggestionListView(EmployeeSelfServiceMixin, ListView):
    model = Suggestion
    template_name = 'ess/suggestion_list.html'
    context_object_name = 'suggestions'
    paginate_by = 20

    def get_queryset(self):
        tab = self.request.GET.get('tab', 'mine')
        qs = Suggestion.objects.filter(tenant=self.request.tenant)
        if tab == 'public':
            qs = qs.filter(status__in=['accepted', 'implemented'])
        else:
            qs = qs.filter(employee=self.employee)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tab'] = self.request.GET.get('tab', 'mine')
        return context


class SuggestionCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = SuggestionForm()
        return render(request, 'ess/suggestion_form.html', {
            'form': form, 'title': 'Submit Suggestion'})

    def post(self, request):
        form = SuggestionForm(request.POST, request.FILES)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.employee = self.employee
            suggestion.tenant = request.tenant
            suggestion.save()
            messages.success(request, 'Suggestion submitted successfully.')
            return redirect('ess:suggestion_list')
        return render(request, 'ess/suggestion_form.html', {
            'form': form, 'title': 'Submit Suggestion'})


class SuggestionDetailView(EmployeeSelfServiceMixin, DetailView):
    model = Suggestion
    template_name = 'ess/suggestion_detail.html'
    context_object_name = 'suggestion'

    def get_queryset(self):
        return Suggestion.objects.filter(tenant=self.request.tenant).filter(
            Q(employee=self.employee) |
            Q(status__in=['accepted', 'implemented'])
        )


# ===========================================================================
# 7.3 Help Desk
# ===========================================================================

class TicketListView(EmployeeSelfServiceMixin, ListView):
    model = HelpDeskTicket
    template_name = 'ess/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 20

    def get_queryset(self):
        qs = HelpDeskTicket.objects.filter(
            tenant=self.request.tenant, employee=self.employee)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = HelpDeskTicket.STATUS_CHOICES
        return context


class TicketCreateView(EmployeeSelfServiceMixin, View):
    def get(self, request):
        form = TicketForm()
        return render(request, 'ess/ticket_form.html', {
            'form': form, 'title': 'Create Support Ticket'})

    def post(self, request):
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.employee = self.employee
            ticket.tenant = request.tenant
            ticket.save()
            messages.success(request, f'Ticket {ticket.ticket_number} created successfully.')
            return redirect('ess:ticket_list')
        return render(request, 'ess/ticket_form.html', {
            'form': form, 'title': 'Create Support Ticket'})


class TicketDetailView(EmployeeSelfServiceMixin, DetailView):
    model = HelpDeskTicket
    template_name = 'ess/ticket_detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        return HelpDeskTicket.objects.filter(
            tenant=self.request.tenant, employee=self.employee)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(
            is_internal=False).select_related('author')
        context['comment_form'] = TicketCommentForm()
        return context


class TicketCommentView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(
            HelpDeskTicket, pk=pk, tenant=request.tenant, employee=self.employee)
        form = TicketCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = self.employee
            comment.tenant = request.tenant
            comment.save()
            messages.success(request, 'Reply added successfully.')
        return redirect('ess:ticket_detail', pk=pk)


class TicketCloseView(EmployeeSelfServiceMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(
            HelpDeskTicket, pk=pk, tenant=request.tenant, employee=self.employee)
        if ticket.status in ('resolved', 'open', 'in_progress', 'waiting_on_employee'):
            ticket.status = 'closed'
            ticket.closed_at = timezone.now()
            ticket.save()
            messages.success(request, 'Ticket closed successfully.')
        else:
            messages.error(request, 'This ticket cannot be closed.')
        return redirect('ess:ticket_detail', pk=pk)
