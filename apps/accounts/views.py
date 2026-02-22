from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.utils import timezone
from django.db.models import Q

from apps.core.models import Tenant
from .models import User, UserProfile, UserInvite
from .forms import (
    LoginForm, RegistrationForm, UserForm, UserProfileForm,
    UserInviteForm, ForgotPasswordForm
)


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is inactive. Contact your administrator.')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'auth/login.html')


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = RegistrationForm()
        return render(request, 'auth/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create tenant
            company_name = form.cleaned_data['company_name']
            tenant = Tenant.objects.create(
                name=company_name,
                email=form.cleaned_data['email']
            )
            # Create user
            user = form.save(commit=False)
            user.tenant = tenant
            user.role = 'tenant_admin'
            user.is_tenant_admin = True
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # Create profile
            UserProfile.objects.create(user=user)
            # Login
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to NavHRM.')
            return redirect('dashboard')
        return render(request, 'auth/register.html', {'form': form})


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'auth/forgot_password.html')

    def post(self, request):
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            messages.success(request, 'Password reset link has been sent to your email.')
        else:
            messages.error(request, 'No account found with this email address.')
        return render(request, 'auth/forgot_password.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')

    def post(self, request):
        logout(request)
        return redirect('accounts:login')


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
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
        return qs


class UserCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserForm()
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Add User'})

    def post(self, request):
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.tenant = request.tenant
            user.set_password('changeme123')
            user.save()
            UserProfile.objects.create(user=user)
            messages.success(request, f'User {user.get_full_name()} created successfully.')
            return redirect('accounts:user_list')
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Add User'})


class UserEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=request.tenant)
        form = UserForm(instance=user)
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User', 'edit_user': user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=request.tenant)
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.get_full_name()} updated successfully.')
            return redirect('accounts:user_list')
        return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User', 'edit_user': user})


class UserDeactivateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=request.tenant)
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.get_full_name()} has been {status}.')
        return redirect('accounts:user_list')


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return render(request, 'accounts/profile.html', {'profile': profile})


class UserProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        return render(request, 'accounts/profile_edit.html', {
            'user_form': user_form,
            'profile_form': profile_form,
        })

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        return render(request, 'accounts/profile_edit.html', {
            'user_form': user_form,
            'profile_form': profile_form,
        })


class UserInviteListView(LoginRequiredMixin, ListView):
    model = UserInvite
    template_name = 'accounts/invite_list.html'
    context_object_name = 'invites'
    paginate_by = 20

    def get_queryset(self):
        return UserInvite.objects.filter(tenant=self.request.tenant)


class UserInviteSendView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserInviteForm()
        return render(request, 'accounts/invite_form.html', {'form': form})

    def post(self, request):
        form = UserInviteForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.tenant = request.tenant
            invite.invited_by = request.user
            invite.expires_at = timezone.now() + timedelta(days=7)
            invite.save()
            messages.success(request, f'Invitation sent to {invite.email}.')
            return redirect('accounts:invite_list')
        return render(request, 'accounts/invite_form.html', {'form': form})


class AcceptInviteView(View):
    def get(self, request, token):
        invite = get_object_or_404(UserInvite.all_objects, token=token, status='pending')
        if invite.expires_at < timezone.now():
            invite.status = 'expired'
            invite.save()
            messages.error(request, 'This invitation has expired.')
            return redirect('accounts:login')
        return render(request, 'auth/accept_invite.html', {'invite': invite})

    def post(self, request, token):
        invite = get_object_or_404(UserInvite.all_objects, token=token, status='pending')
        if invite.expires_at < timezone.now():
            invite.status = 'expired'
            invite.save()
            messages.error(request, 'This invitation has expired.')
            return redirect('accounts:login')

        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        user = User.objects.create_user(
            username=username,
            email=invite.email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            tenant=invite.tenant,
            role=invite.role
        )
        UserProfile.objects.create(user=user)
        invite.status = 'accepted'
        invite.accepted_at = timezone.now()
        invite.save()
        login(request, user)
        messages.success(request, 'Welcome! Your account has been created.')
        return redirect('dashboard')
