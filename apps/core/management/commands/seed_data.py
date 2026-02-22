import random
from datetime import timedelta, date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.core.models import Tenant, set_current_tenant
from apps.accounts.models import User, UserProfile
from apps.organization.models import (
    Company, Location, Department, JobGrade, Designation, CostCenter
)
from apps.employees.models import (
    Employee, EmergencyContact, EmployeeDocument, EmployeeLifecycleEvent
)
from apps.onboarding.models import (
    OnboardingTemplate, OnboardingTemplateTask, OnboardingProcess,
    OnboardingTask, AssetAllocation, OrientationSession, WelcomeKit
)
from apps.offboarding.models import (
    Resignation, ExitInterview, ClearanceItem, ClearanceProcess,
    ClearanceChecklistItem, FnFSettlement, ExperienceLetter
)

fake = Faker()

DEPARTMENTS = [
    'Engineering', 'Human Resources', 'Finance', 'Marketing',
    'Sales', 'Operations', 'Customer Support', 'Product', 'Design', 'Legal'
]

DESIGNATIONS = [
    ('CEO', 10), ('CTO', 9), ('CFO', 9), ('VP Engineering', 8),
    ('VP Marketing', 8), ('Director', 7), ('Senior Manager', 6),
    ('Manager', 5), ('Team Lead', 4), ('Senior Engineer', 4),
    ('Software Engineer', 3), ('Junior Engineer', 2),
    ('HR Manager', 5), ('HR Executive', 3), ('Accountant', 3),
    ('Marketing Executive', 3), ('Sales Executive', 3),
    ('Support Executive', 2), ('Designer', 3), ('Intern', 1),
]

ASSET_TYPES = ['laptop', 'desktop', 'phone', 'id_card', 'access_card']


