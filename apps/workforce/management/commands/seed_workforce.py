import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.organization.models import Department, Designation
from apps.workforce.models import (
    DemandForecast, SkillInventory, TalentAvailability,
    WorkforceGap, HiringBudget, SalaryForecast,
    WorkforceScenario, ScenarioDetail,
    ProductivityMetric, UtilizationRate,
)


class Command(BaseCommand):
    help = 'Seed workforce planning module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding workforce data for {tenant.name}...')
            employees = list(Employee.all_objects.filter(tenant=tenant, status='active'))

            if len(employees) < 5:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - insufficient employees.'))
                continue

            departments = list(Department.all_objects.filter(tenant=tenant, is_active=True))
            designations = list(Designation.all_objects.filter(tenant=tenant, is_active=True))

            self._seed_demand_forecasts(tenant, departments, designations)
            self._seed_skill_inventories(tenant, employees)
            self._seed_talent_availability(tenant, departments, designations)
            self._seed_workforce_gaps(tenant, departments, designations)
            self._seed_hiring_budgets(tenant, departments)
            self._seed_salary_forecasts(tenant, departments, designations)
            self._seed_scenarios(tenant, employees, departments, designations)
            self._seed_productivity_metrics(tenant, employees, departments)
            self._seed_utilization_rates(tenant, employees, departments)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding workforce data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Workforce planning module data seeding complete!'))

    def _seed_demand_forecasts(self, tenant, departments, designations):
        if DemandForecast.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Demand forecasts already exist, skipping...')
            return

        if not departments or not designations:
            return

        statuses = ['draft', 'submitted', 'approved', 'rejected']
        priorities = ['low', 'medium', 'high', 'critical']

        for i in range(min(8, len(departments))):
            dept = departments[i % len(departments)]
            desig = designations[i % len(designations)]
            current = random.randint(5, 50)
            projected = current + random.randint(-5, 20)
            growth = round((projected - current) / max(current, 1) * 100, 2)

            DemandForecast.all_objects.create(
                tenant=tenant,
                department=dept,
                designation=desig,
                fiscal_year='2026-2027',
                current_headcount=current,
                projected_headcount=projected,
                growth_rate=Decimal(str(growth)),
                justification=f'Business growth projection for {dept.name} - {desig.name}',
                status=random.choice(statuses),
                priority=random.choice(priorities),
            )
        self.stdout.write(f'  Created {min(8, len(departments))} demand forecasts.')

    def _seed_skill_inventories(self, tenant, employees):
        if SkillInventory.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Skill inventories already exist, skipping...')
            return

        skills = [
            'Python', 'JavaScript', 'Project Management', 'Data Analysis',
            'Leadership', 'Communication', 'SQL', 'Excel', 'Machine Learning',
            'Cloud Computing', 'Agile', 'DevOps',
        ]
        proficiencies = ['beginner', 'intermediate', 'advanced', 'expert']

        for emp in employees[:10]:
            for skill_name in random.sample(skills, random.randint(2, 4)):
                SkillInventory.all_objects.create(
                    tenant=tenant,
                    employee=emp,
                    skill_name=skill_name,
                    proficiency_level=random.choice(proficiencies),
                    years_of_experience=Decimal(str(random.randint(1, 15))),
                    certified=random.choice([True, False]),
                    certification_expiry=date.today() + timedelta(days=random.randint(30, 730)) if random.choice([True, False]) else None,
                    is_active=True,
                )
        self.stdout.write('  Created skill inventories.')

    def _seed_talent_availability(self, tenant, departments, designations):
        if TalentAvailability.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Talent availability already exist, skipping...')
            return

        if not departments:
            return

        for dept in departments[:6]:
            desig = designations[0] if designations else None
            TalentAvailability.all_objects.create(
                tenant=tenant,
                department=dept,
                designation=desig,
                available_count=random.randint(10, 40),
                on_notice_count=random.randint(0, 5),
                retiring_count=random.randint(0, 3),
                transfer_ready_count=random.randint(0, 5),
                period='Q1-2026',
                notes=f'Talent availability for {dept.name}',
            )
        self.stdout.write(f'  Created {min(6, len(departments))} talent availability records.')

    def _seed_workforce_gaps(self, tenant, departments, designations):
        if WorkforceGap.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Workforce gaps already exist, skipping...')
            return

        if not departments or not designations:
            return

        priorities = ['low', 'medium', 'high', 'critical']
        statuses = ['identified', 'in_progress', 'resolved', 'deferred']

        for i in range(min(6, len(departments))):
            dept = departments[i]
            desig = designations[i % len(designations)]
            required = random.randint(10, 40)
            available = random.randint(5, 35)

            WorkforceGap.all_objects.create(
                tenant=tenant,
                department=dept,
                designation=desig,
                required_count=required,
                available_count=available,
                skills_gap_description=f'Skills gap in {desig.name} for {dept.name}',
                priority=random.choice(priorities),
                action_plan=f'Hire {max(0, required - available)} new employees and upskill existing team.',
                status=random.choice(statuses),
                fiscal_year='2026-2027',
            )
        self.stdout.write(f'  Created {min(6, len(departments))} workforce gaps.')

    def _seed_hiring_budgets(self, tenant, departments):
        if HiringBudget.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Hiring budgets already exist, skipping...')
            return

        if not departments:
            return

        statuses = ['draft', 'submitted', 'approved', 'rejected']

        for dept in departments[:6]:
            allocated = Decimal(str(random.randint(500000, 5000000)))
            utilized = allocated * Decimal(str(random.uniform(0.2, 0.8)))
            budgeted = random.randint(5, 20)
            filled = random.randint(0, budgeted)

            HiringBudget.all_objects.create(
                tenant=tenant,
                department=dept,
                fiscal_year='2026-2027',
                allocated_budget=allocated,
                utilized_budget=utilized.quantize(Decimal('0.01')),
                positions_budgeted=budgeted,
                positions_filled=filled,
                status=random.choice(statuses),
                notes=f'Hiring budget for {dept.name}',
            )
        self.stdout.write(f'  Created {min(6, len(departments))} hiring budgets.')

    def _seed_salary_forecasts(self, tenant, departments, designations):
        if SalaryForecast.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Salary forecasts already exist, skipping...')
            return

        if not departments or not designations:
            return

        for i in range(min(6, len(departments))):
            dept = departments[i]
            desig = designations[i % len(designations)]
            current_salary = Decimal(str(random.randint(30000, 120000)))
            increment = Decimal(str(random.uniform(3.0, 15.0))).quantize(Decimal('0.01'))
            projected = (current_salary * (1 + increment / 100)).quantize(Decimal('0.01'))

            SalaryForecast.all_objects.create(
                tenant=tenant,
                department=dept,
                designation=desig,
                current_avg_salary=current_salary,
                projected_avg_salary=projected,
                increment_percentage=increment,
                effective_date=date(2026, 4, 1),
                fiscal_year='2026-2027',
                headcount=random.randint(5, 30),
                notes=f'Salary forecast for {desig.name} in {dept.name}',
            )
        self.stdout.write(f'  Created {min(6, len(departments))} salary forecasts.')

    def _seed_scenarios(self, tenant, employees, departments, designations):
        if WorkforceScenario.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Workforce scenarios already exist, skipping...')
            return

        if not departments or not designations:
            return

        scenario_data = [
            ('Business Expansion Plan', 'growth', 'Plan for 30% headcount growth across all departments.'),
            ('Cost Optimization', 'restructuring', 'Restructure teams for improved efficiency.'),
            ('Market Downturn Response', 'downsizing', 'Contingency plan for economic slowdown.'),
        ]

        for name, stype, desc in scenario_data:
            scenario = WorkforceScenario.all_objects.create(
                tenant=tenant,
                name=name,
                description=desc,
                scenario_type=stype,
                base_year='2025-2026',
                projection_year='2026-2027',
                assumptions=f'Assumes {stype} scenario with market conditions.',
                impact_summary=f'Estimated impact across {len(departments)} departments.',
                status=random.choice(['draft', 'active']),
                created_by=random.choice(employees),
            )

            for j, dept in enumerate(departments[:4]):
                desig = designations[j % len(designations)]
                current = random.randint(10, 40)
                if stype == 'growth':
                    projected = current + random.randint(5, 15)
                elif stype == 'downsizing':
                    projected = max(1, current - random.randint(3, 10))
                else:
                    projected = current + random.randint(-5, 5)

                ScenarioDetail.all_objects.create(
                    tenant=tenant,
                    scenario=scenario,
                    department=dept,
                    designation=desig,
                    current_headcount=current,
                    projected_headcount=projected,
                    cost_impact=Decimal(str((projected - current) * random.randint(40000, 80000))),
                    notes=f'Impact on {dept.name}',
                )

        self.stdout.write('  Created 3 workforce scenarios with details.')

    def _seed_productivity_metrics(self, tenant, employees, departments):
        if ProductivityMetric.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Productivity metrics already exist, skipping...')
            return

        if not departments:
            return

        metric_names = [
            'Revenue per Employee', 'Tasks Completed', 'Customer Satisfaction',
            'Project Delivery Rate', 'Code Review Throughput', 'Sales Conversion',
        ]

        for i, name in enumerate(metric_names):
            dept = departments[i % len(departments)]
            emp = employees[i % len(employees)] if i % 2 == 0 else None
            target = Decimal(str(random.randint(50, 200)))
            value = target * Decimal(str(random.uniform(0.7, 1.3)))

            ProductivityMetric.all_objects.create(
                tenant=tenant,
                department=dept,
                employee=emp,
                metric_name=name,
                metric_value=value.quantize(Decimal('0.01')),
                target_value=target,
                measurement_period='Q1-2026',
                measurement_date=date.today() - timedelta(days=random.randint(0, 90)),
                notes=f'Metric: {name}',
            )
        self.stdout.write('  Created 6 productivity metrics.')

    def _seed_utilization_rates(self, tenant, employees, departments):
        if UtilizationRate.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Utilization rates already exist, skipping...')
            return

        for emp in employees[:8]:
            dept = departments[0] if departments else None
            total = Decimal('176.00')
            productive = total * Decimal(str(random.uniform(0.65, 0.95)))
            billable = productive * Decimal(str(random.uniform(0.5, 0.9)))

            UtilizationRate.all_objects.create(
                tenant=tenant,
                department=dept,
                employee=emp,
                period='March 2026',
                total_hours=total,
                productive_hours=productive.quantize(Decimal('0.01')),
                billable_hours=billable.quantize(Decimal('0.01')),
                non_billable_hours=(productive - billable).quantize(Decimal('0.01')),
                notes=f'Utilization for {emp.first_name}',
            )
        self.stdout.write('  Created 8 utilization rates.')
