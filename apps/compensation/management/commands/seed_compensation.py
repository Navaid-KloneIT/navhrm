import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.organization.models import Designation
from apps.compensation.models import (
    SalaryBenchmark,
    BenefitPlan, EmployeeBenefit,
    FlexBenefitPlan, FlexBenefitOption, EmployeeFlexSelection,
    EquityGrant, VestingEvent, ExerciseRecord,
    CompensationPlan, CompensationRecommendation,
    RewardProgram, Recognition,
)


class Command(BaseCommand):
    help = 'Seed compensation & benefits module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding compensation data for {tenant.name}...')
            employees = list(Employee.all_objects.filter(tenant=tenant, status='active'))

            if len(employees) < 2:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - insufficient employees.'))
                continue

            self._seed_salary_benchmarks(tenant)
            self._seed_benefit_plans(tenant, employees)
            self._seed_flex_benefits(tenant, employees)
            self._seed_equity_grants(tenant, employees)
            self._seed_compensation_plans(tenant, employees)
            self._seed_reward_programs(tenant, employees)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding compensation data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Compensation module data seeding complete!'))

    def _seed_salary_benchmarks(self, tenant):
        if SalaryBenchmark.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Salary benchmarks already exist, skipping...')
            return

        designations = list(Designation.all_objects.filter(tenant=tenant))
        benchmarks = [
            ('Software Engineer', 'Technology', 'Bangalore', 600000, 900000, 1400000),
            ('Senior Software Engineer', 'Technology', 'Bangalore', 1200000, 1800000, 2600000),
            ('Product Manager', 'Technology', 'Mumbai', 1500000, 2200000, 3200000),
            ('HR Manager', 'Human Resources', 'Delhi', 800000, 1200000, 1800000),
            ('Data Analyst', 'Technology', 'Hyderabad', 500000, 750000, 1100000),
            ('Marketing Manager', 'Marketing', 'Mumbai', 900000, 1400000, 2000000),
            ('Finance Manager', 'Finance', 'Delhi', 1000000, 1500000, 2200000),
            ('DevOps Engineer', 'Technology', 'Pune', 800000, 1200000, 1800000),
        ]

        for title, industry, location, min_s, med_s, max_s in benchmarks:
            designation = random.choice(designations) if designations else None
            SalaryBenchmark.all_objects.create(
                tenant=tenant,
                designation=designation,
                job_title=title,
                industry=industry,
                location=location,
                min_salary=Decimal(str(min_s)),
                median_salary=Decimal(str(med_s)),
                max_salary=Decimal(str(max_s)),
                percentile_25=Decimal(str(int(min_s + (med_s - min_s) * 0.4))),
                percentile_75=Decimal(str(int(med_s + (max_s - med_s) * 0.6))),
                currency='INR',
                source='Market Survey 2025',
                effective_date=date.today() - timedelta(days=random.randint(0, 180)),
                is_active=True,
            )
        self.stdout.write('  Created 8 salary benchmarks.')

    def _seed_benefit_plans(self, tenant, employees):
        if BenefitPlan.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Benefit plans already exist, skipping...')
            return

        today = date.today()
        plans_data = [
            ('Group Health Insurance', 'health_insurance', 'Star Health', 2500, 5000),
            ('Term Life Insurance', 'life_insurance', 'ICICI Prudential', 500, 1500),
            ('Dental Coverage', 'dental', 'Aetna India', 300, 700),
            ('Vision Care Plan', 'vision', 'VSP India', 200, 400),
            ('NPS - Retirement Plan', 'retirement', 'PFRDA', 0, 5000),
            ('Disability Insurance', 'disability', 'HDFC Life', 150, 350),
            ('Wellness Program', 'wellness', 'HealthifyMe Corporate', 0, 1000),
        ]

        plans = []
        for name, plan_type, provider, emp_premium, er_premium in plans_data:
            plan = BenefitPlan.all_objects.create(
                tenant=tenant,
                name=name,
                plan_type=plan_type,
                provider=provider,
                description=f'{name} provided by {provider}',
                premium_employee=Decimal(str(emp_premium)),
                premium_employer=Decimal(str(er_premium)),
                enrollment_start=today - timedelta(days=30),
                enrollment_end=today + timedelta(days=60),
                effective_start=today,
                effective_end=today + timedelta(days=365),
                is_active=True,
            )
            plans.append(plan)
        self.stdout.write('  Created 7 benefit plans.')

        # Enroll some employees
        coverage_levels = ['employee_only', 'employee_spouse', 'family']
        for emp in employees[:min(8, len(employees))]:
            plan = random.choice(plans)
            EmployeeBenefit.all_objects.create(
                tenant=tenant,
                employee=emp,
                benefit_plan=plan,
                enrollment_date=today - timedelta(days=random.randint(0, 90)),
                coverage_level=random.choice(coverage_levels),
                status='active',
                policy_number=f'POL-{random.randint(100000, 999999)}',
            )
        self.stdout.write(f'  Created {min(8, len(employees))} employee benefit enrollments.')

    def _seed_flex_benefits(self, tenant, employees):
        if FlexBenefitPlan.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Flex benefit plans already exist, skipping...')
            return

        today = date.today()
        plan = FlexBenefitPlan.all_objects.create(
            tenant=tenant,
            name='Annual Flex Benefit Plan',
            description='Choose from a variety of benefits up to your allocated amount',
            total_allocation=Decimal('50000'),
            allocation_type='amount',
            period='annual',
            is_active=True,
        )

        options_data = [
            ('Gym Membership', 'Wellness', 12000),
            ('Meal Vouchers', 'Food', 24000),
            ('Fuel Allowance', 'Transport', 18000),
            ('Books & Learning', 'Education', 10000),
            ('Gadget Allowance', 'Technology', 25000),
            ('Internet Reimbursement', 'Utilities', 6000),
        ]

        options = []
        for name, category, cost in options_data:
            opt = FlexBenefitOption.all_objects.create(
                tenant=tenant,
                flex_plan=plan,
                name=name,
                category=category,
                description=f'{name} benefit option',
                cost=Decimal(str(cost)),
                is_active=True,
            )
            options.append(opt)
        self.stdout.write('  Created 1 flex plan with 6 options.')

        # Create selections for some employees
        for emp in employees[:min(5, len(employees))]:
            option = random.choice(options)
            EmployeeFlexSelection.all_objects.create(
                tenant=tenant,
                employee=emp,
                flex_plan=plan,
                flex_option=option,
                period_start=today,
                period_end=today + timedelta(days=365),
                status=random.choice(['selected', 'approved']),
            )
        self.stdout.write(f'  Created {min(5, len(employees))} flex selections.')

    def _seed_equity_grants(self, tenant, employees):
        if EquityGrant.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Equity grants already exist, skipping...')
            return

        today = date.today()
        grant_types = ['esop', 'rsu', 'stock_option']
        schedules = ['monthly', 'quarterly', 'annual', 'cliff']

        for emp in employees[:min(6, len(employees))]:
            grant_type = random.choice(grant_types)
            total = random.choice([100, 200, 500, 1000, 2000])
            grant = EquityGrant.all_objects.create(
                tenant=tenant,
                employee=emp,
                grant_type=grant_type,
                grant_date=today - timedelta(days=random.randint(90, 730)),
                total_shares=total,
                exercise_price=Decimal(str(random.randint(100, 500))),
                current_value_per_share=Decimal(str(random.randint(200, 800))),
                vesting_start_date=today - timedelta(days=random.randint(60, 365)),
                vesting_end_date=today + timedelta(days=random.randint(365, 1460)),
                vesting_schedule=random.choice(schedules),
                cliff_months=random.choice([0, 6, 12]),
                status=random.choice(['active', 'partially_vested']),
            )

            # Create vesting events
            vested_so_far = 0
            for i in range(random.randint(1, 4)):
                shares = min(random.randint(25, total // 4), total - vested_so_far)
                if shares <= 0:
                    break
                vested_so_far += shares
                is_vested = random.choice([True, False])
                VestingEvent.all_objects.create(
                    tenant=tenant,
                    equity_grant=grant,
                    vesting_date=today - timedelta(days=random.randint(0, 365)),
                    shares_vested=shares,
                    is_vested=is_vested,
                    vested_on=timezone.now() if is_vested else None,
                )

        self.stdout.write(f'  Created {min(6, len(employees))} equity grants with vesting events.')

    def _seed_compensation_plans(self, tenant, employees):
        if CompensationPlan.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Compensation plans already exist, skipping...')
            return

        today = date.today()
        plans_data = [
            ('Annual Merit Review 2025-26', 'annual_review', '2025-26', 5000000, 'approved'),
            ('Q1 Promotion Cycle', 'promotion', '2025-26', 2000000, 'completed'),
            ('Market Adjustment - Tech', 'market_adjustment', '2025-26', 1500000, 'active'),
            ('Special Retention Plan', 'special', '2025-26', 1000000, 'draft'),
        ]

        plans = []
        for name, plan_type, fiscal, budget, status in plans_data:
            plan = CompensationPlan.all_objects.create(
                tenant=tenant,
                name=name,
                plan_type=plan_type,
                fiscal_year=fiscal,
                budget_amount=Decimal(str(budget)),
                budget_utilized=Decimal(str(int(budget * random.uniform(0.1, 0.6)))),
                status=status,
                effective_date=today - timedelta(days=random.randint(0, 180)),
                end_date=today + timedelta(days=random.randint(90, 365)),
                description=f'{name} for fiscal year {fiscal}',
            )
            plans.append(plan)
        self.stdout.write('  Created 4 compensation plans.')

        # Create recommendations
        increase_types = ['merit', 'promotion', 'market_adjustment', 'retention']
        statuses = ['pending', 'approved', 'implemented']
        for emp in employees[:min(8, len(employees))]:
            plan = random.choice(plans)
            current = Decimal(str(random.randint(500000, 2000000)))
            pct = Decimal(str(random.randint(5, 25)))
            recommended = current * (1 + pct / 100)
            CompensationRecommendation.all_objects.create(
                tenant=tenant,
                compensation_plan=plan,
                employee=emp,
                current_salary=current,
                recommended_salary=recommended.quantize(Decimal('0.01')),
                increase_percentage=pct,
                increase_type=random.choice(increase_types),
                justification=f'Performance-based recommendation for {emp}',
                status=random.choice(statuses),
            )
        self.stdout.write(f'  Created {min(8, len(employees))} compensation recommendations.')

    def _seed_reward_programs(self, tenant, employees):
        if RewardProgram.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Reward programs already exist, skipping...')
            return

        programs_data = [
            ('Star Performer Award', 'spot_award', 500000, 10000, True),
            ('5 Year Service Award', 'service_award', 300000, 25000, True),
            ('Kudos Wall', 'peer_recognition', 100000, 500, True),
            ('Quarterly Performance Bonus', 'performance_bonus', 2000000, 50000, True),
            ('Team Excellence Award', 'team_award', 500000, 100000, True),
        ]

        programs = []
        for name, ptype, budget, value, monetary in programs_data:
            prog = RewardProgram.all_objects.create(
                tenant=tenant,
                name=name,
                program_type=ptype,
                description=f'{name} program',
                budget_amount=Decimal(str(budget)),
                budget_utilized=Decimal(str(int(budget * random.uniform(0.1, 0.4)))),
                reward_value=Decimal(str(value)),
                is_monetary=monetary,
                is_active=True,
            )
            programs.append(prog)
        self.stdout.write('  Created 5 reward programs.')

        # Create recognitions
        rec_types = ['spot_award', 'peer_recognition', 'achievement', 'innovation', 'leadership', 'teamwork']
        statuses = ['nominated', 'approved', 'awarded']
        today = date.today()

        for i in range(min(10, len(employees))):
            nominee = employees[i]
            nominator = random.choice([e for e in employees if e != nominee])
            program = random.choice(programs)
            status = random.choice(statuses)
            Recognition.all_objects.create(
                tenant=tenant,
                reward_program=program,
                nominee=nominee,
                nominator=nominator,
                recognition_type=random.choice(rec_types),
                title=f'{random.choice(["Outstanding", "Exceptional", "Great", "Brilliant"])} {random.choice(["Performance", "Contribution", "Teamwork", "Innovation"])}',
                description=f'Recognition for {nominee} nominated by {nominator}',
                reward_value=program.reward_value,
                status=status,
                awarded_date=today - timedelta(days=random.randint(0, 90)) if status == 'awarded' else None,
            )
        self.stdout.write(f'  Created {min(10, len(employees))} recognitions.')