class Command(BaseCommand):
    help = 'Seed the database with fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenants', type=int, default=3,
            help='Number of tenants to create'
        )
        parser.add_argument(
            '--employees', type=int, default=50,
            help='Number of employees per tenant'
        )

    def handle(self, *args, **options):
        num_tenants = options['tenants']
        num_employees = options['employees']

        self.stdout.write('Seeding database...\n')

        for i in range(num_tenants):
            tenant = self._create_tenant(i)
            set_current_tenant(tenant)
            self.stdout.write(f'  Created tenant: {tenant.name}')

            admin_user = self._create_admin_user(tenant, i)
            users = self._create_users(tenant, 5)
            self.stdout.write(f'  Created {len(users) + 1} users')

            company = self._create_company(tenant)
            locations = self._create_locations(tenant, company)
            departments = self._create_departments(tenant, company)
            job_grades = self._create_job_grades(tenant)
            designations = self._create_designations(tenant, departments, job_grades)
            cost_centers = self._create_cost_centers(tenant, departments)
            self.stdout.write(f'  Created org structure: {len(departments)} depts, {len(designations)} designations')

            employees = self._create_employees(tenant, departments, designations, num_employees)
            self.stdout.write(f'  Created {len(employees)} employees')

            self._assign_department_heads(departments, employees)
            self._create_emergency_contacts(tenant, employees)
            self._create_lifecycle_events(tenant, employees, departments, designations, admin_user)

            self._create_onboarding_data(tenant, employees, users + [admin_user])
            self._create_offboarding_data(tenant, employees, admin_user)

            self.stdout.write(f'  Completed tenant: {tenant.name}\n')

        set_current_tenant(None)
        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))

    def _create_tenant(self, index):
        names = ['Acme Corporation', 'TechVision Inc', 'GlobalSoft Solutions',
                 'Innovate Labs', 'Stellar Systems']
        name = names[index] if index < len(names) else fake.company()
        return Tenant.objects.create(
            name=name,
            email=fake.company_email(),
            phone=fake.phone_number()[:20],
            address=fake.address(),
            website=fake.url(),
        )

    def _create_admin_user(self, tenant, index):
        user = User.objects.create_user(
            username=f'admin{index + 1}',
            email=f'admin{index + 1}@example.com',
            password='password123',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            tenant=tenant,
            role='tenant_admin',
            is_tenant_admin=True,
            phone=fake.phone_number()[:20],
        )
        UserProfile.objects.create(
            user=user,
            bio=fake.text(max_nb_chars=200),
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=55),
            city=fake.city(),
            state=fake.state(),
            country='United States',
        )
        return user

    def _create_users(self, tenant, count):
        users = []
        roles = ['hr_manager', 'hr_staff', 'manager', 'employee', 'employee']
        for i in range(count):
            user = User.objects.create_user(
                username=fake.user_name() + str(random.randint(100, 999)),
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                tenant=tenant,
                role=roles[i % len(roles)],
                phone=fake.phone_number()[:20],
            )
            UserProfile.objects.create(
                user=user,
                bio=fake.text(max_nb_chars=150),
                date_of_birth=fake.date_of_birth(minimum_age=22, maximum_age=50),
                city=fake.city(),
                state=fake.state(),
                country='United States',
            )
            users.append(user)
        return users

    def _create_company(self, tenant):
        return Company.objects.create(
            tenant=tenant,
            name=tenant.name,
            legal_name=tenant.name + ' LLC',
            registration_number=fake.bothify('REG-####-????'),
            tax_id=fake.bothify('##-#######'),
            email=tenant.email,
            phone=tenant.phone,
            website=tenant.website,
            address_line1=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            country='United States',
            zip_code=fake.zipcode(),
            founded_date=fake.date_between(start_date='-20y', end_date='-2y'),
            industry=random.choice(['Technology', 'Finance', 'Healthcare', 'Consulting', 'Manufacturing']),
            description=fake.text(max_nb_chars=300),
        )

    def _create_locations(self, tenant, company):
        locations = []
        for i in range(random.randint(2, 4)):
            locations.append(Location.objects.create(
                tenant=tenant,
                company=company,
                name=f'{fake.city()} Office',
                address_line1=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                country='United States',
                zip_code=fake.zipcode(),
                phone=fake.phone_number()[:20],
                is_headquarters=(i == 0),
            ))
        return locations

    def _create_departments(self, tenant, company):
        departments = []
        for name in DEPARTMENTS:
            departments.append(Department.objects.create(
                tenant=tenant,
                name=name,
                code=name[:3].upper(),
                description=fake.text(max_nb_chars=200),
                company=company,
            ))
        # Set some parent relationships
        for dept in departments[5:]:
            dept.parent = random.choice(departments[:5])
            dept.save()
        return departments

    def _create_job_grades(self, tenant):
        grades = []
        grade_data = [
            ('G1 - Entry', 1, 30000, 45000),
            ('G2 - Junior', 2, 40000, 60000),
            ('G3 - Mid', 3, 55000, 80000),
            ('G4 - Senior', 4, 75000, 110000),
            ('G5 - Lead', 5, 100000, 140000),
            ('G6 - Manager', 6, 120000, 170000),
            ('G7 - Director', 7, 150000, 220000),
            ('G8 - VP', 8, 180000, 280000),
            ('G9 - C-Suite', 9, 250000, 400000),
            ('G10 - Executive', 10, 300000, 500000),
        ]
        for name, level, min_s, max_s in grade_data:
            grades.append(JobGrade.objects.create(
                tenant=tenant,
                name=name,
                code=f'G{level}',
                level=level,
                min_salary=Decimal(str(min_s)),
                max_salary=Decimal(str(max_s)),
            ))
        return grades

    def _create_designations(self, tenant, departments, job_grades):
        designations = []
        for title, level in DESIGNATIONS:
            dept = random.choice(departments)
            grade = next((g for g in job_grades if g.level == level), job_grades[0])
            designations.append(Designation.objects.create(
                tenant=tenant,
                name=title,
                code=title[:4].upper().replace(' ', ''),
                department=dept,
                job_grade=grade,
                description=fake.text(max_nb_chars=150),
                responsibilities=fake.text(max_nb_chars=200),
            ))
        return designations

    def _create_cost_centers(self, tenant, departments):
        centers = []
        for i, dept in enumerate(departments[:6]):
            budget = Decimal(str(random.randint(50000, 500000)))
            spent = budget * Decimal(str(random.uniform(0.1, 0.8)))
            centers.append(CostCenter.objects.create(
                tenant=tenant,
                name=f'{dept.name} Cost Center',
                code=f'CC-{tenant.slug[:4].upper()}-{dept.code}-{i+1:03d}',
                description=f'Cost center for {dept.name}',
                department=dept,
                budget=budget,
                spent=spent.quantize(Decimal('0.01')),
            ))
        return centers

    def _create_employees(self, tenant, departments, designations, count):
        employees = []
        statuses = ['active'] * 8 + ['on_leave', 'resigned']

        for i in range(count):
            dept = random.choice(departments)
            desig = random.choice([d for d in designations if d.department == dept] or designations)
            grade = desig.job_grade
            salary = Decimal(str(random.randint(
                int(grade.min_salary or 30000),
                int(grade.max_salary or 100000)
            ))) if grade else Decimal(str(random.randint(30000, 100000)))

            joining = fake.date_between(start_date='-5y', end_date='today')
            status = random.choice(statuses)
            leaving = None
            if status == 'resigned':
                leaving = fake.date_between(start_date=joining, end_date='today')

            emp = Employee.objects.create(
                tenant=tenant,
                employee_id=f'{tenant.slug[:4].upper()}-{i+1:04d}',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number()[:20],
                personal_email=fake.email(),
                date_of_birth=fake.date_of_birth(minimum_age=22, maximum_age=55),
                gender=random.choice(['male', 'female']),
                marital_status=random.choice(['single', 'married', 'single', 'single']),
                blood_group=random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-']),
                nationality=random.choice(['American', 'Indian', 'British', 'Canadian', 'Australian']),
                address_line1=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                country='United States',
                zip_code=fake.zipcode(),
                department=dept,
                designation=desig,
                employment_type=random.choice(['full_time'] * 7 + ['part_time', 'contract', 'intern']),
                date_of_joining=joining,
                date_of_leaving=leaving,
                probation_end_date=joining + timedelta(days=90),
                status=status,
                salary=salary,
                bank_name=random.choice(['Chase', 'Bank of America', 'Wells Fargo', 'Citi']),
                bank_account=fake.bban()[:20],
            )
            employees.append(emp)

        # Assign some reporting managers
        managers = [e for e in employees if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        for emp in employees:
            if managers and emp not in managers:
                dept_managers = [m for m in managers if m.department == emp.department]
                emp.reporting_manager = random.choice(dept_managers or managers)
                emp.save()

        return employees

    def _assign_department_heads(self, departments, employees):
        for dept in departments:
            dept_emps = [e for e in employees if e.department == dept and e.status == 'active']
            if dept_emps:
                senior = sorted(
                    dept_emps,
                    key=lambda e: e.designation.job_grade.level if e.designation and e.designation.job_grade else 0,
                    reverse=True
                )
                dept.head = senior[0]
                dept.save()

    def _create_emergency_contacts(self, tenant, employees):
        for emp in employees[:30]:
            for _ in range(random.randint(1, 2)):
                EmergencyContact.objects.create(
                    tenant=tenant,
                    employee=emp,
                    name=fake.name(),
                    relationship=random.choice(['spouse', 'parent', 'sibling', 'friend']),
                    phone=fake.phone_number()[:20],
                    email=fake.email(),
                    is_primary=True,
                )

    def _create_lifecycle_events(self, tenant, employees, departments, designations, admin_user):
        for emp in employees[:20]:
            EmployeeLifecycleEvent.objects.create(
                tenant=tenant,
                employee=emp,
                event_type='hired',
                event_date=emp.date_of_joining,
                description=f'Hired as {emp.designation or "Employee"}',
                to_department=emp.department,
                to_designation=emp.designation,
                new_salary=emp.salary,
                processed_by=admin_user,
            )

        for emp in random.sample(list(employees[:20]), min(5, len(employees))):
            new_dept = random.choice(departments)
            new_desig = random.choice(designations)
            EmployeeLifecycleEvent.objects.create(
                tenant=tenant,
                employee=emp,
                event_type=random.choice(['promoted', 'transferred']),
                event_date=fake.date_between(start_date=emp.date_of_joining, end_date='today'),
                description=fake.text(max_nb_chars=100),
                from_department=emp.department,
                to_department=new_dept,
                from_designation=emp.designation,
                to_designation=new_desig,
                old_salary=emp.salary,
                new_salary=emp.salary * Decimal('1.15'),
                processed_by=admin_user,
            )

    def _create_onboarding_data(self, tenant, employees, users):
        # Templates
        template = OnboardingTemplate.objects.create(
            tenant=tenant,
            name='Standard Onboarding',
            description='Default onboarding process for new employees',
        )
        task_titles = [
            'Complete HR paperwork', 'IT system access setup',
            'Workstation setup', 'Team introduction',
            'Company policy review', 'Benefits enrollment',
            'Security training', 'First week check-in',
        ]
        for i, title in enumerate(task_titles):
            OnboardingTemplateTask.objects.create(
                tenant=tenant,
                template=template,
                title=title,
                description=fake.text(max_nb_chars=100),
                days_after_joining=i * 2,
                order=i,
            )

        # Processes for recent employees
        recent = [e for e in employees if e.status == 'active'][:5]
        for emp in recent:
            process = OnboardingProcess.objects.create(
                tenant=tenant,
                employee=emp,
                template=template,
                status=random.choice(['pending', 'in_progress', 'completed']),
                start_date=emp.date_of_joining,
                target_completion_date=emp.date_of_joining + timedelta(days=30),
            )
            for j, title in enumerate(task_titles[:5]):
                OnboardingTask.objects.create(
                    tenant=tenant,
                    process=process,
                    title=title,
                    assigned_to=random.choice(users),
                    status=random.choice(['pending', 'completed', 'in_progress']),
                    due_date=emp.date_of_joining + timedelta(days=j * 3),
                    order=j,
                )

        # Assets
        for emp in employees[:15]:
            AssetAllocation.objects.create(
                tenant=tenant,
                employee=emp,
                asset_type=random.choice(ASSET_TYPES),
                asset_name=f'{random.choice(["MacBook Pro", "ThinkPad", "Dell XPS", "iPhone"])}',
                asset_id=fake.bothify('AST-####'),
                serial_number=fake.bothify('SN-????????'),
                allocated_date=emp.date_of_joining,
                status='allocated',
            )

        # Orientation sessions
        for _ in range(3):
            OrientationSession.objects.create(
                tenant=tenant,
                title=random.choice([
                    'Company Overview', 'IT Security Training',
                    'HR Policies Overview', 'Team Meet & Greet'
                ]),
                session_type=random.choice(['training', 'meet_greet', 'presentation']),
                description=fake.text(max_nb_chars=150),
                facilitator=random.choice(users),
                date=fake.date_between(start_date='today', end_date='+30d'),
                start_time='09:00',
                end_time='11:00',
                location='Conference Room A',
            )

        # Welcome Kit
        WelcomeKit.objects.create(
            tenant=tenant,
            name='Standard Welcome Kit',
            description='Welcome package for new hires',
            message='Welcome to the team! We are excited to have you on board.',
            policies='Please review our employee handbook and code of conduct.',
        )

    def _create_offboarding_data(self, tenant, employees, admin_user):
        resigned = [e for e in employees if e.status == 'resigned'][:3]

        for emp in resigned:
            leaving = emp.date_of_leaving or fake.date_between(start_date='-6m', end_date='today')

            Resignation.objects.create(
                tenant=tenant,
                employee=emp,
                resignation_date=leaving - timedelta(days=30),
                last_working_day=leaving,
                reason=fake.text(max_nb_chars=200),
                status=random.choice(['approved', 'submitted']),
                approved_by=admin_user,
                approved_date=leaving - timedelta(days=25),
            )

            ExitInterview.objects.create(
                tenant=tenant,
                employee=emp,
                interviewer=admin_user,
                scheduled_date=timezone.now() - timedelta(days=random.randint(1, 60)),
                status='completed',
                overall_experience=random.randint(3, 5),
                reason_for_leaving=fake.text(max_nb_chars=150),
                what_liked=fake.text(max_nb_chars=100),
                what_disliked=fake.text(max_nb_chars=100),
                would_recommend=random.choice([True, False, True]),
                additional_feedback=fake.text(max_nb_chars=150),
            )

        # Clearance items
        clearance_items = []
        for name in ['IT Assets Return', 'Finance Clearance', 'HR Clearance',
                      'Admin Clearance', 'Manager Sign-off']:
            clearance_items.append(ClearanceItem.objects.create(
                tenant=tenant,
                name=name,
                description=f'Clearance from {name}',
                is_mandatory=True,
                order=len(clearance_items),
            ))

        for emp in resigned[:2]:
            process = ClearanceProcess.objects.create(
                tenant=tenant,
                employee=emp,
                status='completed',
                initiated_date=emp.date_of_leaving - timedelta(days=15) if emp.date_of_leaving else date.today(),
                completed_date=emp.date_of_leaving,
            )
            for item in clearance_items:
                ClearanceChecklistItem.objects.create(
                    tenant=tenant,
                    process=process,
                    clearance_item=item,
                    status='cleared',
                    cleared_by=admin_user,
                    cleared_date=emp.date_of_leaving or date.today(),
                )

            salary = emp.salary or Decimal('50000')
            FnFSettlement.objects.create(
                tenant=tenant,
                employee=emp,
                settlement_date=emp.date_of_leaving or date.today(),
                status='paid',
                basic_salary=salary / 12,
                pending_salary=salary / 24,
                leave_encashment=Decimal(str(random.randint(5000, 20000))),
                bonus=Decimal(str(random.randint(0, 10000))),
                gratuity=Decimal(str(random.randint(0, 50000))),
                notice_period_recovery=Decimal('0'),
                tax_deduction=salary / 36,
                approved_by=admin_user,
            )

            ExperienceLetter.objects.create(
                tenant=tenant,
                employee=emp,
                letter_date=emp.date_of_leaving or date.today(),
                letter_type='experience',
                content=f'This is to certify that {emp.full_name} (Employee ID: {emp.employee_id}) '
                        f'was employed with {tenant.name} from {emp.date_of_joining} to '
                        f'{emp.date_of_leaving or "present"}. During their tenure, they served as '
                        f'{emp.designation or "Employee"} in the {emp.department or "organization"}. '
                        f'We wish them all the best in their future endeavors.',
                generated_by=admin_user,
                is_issued=True,
            )
