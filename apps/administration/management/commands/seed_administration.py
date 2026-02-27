import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Tenant
from apps.accounts.models import User
from apps.administration.models import (
    Role, Permission, LoginHistory,
    ApprovalWorkflow, ApprovalStep, EmailTemplate, NotificationSetting, EscalationRule,
    SystemSetting, FinancialYear, FinancialPeriod, WorkingHoursPolicy, IntegrationSetting,
    AuditTrail, DataRetentionPolicy, BackupConfiguration, BackupLog,
)


class Command(BaseCommand):
    help = 'Seed administration module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding administration data for {tenant.name}...')
            users = list(User.objects.filter(tenant=tenant))

            if len(users) < 1:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - no users found.'))
                continue

            self._seed_roles(tenant)
            self._seed_login_history(tenant, users)
            self._seed_approval_workflows(tenant, users)
            self._seed_email_templates(tenant)
            self._seed_escalation_rules(tenant)
            self._seed_system_settings(tenant)
            self._seed_financial_years(tenant)
            self._seed_working_hours(tenant)
            self._seed_integrations(tenant)
            self._seed_audit_trail(tenant, users)
            self._seed_data_retention(tenant)
            self._seed_backup(tenant, users)
            self._seed_notification_settings(tenant)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding administration data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Administration data seeding complete!'))

    def _seed_roles(self, tenant):
        if Role.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Roles already exist, skipping...')
            return

        roles_data = [
            ('Super Administrator', 'super_admin', 'Full access to all modules and settings', True),
            ('HR Manager', 'hr_manager', 'Manage HR operations, employees, payroll, and reports', True),
            ('HR Executive', 'hr_executive', 'Handle day-to-day HR tasks, leave approvals, attendance', False),
            ('Department Manager', 'dept_manager', 'Manage team members, approve leaves and timesheets', False),
            ('Finance Manager', 'finance_mgr', 'Access payroll, statutory compliance, and financial reports', False),
            ('Recruiter', 'recruiter', 'Manage job postings, candidates, interviews, and offers', False),
            ('Training Coordinator', 'training_coord', 'Manage training programs, courses, and enrollments', False),
            ('Employee', 'employee_role', 'Basic self-service access for leave, attendance, profile', True),
        ]

        modules = [code for code, _ in Permission.MODULE_CHOICES]
        actions = [code for code, _ in Permission.ACTION_CHOICES]

        # Permission templates per role
        full_access = {m: actions for m in modules}
        hr_access = {m: actions for m in ['employees', 'organization', 'attendance', 'payroll', 'performance', 'training', 'recruitment', 'reports']}
        hr_access['ess'] = ['view']
        hr_access['administration'] = ['view']
        hr_exec_access = {m: ['view', 'create', 'edit'] for m in ['employees', 'attendance', 'recruitment']}
        hr_exec_access['reports'] = ['view']
        dept_mgr_access = {'employees': ['view'], 'attendance': ['view', 'approve'], 'performance': ['view', 'create', 'edit', 'approve'], 'reports': ['view']}
        finance_access = {'payroll': actions, 'reports': ['view', 'export'], 'employees': ['view']}
        recruiter_access = {'recruitment': actions, 'employees': ['view'], 'reports': ['view']}
        training_access = {'training': actions, 'employees': ['view'], 'reports': ['view']}
        employee_access = {'ess': ['view', 'create', 'edit'], 'attendance': ['view'], 'performance': ['view']}

        perm_map = {
            'super_admin': full_access,
            'hr_manager': hr_access,
            'hr_executive': hr_exec_access,
            'dept_manager': dept_mgr_access,
            'finance_mgr': finance_access,
            'recruiter': recruiter_access,
            'training_coord': training_access,
            'employee_role': employee_access,
        }

        for name, code, desc, is_system in roles_data:
            role = Role.all_objects.create(
                name=name, code=code, description=desc,
                is_system_role=is_system, tenant=tenant,
            )
            role_perms = perm_map.get(code, {})
            for module in modules:
                for action in actions:
                    is_granted = action in role_perms.get(module, [])
                    Permission.all_objects.create(
                        role=role, module=module, action=action,
                        is_granted=is_granted, tenant=tenant,
                    )
        self.stdout.write('  Created 8 roles with permissions')

    def _seed_login_history(self, tenant, users):
        if LoginHistory.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Login history already exists, skipping...')
            return

        ips = ['192.168.1.10', '192.168.1.25', '10.0.0.5', '172.16.0.100',
               '192.168.0.50', '10.10.10.15', '203.0.113.42', '198.51.100.7']
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/17.2',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15',
        ]
        statuses = ['success', 'success', 'success', 'success', 'success',
                    'success', 'success', 'failed', 'failed', 'locked']
        failure_reasons = ['', '', '', '', '', '', '', 'Invalid password', 'Invalid password', 'Account locked after 5 attempts']

        now = timezone.now()
        for i in range(50):
            user = random.choice(users)
            status_idx = random.randint(0, len(statuses) - 1)
            login_time = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            logout_time = login_time + timedelta(hours=random.randint(1, 9)) if statuses[status_idx] == 'success' else None

            LoginHistory.all_objects.create(
                user=user,
                ip_address=random.choice(ips),
                user_agent=random.choice(agents),
                status=statuses[status_idx],
                failure_reason=failure_reasons[status_idx],
                logout_at=logout_time,
                tenant=tenant,
            )
        self.stdout.write('  Created 50 login history records')

    def _seed_approval_workflows(self, tenant, users):
        if ApprovalWorkflow.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Approval workflows already exist, skipping...')
            return

        workflows_data = [
            ('Leave Approval Workflow', 'leave', 'Standard leave approval process', [
                (1, 'Manager Approval', 'reporting_manager', False, 0),
                (2, 'HR Review', 'hr_manager', True, 3),
            ]),
            ('Attendance Regularization Workflow', 'attendance_regularization', 'Attendance correction approval', [
                (1, 'Manager Approval', 'reporting_manager', False, 0),
                (2, 'HR Verification', 'hr_manager', False, 2),
            ]),
            ('Expense Approval Workflow', 'expense', 'Multi-level expense approval based on amount', [
                (1, 'Manager Approval', 'reporting_manager', False, 0),
                (2, 'Department Head Approval', 'department_head', True, 0),
                (3, 'Finance Review', 'hr_manager', False, 5),
            ]),
            ('Timesheet Approval', 'timesheet', 'Weekly timesheet approval process', [
                (1, 'Project Manager Review', 'reporting_manager', False, 0),
                (2, 'HR Final Approval', 'hr_manager', True, 2),
            ]),
            ('Resignation Workflow', 'resignation', 'Employee resignation processing', [
                (1, 'Manager Acknowledgement', 'reporting_manager', False, 0),
                (2, 'HR Processing', 'hr_manager', False, 0),
                (3, 'Director Approval', 'department_head', False, 0),
            ]),
            ('Training Nomination Workflow', 'training_nomination', 'Training request and nomination approval', [
                (1, 'Manager Recommendation', 'reporting_manager', False, 0),
                (2, 'HR Approval', 'hr_manager', False, 3),
            ]),
            ('Recruitment Approval', 'recruitment', 'Job requisition and offer approval', [
                (1, 'Department Head Approval', 'department_head', False, 0),
                (2, 'HR Review', 'hr_manager', False, 0),
                (3, 'Management Final Approval', 'department_head', False, 5),
            ]),
            ('Loan Application Workflow', 'loan', 'Employee loan request approval', [
                (1, 'Manager Recommendation', 'reporting_manager', False, 0),
                (2, 'HR Review', 'hr_manager', False, 0),
                (3, 'Finance Approval', 'department_head', False, 0),
            ]),
        ]

        for wf_name, module, desc, steps in workflows_data:
            workflow = ApprovalWorkflow.all_objects.create(
                name=wf_name, module=module, description=desc,
                is_active=True, tenant=tenant,
            )
            for order, step_name, approver_type, can_skip, auto_days in steps:
                ApprovalStep.all_objects.create(
                    workflow=workflow, step_order=order, name=step_name,
                    approver_type=approver_type, can_skip=can_skip,
                    auto_approve_days=auto_days, tenant=tenant,
                )
        self.stdout.write('  Created 8 approval workflows with steps')

    def _seed_email_templates(self, tenant):
        if EmailTemplate.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Email templates already exist, skipping...')
            return

        templates_data = [
            ('Leave Application Notification', 'leave_applied', 'Leave Application - {{employee_name}}',
             '<h3>Leave Application Submitted</h3><p>Dear {{manager_name}},</p><p>{{employee_name}} has submitted a leave application.</p><p><strong>Type:</strong> {{leave_type}}</p><p><strong>From:</strong> {{from_date}}</p><p><strong>To:</strong> {{to_date}}</p><p><strong>Reason:</strong> {{reason}}</p><p>Please review and take action.</p><p>Regards,<br>{{company_name}} HR Team</p>'),
            ('Leave Approved Notification', 'leave_approved', 'Leave Approved - {{employee_name}}',
             '<h3>Leave Approved</h3><p>Dear {{employee_name}},</p><p>Your leave application has been approved by {{manager_name}}.</p><p><strong>Type:</strong> {{leave_type}}</p><p><strong>From:</strong> {{from_date}}</p><p><strong>To:</strong> {{to_date}}</p><p>Regards,<br>{{company_name}} HR Team</p>'),
            ('Leave Rejected Notification', 'leave_rejected', 'Leave Rejected - {{employee_name}}',
             '<h3>Leave Rejected</h3><p>Dear {{employee_name}},</p><p>Your leave application has been rejected by {{manager_name}}.</p><p><strong>Reason:</strong> {{rejection_reason}}</p><p>Please contact your manager for more details.</p><p>Regards,<br>{{company_name}} HR Team</p>'),
            ('New Employee Welcome', 'welcome_email', 'Welcome to {{company_name}}!',
             '<h3>Welcome Aboard!</h3><p>Dear {{employee_name}},</p><p>Welcome to {{company_name}}! We are excited to have you on our team.</p><p>Your login credentials have been sent separately. Please complete your profile setup at your earliest convenience.</p><p><strong>Start Date:</strong> {{date}}</p><p><strong>Department:</strong> {{department}}</p><p><strong>Reporting To:</strong> {{manager_name}}</p><p>Regards,<br>{{company_name}} HR Team</p>'),
            ('Salary Processed Notification', 'salary_processed', 'Salary Processed for {{date}}',
             '<h3>Salary Processed</h3><p>Dear {{employee_name}},</p><p>Your salary for the month of {{date}} has been processed and credited to your registered bank account.</p><p>You can view your payslip in the Employee Self-Service portal.</p><p>Regards,<br>{{company_name}} HR Team</p>'),
            ('Birthday Wishes', 'employee_birthday', 'Happy Birthday, {{employee_name}}!',
             '<h3>Happy Birthday! 🎂</h3><p>Dear {{employee_name}},</p><p>Wishing you a very Happy Birthday from the entire {{company_name}} family!</p><p>May this year bring you joy, success, and fulfillment.</p><p>Best Wishes,<br>{{company_name}} HR Team</p>'),
            ('Password Reset', 'password_reset', 'Password Reset Request - {{company_name}}',
             '<h3>Password Reset</h3><p>Dear {{employee_name}},</p><p>We received a request to reset your password. Click the link below to create a new password:</p><p><a href="{{reset_link}}">Reset Password</a></p><p>This link expires in 24 hours. If you did not request this, please ignore this email.</p><p>Regards,<br>{{company_name}} IT Team</p>'),
            ('Attendance Regularization', 'attendance_regularization', 'Attendance Regularization Request - {{employee_name}}',
             '<h3>Attendance Regularization</h3><p>Dear {{manager_name}},</p><p>{{employee_name}} has submitted an attendance regularization request for {{date}}.</p><p><strong>Reason:</strong> {{reason}}</p><p>Please review and take action.</p><p>Regards,<br>{{company_name}} HR Team</p>'),
            ('Exit Process Initiated', 'exit_initiated', 'Exit Process Initiated - {{employee_name}}',
             '<h3>Exit Process Initiated</h3><p>Dear HR Team,</p><p>The exit process has been initiated for {{employee_name}}.</p><p><strong>Last Working Day:</strong> {{date}}</p><p><strong>Department:</strong> {{department}}</p><p>Please ensure all clearance formalities are completed.</p><p>Regards,<br>{{company_name}} System</p>'),
            ('Expense Claim Submitted', 'expense_submitted', 'Expense Claim Submitted - {{employee_name}}',
             '<h3>Expense Claim Submitted</h3><p>Dear {{manager_name}},</p><p>{{employee_name}} has submitted an expense claim for your approval.</p><p><strong>Amount:</strong> {{amount}}</p><p><strong>Category:</strong> {{category}}</p><p>Please review and approve.</p><p>Regards,<br>{{company_name}} HR Team</p>'),
            ('New Employee Onboarding', 'new_employee', 'New Employee Joining - {{employee_name}}',
             '<h3>New Employee Joining</h3><p>Dear Team,</p><p>We are pleased to inform you that {{employee_name}} will be joining {{company_name}} as {{designation}}.</p><p><strong>Joining Date:</strong> {{date}}</p><p><strong>Department:</strong> {{department}}</p><p>Please extend a warm welcome!</p><p>Regards,<br>{{company_name}} HR Team</p>'),
        ]

        for name, event, subject, body in templates_data:
            EmailTemplate.all_objects.create(
                name=name, event=event, subject=subject, body=body,
                is_active=True, tenant=tenant,
            )
        self.stdout.write('  Created 11 email templates')

    def _seed_escalation_rules(self, tenant):
        if EscalationRule.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Escalation rules already exist, skipping...')
            return

        workflows = ApprovalWorkflow.all_objects.filter(tenant=tenant)
        users = list(User.objects.filter(tenant=tenant, role__in=['tenant_admin', 'hr_manager']))
        admin_user = users[0] if users else None

        rules_data = [
            ('remind', 2, 3),
            ('escalate_next', 5, 2),
            ('notify_admin', 7, 1),
            ('auto_approve', 10, 1),
        ]

        for workflow in workflows[:5]:
            rule_idx = random.randint(0, len(rules_data) - 1)
            action, days, max_rem = rules_data[rule_idx]
            EscalationRule.all_objects.create(
                workflow=workflow, trigger_after_days=days, action=action,
                notify_user=admin_user, max_reminders=max_rem,
                is_active=True, tenant=tenant,
            )
        self.stdout.write('  Created escalation rules')

    def _seed_system_settings(self, tenant):
        if SystemSetting.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  System settings already exist, skipping...')
            return

        settings_data = [
            ('timezone', 'Asia/Kolkata', 'general', 'string', 'Default timezone for the organization'),
            ('date_format', 'DD/MM/YYYY', 'general', 'string', 'Date display format'),
            ('currency', 'INR', 'general', 'string', 'Default currency'),
            ('fiscal_year_start', '4', 'general', 'string', 'Fiscal year start month (April)'),
            ('company_logo_url', '', 'display', 'string', 'Company logo URL'),
            ('primary_color', '#4f46e5', 'display', 'string', 'Primary brand color'),
            ('email_from_address', f'hr@{tenant.slug}.com', 'email', 'string', 'Default sender email'),
            ('email_from_name', f'{tenant.name} HR', 'email', 'string', 'Default sender name'),
            ('password_min_length', '8', 'security', 'integer', 'Minimum password length'),
            ('session_timeout_minutes', '30', 'security', 'integer', 'Session timeout in minutes'),
            ('max_login_attempts', '5', 'security', 'integer', 'Max failed login attempts before lock'),
            ('enable_email_notifications', 'true', 'notifications', 'boolean', 'Enable email notifications'),
            ('enable_birthday_notifications', 'true', 'notifications', 'boolean', 'Send birthday notifications'),
        ]

        for key, value, category, value_type, desc in settings_data:
            SystemSetting.all_objects.create(
                key=key, value=value, category=category,
                value_type=value_type, description=desc, tenant=tenant,
            )
        self.stdout.write('  Created 13 system settings')

    def _seed_financial_years(self, tenant):
        if FinancialYear.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Financial years already exist, skipping...')
            return

        fy_data = [
            ('FY 2023-24', date(2023, 4, 1), date(2024, 3, 31), False, True),
            ('FY 2024-25', date(2024, 4, 1), date(2025, 3, 31), False, False),
            ('FY 2025-26', date(2025, 4, 1), date(2026, 3, 31), True, False),
        ]

        for name, start, end, is_active, is_locked in fy_data:
            fy = FinancialYear.all_objects.create(
                name=name, start_date=start, end_date=end,
                is_active=is_active, is_locked=is_locked, tenant=tenant,
            )
            # Generate monthly periods
            current = start
            period_num = 1
            while current <= end and period_num <= 12:
                from calendar import monthrange
                month_name = current.strftime('%B %Y')
                last_day = monthrange(current.year, current.month)[1]
                period_end = date(current.year, current.month, last_day)
                if period_end > end:
                    period_end = end

                FinancialPeriod.all_objects.create(
                    financial_year=fy, name=month_name, period_number=period_num,
                    start_date=current, end_date=period_end,
                    is_locked=is_locked, tenant=tenant,
                )

                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)
                period_num += 1

        self.stdout.write('  Created 3 financial years with 36 periods')

    def _seed_working_hours(self, tenant):
        if WorkingHoursPolicy.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Working hours policies already exist, skipping...')
            return

        policies_data = [
            ('Standard Office Hours', '09:00', '18:00', 60, 8.0, 15, 15, 8.0, [0, 1, 2, 3, 4], True),
            ('Flexible Hours', '08:00', '17:00', 60, 8.0, 30, 30, 8.0, [0, 1, 2, 3, 4], False),
            ('Night Shift', '22:00', '06:00', 45, 7.25, 10, 10, 7.25, [0, 1, 2, 3, 4, 5], False),
            ('Half Day Saturday', '09:00', '18:00', 60, 8.0, 15, 15, 8.0, [0, 1, 2, 3, 4, 5], False),
            ('Remote Work Policy', '09:30', '18:30', 60, 8.0, 30, 30, 9.0, [0, 1, 2, 3, 4], False),
        ]

        for name, start, end, brk, total, grace_late, grace_early, ot, days, is_default in policies_data:
            from datetime import time
            h1, m1 = map(int, start.split(':'))
            h2, m2 = map(int, end.split(':'))
            WorkingHoursPolicy.all_objects.create(
                name=name, work_start_time=time(h1, m1), work_end_time=time(h2, m2),
                break_duration=brk, total_hours=total,
                grace_late_minutes=grace_late, grace_early_minutes=grace_early,
                overtime_threshold=ot, working_days=days,
                is_default=is_default, is_active=True, tenant=tenant,
            )
        self.stdout.write('  Created 5 working hours policies')

    def _seed_integrations(self, tenant):
        if IntegrationSetting.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Integration settings already exist, skipping...')
            return

        integrations_data = [
            ('Company SMTP Server', 'smtp', 'smtp_api_key_xxxxx', '', 'smtp.company.com',
             {'port': 587, 'use_tls': True, 'from_email': f'noreply@{tenant.slug}.com'}, 'active'),
            ('Slack Workspace', 'slack', 'xoxb-slack-token-xxxxx', 'slack_secret_xxxxx', 'https://slack.com/api',
             {'channel': '#hr-notifications', 'bot_name': 'HR Bot'}, 'active'),
            ('Microsoft Teams', 'teams', 'teams_webhook_xxxxx', '', 'https://outlook.office.com/webhook/',
             {'channel': 'HR Notifications'}, 'inactive'),
            ('Biometric Device', 'biometric', 'bio_api_key_xxxxx', '', 'https://biometric.local/api',
             {'device_id': 'BIO-001', 'sync_interval': 15}, 'active'),
            ('Google Workspace', 'google_workspace', 'google_api_key_xxxxx', 'google_secret_xxxxx', 'https://www.googleapis.com',
             {'domain': f'{tenant.slug}.com', 'sync_calendar': True}, 'inactive'),
            ('SMS Gateway', 'sms_gateway', 'sms_api_key_xxxxx', '', 'https://api.smsgateway.com/v2',
             {'sender_id': 'HRMSYS', 'country_code': '+91'}, 'active'),
        ]

        now = timezone.now()
        for name, provider, api_key, api_secret, base_url, config, status in integrations_data:
            tested_at = now - timedelta(days=random.randint(1, 15)) if status == 'active' else None
            IntegrationSetting.all_objects.create(
                name=name, provider=provider, api_key=api_key,
                api_secret=api_secret, base_url=base_url,
                config_json=config, status=status,
                last_tested_at=tested_at, is_active=True, tenant=tenant,
            )
        self.stdout.write('  Created 6 integration settings')

    def _seed_audit_trail(self, tenant, users):
        if AuditTrail.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Audit trail already exists, skipping...')
            return

        models_actions = [
            ('Employee', 'create', 'John Doe', {'first_name': {'old': '', 'new': 'John'}, 'last_name': {'old': '', 'new': 'Doe'}, 'email': {'old': '', 'new': 'john@company.com'}}),
            ('Employee', 'update', 'Jane Smith', {'department': {'old': 'Sales', 'new': 'Marketing'}, 'designation': {'old': 'Executive', 'new': 'Senior Executive'}}),
            ('Employee', 'update', 'Raj Kumar', {'salary': {'old': '50000', 'new': '55000'}, 'designation': {'old': 'Developer', 'new': 'Senior Developer'}}),
            ('Department', 'create', 'Engineering', {'name': {'old': '', 'new': 'Engineering'}, 'code': {'old': '', 'new': 'ENG'}}),
            ('Department', 'update', 'Marketing', {'head': {'old': 'None', 'new': 'Jane Smith'}}),
            ('LeaveApplication', 'create', 'Leave #101', {'employee': {'old': '', 'new': 'John Doe'}, 'type': {'old': '', 'new': 'Casual Leave'}, 'days': {'old': '', 'new': '3'}}),
            ('LeaveApplication', 'approve', 'Leave #101', {'status': {'old': 'pending', 'new': 'approved'}}),
            ('LeaveApplication', 'reject', 'Leave #102', {'status': {'old': 'pending', 'new': 'rejected'}, 'reason': {'old': '', 'new': 'Insufficient leave balance'}}),
            ('Attendance', 'update', 'Attendance - John 2025-02-15', {'status': {'old': 'absent', 'new': 'present'}, 'source': {'old': 'system', 'new': 'regularized'}}),
            ('PayrollPeriod', 'create', 'February 2025 Payroll', {'month': {'old': '', 'new': '2'}, 'year': {'old': '', 'new': '2025'}}),
            ('Salary', 'update', 'Salary - Raj Kumar', {'basic': {'old': '30000', 'new': '33000'}, 'hra': {'old': '12000', 'new': '13200'}}),
            ('JobRequisition', 'create', 'Software Engineer', {'department': {'old': '', 'new': 'Engineering'}, 'positions': {'old': '', 'new': '3'}}),
            ('User', 'create', 'newuser@company.com', {'username': {'old': '', 'new': 'newuser'}, 'role': {'old': '', 'new': 'employee'}}),
            ('User', 'update', 'admin@company.com', {'role': {'old': 'employee', 'new': 'hr_manager'}}),
            ('User', 'login', 'admin1', {}),
            ('User', 'login', 'admin1', {}),
            ('User', 'logout', 'admin1', {}),
            ('Role', 'create', 'HR Executive', {'name': {'old': '', 'new': 'HR Executive'}, 'code': {'old': '', 'new': 'hr_executive'}}),
            ('Company', 'update', tenant.name, {'address': {'old': '123 Old St', 'new': '456 New Ave'}}),
            ('Training', 'create', 'Leadership Workshop', {'category': {'old': '', 'new': 'Soft Skills'}, 'mode': {'old': '', 'new': 'classroom'}}),
            ('Employee', 'delete', 'Test Employee', {'reason': {'old': '', 'new': 'Duplicate record'}}),
            ('FinancialYear', 'create', 'FY 2025-26', {'start_date': {'old': '', 'new': '2025-04-01'}, 'end_date': {'old': '', 'new': '2026-03-31'}}),
            ('SystemSetting', 'update', 'timezone', {'value': {'old': 'UTC', 'new': 'Asia/Kolkata'}}),
            ('LeaveApplication', 'export', 'Leave Report Feb 2025', {}),
            ('PayrollPeriod', 'export', 'Salary Register Feb 2025', {}),
        ]

        ips = ['192.168.1.10', '192.168.1.25', '10.0.0.5', '172.16.0.100', '203.0.113.42']
        now = timezone.now()

        for i, (model, action, obj_repr, changes) in enumerate(models_actions):
            AuditTrail.all_objects.create(
                user=random.choice(users),
                action=action,
                model_name=model,
                object_id=random.randint(1, 100),
                object_repr=obj_repr,
                changes=changes,
                ip_address=random.choice(ips),
                tenant=tenant,
            )
            # Manually set timestamp to spread over past 30 days
            entry = AuditTrail.all_objects.filter(tenant=tenant).order_by('-pk').first()
            offset = timedelta(days=i, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            AuditTrail.all_objects.filter(pk=entry.pk).update(timestamp=now - offset)

        self.stdout.write('  Created 25 audit trail records')

    def _seed_data_retention(self, tenant):
        if DataRetentionPolicy.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Data retention policies already exist, skipping...')
            return

        policies_data = [
            ('employee_records', 2555, 'archive', 'Retain employee records for 7 years after separation'),
            ('payroll_data', 2555, 'archive', 'Retain payroll data for 7 years for tax compliance'),
            ('attendance_data', 1095, 'archive', 'Retain attendance records for 3 years'),
            ('audit_logs', 1825, 'archive', 'Retain audit logs for 5 years for compliance'),
            ('login_history', 365, 'delete', 'Purge login history older than 1 year'),
            ('documents', 3650, 'archive', 'Retain employee documents for 10 years'),
            ('applicant_data', 730, 'anonymize', 'Anonymize applicant data after 2 years per GDPR'),
        ]

        now = timezone.now()
        for data_type, days, action, desc in policies_data:
            last_exec = now - timedelta(days=random.randint(1, 30)) if random.random() > 0.3 else None
            DataRetentionPolicy.all_objects.create(
                data_type=data_type, retention_days=days, action=action,
                description=desc, is_active=True,
                last_executed=last_exec, tenant=tenant,
            )
        self.stdout.write('  Created 7 data retention policies')

    def _seed_backup(self, tenant, users):
        if BackupConfiguration.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Backup configuration already exists, skipping...')
            return

        config = BackupConfiguration.all_objects.create(
            backup_type='full', frequency='weekly', retention_count=5,
            include_media=True, is_active=True,
            last_backup_at=timezone.now() - timedelta(hours=12),
            last_backup_size='2.3 GB',
            tenant=tenant,
        )

        now = timezone.now()
        admin_user = users[0] if users else None
        logs_data = [
            ('completed', 7, '2.3 GB'),
            ('completed', 14, '2.1 GB'),
            ('completed', 21, '2.0 GB'),
            ('failed', 28, ''),
            ('completed', 35, '1.9 GB'),
            ('completed', 42, '1.8 GB'),
            ('completed', 1, '2.4 GB'),
        ]

        for status, days_ago, size in logs_data:
            started = now - timedelta(days=days_ago, hours=2)
            completed = started + timedelta(minutes=random.randint(15, 45)) if status == 'completed' else None
            error = 'Database connection timeout during backup' if status == 'failed' else ''
            log = BackupLog.all_objects.create(
                backup_config=config, status=status,
                completed_at=completed, file_size=size,
                error_message=error, initiated_by=admin_user,
                tenant=tenant,
            )
            BackupLog.all_objects.filter(pk=log.pk).update(started_at=started)

        self.stdout.write('  Created backup configuration with 7 backup logs')

    def _seed_notification_settings(self, tenant):
        if NotificationSetting.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Notification settings already exist, skipping...')
            return

        settings_data = [
            ('leave_applied', 'email', 'manager', True),
            ('leave_approved', 'both', 'employee', True),
            ('leave_rejected', 'both', 'employee', True),
            ('attendance_regularization', 'email', 'manager', True),
            ('expense_submitted', 'email', 'manager', True),
            ('expense_approved', 'email', 'employee', True),
            ('new_employee', 'both', 'hr', True),
            ('employee_birthday', 'in_app', 'employee', True),
            ('salary_processed', 'email', 'employee', True),
            ('password_reset', 'email', 'employee', True),
            ('welcome_email', 'email', 'employee', True),
            ('exit_initiated', 'both', 'hr', True),
            ('custom', 'none', 'admin', False),
        ]

        for event, channel, recipients, is_enabled in settings_data:
            NotificationSetting.all_objects.create(
                event=event, channel=channel, recipients=recipients,
                is_enabled=is_enabled, tenant=tenant,
            )
        self.stdout.write('  Created 13 notification settings')
