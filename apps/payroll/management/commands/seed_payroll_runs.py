"""
Seed sample data for Payroll Periods, Salary Holds, and Salary Revisions.
Requires: employees, pay components, and employee salary assignments to exist.

Usage:
    python manage.py seed_payroll_runs
    python manage.py seed_payroll_runs --clear   # Clear & re-seed
"""
import random
from datetime import timedelta, date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.core.models import Tenant, set_current_tenant
from apps.employees.models import Employee
from apps.payroll.models import (
    PayComponent, SalaryStructure,
    EmployeeSalaryStructure, EmployeeSalaryComponent,
    PayrollPeriod, PayrollEntry, PayrollEntryComponent,
    SalaryHold, SalaryRevision,
)

fake = Faker('en_IN')

HOLD_REASONS = [
    'Pending background verification – documents submitted are under review.',
    'Employee has an outstanding loan balance from the company.',
    'Disciplinary inquiry in progress – salary held per HR policy.',
    'Notice period not served – clearance pending from reporting manager.',
    'Assets not returned – company laptop and ID card pending.',
    'Incorrect bank details – awaiting updated bank account information.',
    'Tax declaration not submitted – TDS cannot be computed.',
    'Probation review pending – salary increment on hold.',
    'Inter-department transfer in progress – budget reallocation pending.',
    'Attendance discrepancy under investigation for the current month.',
]

REVISION_REASONS = [
    'Annual appraisal – performance rating: Exceeds Expectations.',
    'Mid-year correction – market salary benchmarking adjustment.',
    'Promotion to Senior role – effective from new financial year.',
    'Role change: moved from individual contributor to team lead.',
    'Annual increment as per company compensation policy.',
    'Counter-offer retention package approved by VP-HR.',
    'Grade change from L4 to L5 – salary band realignment.',
    'Post-probation confirmation – revised from trainee CTC.',
    'Special adjustment – critical skill retention bonus included.',
    'Lateral move to new department with revised compensation.',
]


