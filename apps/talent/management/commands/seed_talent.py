import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.organization.models import Department, Designation
from apps.talent.models import (
    TalentAssessment,
    CriticalPosition, SuccessionCandidate,
    CareerPath, CareerPathStep, EmployeeCareerPlan,
    InternalJobPosting, TransferApplication,
    TalentReviewSession, TalentReviewParticipant,
    FlightRiskAssessment, RetentionPlan, RetentionAction,
)


class Command(BaseCommand):
    help = 'Seed talent management module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding talent data for {tenant.name}...')
            employees = list(Employee.all_objects.filter(tenant=tenant, status='active'))

            if len(employees) < 5:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - insufficient employees.'))
                continue

            departments = list(Department.all_objects.filter(tenant=tenant, is_active=True))
            designations = list(Designation.all_objects.filter(tenant=tenant, is_active=True))

            self._seed_talent_assessments(tenant, employees)
            self._seed_critical_positions(tenant, employees, departments, designations)
            self._seed_career_paths(tenant, employees, departments, designations)
            self._seed_internal_postings(tenant, employees, departments, designations)
            self._seed_talent_reviews(tenant, employees)
            self._seed_retention(tenant, employees)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding talent data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Talent management module data seeding complete!'))

    def _seed_talent_assessments(self, tenant, employees):
        if TalentAssessment.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Talent assessments already exist, skipping...')
            return

        today = date.today()
        for emp in employees[:10]:
            TalentAssessment.all_objects.create(
                tenant=tenant,
                employee=emp,
                performance_rating=random.randint(1, 5),
                potential_rating=random.randint(1, 5),
                assessment_date=today - timedelta(days=random.randint(0, 180)),
                assessed_by=random.choice(employees),
                notes=f'Assessment for {emp.first_name}',
                is_active=True,
            )
        self.stdout.write(f'  Created {min(10, len(employees))} talent assessments.')

    def _seed_critical_positions(self, tenant, employees, departments, designations):
        if CriticalPosition.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Critical positions already exist, skipping...')
            return

        if not designations or not departments:
            self.stdout.write('  No designations/departments, skipping critical positions...')
            return

        criticality_levels = ['critical', 'high', 'medium', 'low']
        positions = []
        for i, desig in enumerate(designations[:5]):
            dept = departments[i % len(departments)] if departments else None
            pos = CriticalPosition.all_objects.create(
                tenant=tenant,
                designation=desig,
                department=dept,
                criticality=criticality_levels[i % len(criticality_levels)],
                incumbent=employees[i] if i < len(employees) else None,
                reason=f'Key role for business continuity',
                status='active',
            )
            positions.append(pos)

        # Add succession candidates
        readiness_levels = ['ready_now', 'ready_1_2_years', 'ready_3_5_years']
        statuses = ['identified', 'in_development', 'ready']
        used_combos = set()
        for pos in positions:
            for j in range(random.randint(1, 3)):
                emp = random.choice(employees)
                combo = (pos.pk, emp.pk)
                if combo in used_combos:
                    continue
                used_combos.add(combo)
                SuccessionCandidate.all_objects.create(
                    tenant=tenant,
                    critical_position=pos,
                    employee=emp,
                    readiness=random.choice(readiness_levels),
                    status=random.choice(statuses),
                    development_needs='Leadership training, cross-functional exposure',
                    strengths='Strong technical skills, good team player',
                )

        self.stdout.write(f'  Created {len(positions)} critical positions with successors.')

    def _seed_career_paths(self, tenant, employees, departments, designations):
        if CareerPath.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Career paths already exist, skipping...')
            return

        if not designations:
            self.stdout.write('  No designations, skipping career paths...')
            return

        path_names = [
            ('Engineering Track', 'Technical career progression'),
            ('Management Track', 'People management progression'),
            ('Product Track', 'Product management progression'),
        ]

        for name, desc in path_names:
            dept = departments[0] if departments else None
            path = CareerPath.all_objects.create(
                tenant=tenant,
                name=name,
                description=desc,
                department=dept,
                status='active',
            )

            # Add steps
            for seq in range(1, min(4, len(designations) + 1)):
                CareerPathStep.all_objects.create(
                    tenant=tenant,
                    career_path=path,
                    sequence=seq,
                    designation=designations[(seq - 1) % len(designations)],
                    required_experience_years=seq * 2,
                    required_skills=f'Skill set for level {seq}',
                    required_competencies=f'Core competencies for step {seq}',
                    description=f'Step {seq} in {name}',
                )

        # Create employee career plans
        paths = list(CareerPath.all_objects.filter(tenant=tenant))
        for emp in employees[:5]:
            path = random.choice(paths)
            steps = list(path.steps.all().order_by('sequence'))
            if steps:
                EmployeeCareerPlan.all_objects.create(
                    tenant=tenant,
                    employee=emp,
                    career_path=path,
                    current_step=steps[0] if steps else None,
                    target_step=steps[-1] if steps else None,
                    target_date=date.today() + timedelta(days=random.randint(365, 1095)),
                    status='active',
                )

        self.stdout.write(f'  Created {len(path_names)} career paths with steps and plans.')

    def _seed_internal_postings(self, tenant, employees, departments, designations):
        if InternalJobPosting.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Internal postings already exist, skipping...')
            return

        posting_titles = [
            'Senior Developer - Backend Team',
            'Team Lead - Frontend',
            'Product Manager - Growth',
            'HR Business Partner',
        ]

        today = date.today()
        postings = []
        for i, title in enumerate(posting_titles):
            posting = InternalJobPosting.all_objects.create(
                tenant=tenant,
                title=title,
                department=departments[i % len(departments)] if departments else None,
                designation=designations[i % len(designations)] if designations else None,
                description=f'We are looking for an internal candidate for {title}.',
                requirements='Minimum 2 years in current role, good performance record.',
                positions=1,
                status=['open', 'open', 'closed', 'on_hold'][i],
                posted_by=employees[0] if employees else None,
                closing_date=today + timedelta(days=random.randint(15, 60)),
            )
            postings.append(posting)

        # Create transfer applications
        statuses = ['applied', 'shortlisted', 'selected', 'rejected']
        used_combos = set()
        for posting in postings[:2]:  # Only for open postings
            for j in range(random.randint(1, 3)):
                emp = random.choice(employees[1:])
                combo = (posting.pk, emp.pk)
                if combo in used_combos:
                    continue
                used_combos.add(combo)
                TransferApplication.all_objects.create(
                    tenant=tenant,
                    posting=posting,
                    employee=emp,
                    current_department=departments[0] if departments else None,
                    current_designation=designations[0] if designations else None,
                    reason='Seeking career growth and new challenges.',
                    status=random.choice(statuses),
                )

        self.stdout.write(f'  Created {len(posting_titles)} internal postings with applications.')

    def _seed_talent_reviews(self, tenant, employees):
        if TalentReviewSession.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Talent review sessions already exist, skipping...')
            return

        today = date.today()
        sessions = [
            ('Q4 2025 Talent Review', 'scheduled'),
            ('Q3 2025 Calibration', 'completed'),
            ('Annual Talent Review 2025', 'in_progress'),
        ]

        for name, status in sessions:
            session = TalentReviewSession.all_objects.create(
                tenant=tenant,
                name=name,
                review_period_start=today - timedelta(days=90),
                review_period_end=today,
                session_date=today - timedelta(days=random.randint(0, 30)),
                status=status,
                facilitator=employees[0] if employees else None,
                description=f'{name} - talent calibration session.',
            )

            # Add participants
            for emp in random.sample(employees, min(5, len(employees))):
                perf = random.randint(1, 5)
                pot = random.randint(1, 5)
                TalentReviewParticipant.all_objects.create(
                    tenant=tenant,
                    session=session,
                    employee=emp,
                    initial_performance_rating=perf,
                    initial_potential_rating=pot,
                    calibrated_performance_rating=perf if status == 'completed' else None,
                    calibrated_potential_rating=pot if status == 'completed' else None,
                    calibration_notes='Discussed performance trajectory.' if status == 'completed' else '',
                )

        self.stdout.write(f'  Created {len(sessions)} talent review sessions with participants.')

    def _seed_retention(self, tenant, employees):
        if FlightRiskAssessment.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Flight risk assessments already exist, skipping...')
            return

        today = date.today()
        risk_levels = ['critical', 'high', 'medium', 'low']
        risk_factors_list = [
            'Compensation below market rate, limited growth opportunities',
            'Approached by competitor, expressing dissatisfaction',
            'No recent promotion, team dynamics issues',
            'Relocation challenges, work-life balance concerns',
        ]

        assessments = []
        for i, emp in enumerate(employees[:6]):
            assessment = FlightRiskAssessment.all_objects.create(
                tenant=tenant,
                employee=emp,
                risk_level=risk_levels[i % len(risk_levels)],
                risk_factors=risk_factors_list[i % len(risk_factors_list)],
                impact_if_lost=f'High impact - key contributor in team.',
                assessed_date=today - timedelta(days=random.randint(0, 60)),
                assessed_by=employees[0],
                is_active=True,
            )
            assessments.append(assessment)

        # Create retention plans for high-risk employees
        action_descriptions = [
            'Schedule 1:1 with VP',
            'Propose salary adjustment',
            'Assign to high-visibility project',
            'Offer flexible work arrangement',
            'Enroll in leadership program',
        ]

        for assessment in assessments[:3]:
            plan = RetentionPlan.all_objects.create(
                tenant=tenant,
                employee=assessment.employee,
                flight_risk=assessment,
                title=f'Retention Plan - {assessment.employee.first_name}',
                description='Comprehensive retention strategy to address identified risk factors.',
                responsible_person=employees[0],
                target_date=today + timedelta(days=random.randint(30, 90)),
                status=random.choice(['planned', 'in_progress']),
            )

            # Add actions
            for desc in random.sample(action_descriptions, 3):
                RetentionAction.all_objects.create(
                    tenant=tenant,
                    retention_plan=plan,
                    description=desc,
                    assigned_to=random.choice(employees[:3]),
                    due_date=today + timedelta(days=random.randint(7, 45)),
                    status=random.choice(['pending', 'in_progress', 'completed']),
                )

        self.stdout.write(f'  Created {len(assessments)} flight risk assessments with retention plans.')