class Command(BaseCommand):
    help = 'Seed Payroll Periods, Salary Holds, and Salary Revisions with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete existing periods, holds, and revisions before seeding',
        )

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR(
                'No tenants found. Run "python manage.py seed_data" first.'
            ))
            return

        if options['clear']:
            self._clear_data()

        self.stdout.write('Seeding Payroll Periods, Salary Holds & Salary Revisions...\n')

        for tenant in tenants:
            set_current_tenant(tenant)
            self.stdout.write(f'  Tenant: {tenant.name}')

            employees = list(Employee.all_objects.filter(
                tenant=tenant, status='active'))

            if not employees:
                self.stdout.write(self.style.WARNING(
                    '    Skipping - no active employees found'))
                continue

            # Find managers
            managers = [e for e in employees
                        if e.designation and e.designation.job_grade
                        and e.designation.job_grade.level >= 5]
            if not managers:
                managers = employees[:3]

            # Get salary assignments
            assignments = list(EmployeeSalaryStructure.all_objects.filter(
                tenant=tenant, status='active'))
            if not assignments:
                self.stdout.write(self.style.WARNING(
                    '    Skipping - no salary assignments found. '
                    'Run "python manage.py seed_payroll" first.'))
                continue

            pay_components = list(PayComponent.all_objects.filter(tenant=tenant))
            structures = list(SalaryStructure.all_objects.filter(
                tenant=tenant, is_active=True))

            # 1. Payroll Periods
            periods = self._create_payroll_periods(
                tenant, employees, assignments, pay_components, managers)
            self.stdout.write(
                f'    Created {len(periods)} payroll periods with entries')

            # 2. Salary Holds
            hold_count = self._create_salary_holds(
                tenant, employees, periods, managers)
            self.stdout.write(f'    Created {hold_count} salary holds')

            # 3. Salary Revisions
            rev_count = self._create_salary_revisions(
                tenant, employees, assignments, structures,
                pay_components, managers)
            self.stdout.write(f'    Created {rev_count} salary revisions')

            self.stdout.write(self.style.SUCCESS(
                f'    Completed: {tenant.name}\n'))

        set_current_tenant(None)
        self.stdout.write(self.style.SUCCESS(
            '\nPayroll runs data seeded successfully!'))

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------
    def _clear_data(self):
        self.stdout.write('Clearing existing data...')
        for model in [SalaryRevision, SalaryHold,
                       PayrollEntryComponent, PayrollEntry, PayrollPeriod]:
            count = model.all_objects.all().delete()[0]
            if count:
                self.stdout.write(f'  Deleted {count} {model.__name__} records')
        self.stdout.write('')

    # ------------------------------------------------------------------
    # Payroll Periods (12 months)
    # ------------------------------------------------------------------
    def _create_payroll_periods(self, tenant, employees, assignments,
                                 pay_components, managers):
        periods = []
        today = date.today()

        emp_salary_map = {}
        for assignment in assignments:
            emp_salary_map[assignment.employee_id] = assignment

        # Create payroll periods for the last 12 months
        for month_offset in range(12, 0, -1):
            period_date = today.replace(day=15) - timedelta(days=month_offset * 30)
            month = period_date.month
            year = period_date.year
            month_name = period_date.strftime('%B')

            # Check if already exists
            if PayrollPeriod.all_objects.filter(
                    tenant=tenant, month=month, year=year).exists():
                existing = PayrollPeriod.all_objects.get(
                    tenant=tenant, month=month, year=year)
                periods.append(existing)
                continue

            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            start_date = date(year, month, 1)
            payment_date = end_date + timedelta(days=1)

            # Status progression: older = paid, recent = in progress
            if month_offset >= 6:
                period_status = 'paid'
            elif month_offset >= 4:
                period_status = 'approved'
            elif month_offset == 3:
                period_status = 'processed'
            elif month_offset == 2:
                period_status = 'processing'
            else:
                period_status = 'draft'

            period = PayrollPeriod.objects.create(
                tenant=tenant,
                name=f'{month_name} {year}',
                month=month,
                year=year,
                start_date=start_date,
                end_date=end_date,
                payment_date=payment_date if period_status == 'paid' else None,
                status=period_status,
                employee_count=len(employees),
                processed_by=(
                    random.choice(managers)
                ) if period_status not in ('draft',) else None,
                processed_at=(
                    timezone.now() - timedelta(days=month_offset * 30)
                ) if period_status not in ('draft',) else None,
                approved_by=(
                    random.choice(managers)
                ) if period_status in ('approved', 'paid') else None,
                approved_at=(
                    timezone.now() - timedelta(days=month_offset * 30 - 3)
                ) if period_status in ('approved', 'paid') else None,
                remarks=f'Payroll for {month_name} {year}',
            )

            # Create entries for each employee
            total_gross = Decimal('0')
            total_deductions = Decimal('0')
            total_net = Decimal('0')

            for emp in employees:
                emp_sal = emp_salary_map.get(emp.id)
                if not emp_sal:
                    continue

                gross = emp_sal.gross_salary or Decimal('0')
                deduction_total = Decimal('0')
                emp_components = list(
                    EmployeeSalaryComponent.all_objects.filter(
                        tenant=tenant, employee_salary=emp_sal))

                for ec in emp_components:
                    if ec.pay_component.component_type == 'deduction':
                        deduction_total += ec.monthly_amount

                net_pay = gross - deduction_total
                days_in_month = (end_date - start_date).days + 1
                days_present = days_in_month - random.randint(0, 4)
                days_absent = days_in_month - days_present
                lop_days = Decimal(str(max(0, days_absent - 1)))
                lop_amount = Decimal('0')
                if days_in_month > 0:
                    lop_amount = (
                        gross / days_in_month * lop_days
                    ).quantize(Decimal('0.01'))

                # Variety: bonus/arrears for some paid months
                bonus_amount = Decimal('0')
                arrears_amount = Decimal('0')
                if period_status == 'paid':
                    if random.random() < 0.12:
                        bonus_amount = Decimal(
                            str(random.randint(2000, 15000)))
                    if random.random() < 0.08:
                        arrears_amount = Decimal(
                            str(random.randint(1000, 8000)))

                # Map period status to entry status
                entry_status_map = {
                    'draft': 'draft',
                    'processing': 'draft',
                    'processed': 'calculated',
                    'approved': 'approved',
                    'paid': 'paid',
                }
                entry_status = entry_status_map.get(period_status, 'draft')

                entry_net = (
                    net_pay - lop_amount + bonus_amount + arrears_amount
                ).quantize(Decimal('0.01'))

                entry = PayrollEntry.objects.create(
                    tenant=tenant,
                    payroll_period=period,
                    employee=emp,
                    employee_salary=emp_sal,
                    gross_earnings=gross,
                    total_deductions=deduction_total.quantize(Decimal('0.01')),
                    net_pay=entry_net,
                    days_payable=days_in_month,
                    days_present=days_present,
                    days_absent=days_absent,
                    lop_days=lop_days,
                    lop_amount=lop_amount,
                    bonus_amount=bonus_amount,
                    arrears_amount=arrears_amount,
                    status=entry_status,
                )

                # Create entry components
                for ec in emp_components:
                    PayrollEntryComponent.objects.create(
                        tenant=tenant,
                        payroll_entry=entry,
                        pay_component=ec.pay_component,
                        amount=ec.monthly_amount,
                    )

                total_gross += gross
                total_deductions += deduction_total
                total_net += (net_pay - lop_amount + bonus_amount
                              + arrears_amount)

            period.total_gross = total_gross.quantize(Decimal('0.01'))
            period.total_deductions = total_deductions.quantize(Decimal('0.01'))
            period.total_net = total_net.quantize(Decimal('0.01'))
            period.save()

            periods.append(period)

        return periods

    # ------------------------------------------------------------------
    # Salary Holds (8-12 records with variety)
    # ------------------------------------------------------------------
    def _create_salary_holds(self, tenant, employees, periods, managers):
        count = 0
        if len(employees) < 3 or not periods:
            return count

        # Create 8-12 salary holds across different periods
        num_holds = min(random.randint(8, 12), len(employees))
        held_employees = random.sample(employees, num_holds)

        for emp in held_employees:
            existing = SalaryHold.all_objects.filter(
                tenant=tenant, employee=emp).exists()
            if existing:
                continue

            reason = random.choice(HOLD_REASONS)
            is_released = random.random() < 0.5

            hold = SalaryHold.objects.create(
                tenant=tenant,
                employee=emp,
                payroll_period=(
                    random.choice(periods)
                    if random.random() < 0.75 else None
                ),
                reason=reason,
                held_by=random.choice(managers),
                status='released' if is_released else 'active',
                released_by=(
                    random.choice(managers)
                ) if is_released else None,
                released_at=(
                    timezone.now() - timedelta(days=random.randint(1, 30))
                ) if is_released else None,
                release_remarks=(
                    random.choice([
                        'All pending items cleared. Salary released.',
                        'Background verification completed successfully.',
                        'Assets returned and clearance obtained.',
                        'Bank details updated and verified.',
                        'Disciplinary matter resolved. No action required.',
                        'Tax documents received. TDS recomputed.',
                        'Manager approved release after review.',
                        'Probation confirmed. Salary released with increment.',
                    ])
                ) if is_released else '',
            )
            count += 1

        return count

    # ------------------------------------------------------------------
    # Salary Revisions (10-15 records with variety)
    # ------------------------------------------------------------------
    def _create_salary_revisions(self, tenant, employees, assignments,
                                   structures, pay_components, managers):
        count = 0
        if len(employees) < 5 or not structures:
            return count

        emp_salary_map = {a.employee_id: a for a in assignments}

        # Create 10-15 salary revisions
        num_revisions = min(random.randint(10, 15), len(employees))
        revised_employees = random.sample(employees, num_revisions)

        statuses = ['draft', 'pending', 'approved', 'rejected', 'applied']
        status_weights = [0.10, 0.20, 0.25, 0.10, 0.35]

        # Spread effective dates across different months
        effective_dates = [
            date(2025, 4, 1),   # April (FY start)
            date(2025, 7, 1),   # July (mid-year)
            date(2025, 10, 1),  # October (Q3)
            date(2026, 1, 1),   # January
            date(2026, 4, 1),   # April (next FY)
        ]

        for emp in revised_employees:
            existing = SalaryRevision.all_objects.filter(
                tenant=tenant, employee=emp).exists()
            if existing:
                continue

            old_assignment = emp_salary_map.get(emp.id)
            if not old_assignment:
                continue

            old_ctc = old_assignment.ctc
            if not old_ctc or old_ctc <= 0:
                continue

            # Hike between 5-30%
            hike_pct = Decimal(str(random.randint(5, 30))) / Decimal('100')
            new_ctc = (old_ctc * (1 + hike_pct)).quantize(Decimal('0.01'))

            status = random.choices(statuses, weights=status_weights, k=1)[0]
            effective_from = random.choice(effective_dates)
            revision_date = effective_from - timedelta(
                days=random.randint(15, 60))

            arrears_amount = Decimal('0')
            new_assignment = None

            if status == 'applied':
                # Create a new salary assignment for applied revisions
                arrears_months = random.randint(1, 4)
                monthly_diff = (new_ctc - old_ctc) / 12
                arrears_amount = (
                    monthly_diff * arrears_months
                ).quantize(Decimal('0.01'))

                # Pick appropriate structure
                if structures:
                    if new_ctc < Decimal('500000'):
                        structure = structures[0]
                    elif new_ctc < Decimal('1000000') and len(structures) > 1:
                        structure = structures[1]
                    elif len(structures) > 2:
                        structure = structures[2]
                    else:
                        structure = structures[-1]
                else:
                    continue

                monthly_ctc = new_ctc / 12
                basic = monthly_ctc * Decimal('0.40')
                hra = basic * Decimal('0.50')
                da = basic * Decimal('0.05')
                lta = basic * Decimal('0.10')
                conv = Decimal('1600')
                med = Decimal('1250')
                gross = basic + hra + da + lta + conv + med
                pf_er = min(basic * Decimal('0.12'), Decimal('1800'))
                esi_er = (
                    gross * Decimal('0.0325')
                    if gross <= Decimal('21000') else Decimal('0')
                )
                special = monthly_ctc - gross - pf_er - esi_er
                if special < 0:
                    special = Decimal('0')
                gross += special
                pf_ee = min(basic * Decimal('0.12'), Decimal('1800'))
                esi_ee = (
                    gross * Decimal('0.0075')
                    if gross <= Decimal('21000') else Decimal('0')
                )
                pt = Decimal('200')
                net = gross - pf_ee - esi_ee - pt

                new_assignment = EmployeeSalaryStructure.objects.create(
                    tenant=tenant,
                    employee=emp,
                    salary_structure=structure,
                    ctc=new_ctc,
                    gross_salary=gross.quantize(Decimal('0.01')),
                    net_salary=net.quantize(Decimal('0.01')),
                    effective_from=effective_from,
                    status='active',
                    remarks=(
                        f'Revised CTC after appraisal – '
                        f'{hike_pct * 100:.0f}% hike'
                    ),
                )

                # Mark old assignment as revised
                old_assignment.status = 'revised'
                old_assignment.effective_to = (
                    effective_from - timedelta(days=1)
                )
                old_assignment.save()

                # Create components for new assignment
                component_amounts = {
                    'BASIC': basic, 'HRA': hra, 'DA': da,
                    'SPECIAL': special, 'CONV': conv, 'MED': med,
                    'LTA': lta, 'PF_EE': pf_ee, 'PF_ER': pf_er,
                    'ESI_EE': esi_ee, 'ESI_ER': esi_er,
                    'PT': pt, 'TDS': Decimal('0'),
                }
                for comp in pay_components:
                    monthly_amt = component_amounts.get(
                        comp.code, Decimal('0'))
                    EmployeeSalaryComponent.objects.create(
                        tenant=tenant,
                        employee_salary=new_assignment,
                        pay_component=comp,
                        monthly_amount=monthly_amt.quantize(Decimal('0.01')),
                        annual_amount=(
                            monthly_amt * 12
                        ).quantize(Decimal('0.01')),
                        is_overridden=False,
                    )

            SalaryRevision.objects.create(
                tenant=tenant,
                employee=emp,
                old_salary_structure=old_assignment,
                new_salary_structure=new_assignment,
                old_ctc=old_ctc,
                new_ctc=new_ctc,
                effective_from=effective_from,
                revision_date=revision_date,
                arrears_from=(
                    effective_from - timedelta(days=90)
                ) if arrears_amount > 0 else None,
                arrears_amount=arrears_amount,
                reason=random.choice(REVISION_REASONS),
                status=status,
                approved_by=(
                    random.choice(managers)
                ) if status in ('approved', 'applied') else None,
                approved_at=(
                    timezone.now() - timedelta(days=random.randint(1, 30))
                ) if status in ('approved', 'applied') else None,
            )
            count += 1

        return count
