import random
from datetime import timedelta, date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.core.models import Tenant, set_current_tenant
from apps.employees.models import Employee
from apps.organization.models import JobGrade
from apps.payroll.models import (
    PayComponent, SalaryStructure, SalaryStructureComponent,
    EmployeeSalaryStructure, EmployeeSalaryComponent,
    PayrollPeriod, PayrollEntry, PayrollEntryComponent,
    SalaryHold, SalaryRevision,
    PFConfiguration, ESIConfiguration, ProfessionalTaxSlab,
    LWFConfiguration, StatutoryContribution,
    TaxRegimeChoice, InvestmentDeclaration,
    BankFile, Payslip, PaymentRegister, Reimbursement,
)

fake = Faker()

# ---------------------------------------------------------------------------
# Pay component definitions (Indian payroll standard)
# ---------------------------------------------------------------------------

PAY_COMPONENTS = [
    # Earnings
    {
        'name': 'Basic', 'code': 'BASIC',
        'component_type': 'earning', 'category': 'basic',
        'calculation_type': 'percent_of_ctc', 'default_value': Decimal('40.00'),
        'is_taxable': True, 'is_statutory': False, 'display_order': 1,
        'description': 'Basic salary - 40% of CTC',
    },
    {
        'name': 'House Rent Allowance', 'code': 'HRA',
        'component_type': 'earning', 'category': 'hra',
        'calculation_type': 'percent_of_basic', 'default_value': Decimal('50.00'),
        'is_taxable': True, 'is_statutory': False, 'display_order': 2,
        'description': 'HRA - 50% of Basic',
    },
    {
        'name': 'Dearness Allowance', 'code': 'DA',
        'component_type': 'earning', 'category': 'da',
        'calculation_type': 'percent_of_basic', 'default_value': Decimal('5.00'),
        'is_taxable': True, 'is_statutory': False, 'display_order': 3,
        'description': 'DA - 5% of Basic',
    },
    {
        'name': 'Special Allowance', 'code': 'SPECIAL',
        'component_type': 'earning', 'category': 'special',
        'calculation_type': 'fixed', 'default_value': Decimal('0.00'),
        'is_taxable': True, 'is_statutory': False, 'display_order': 4,
        'description': 'Special allowance - balancing component',
    },
    {
        'name': 'Conveyance Allowance', 'code': 'CONV',
        'component_type': 'earning', 'category': 'conveyance',
        'calculation_type': 'fixed', 'default_value': Decimal('1600.00'),
        'is_taxable': True, 'is_statutory': False, 'display_order': 5,
        'description': 'Monthly conveyance allowance',
    },
    {
        'name': 'Medical Allowance', 'code': 'MED',
        'component_type': 'earning', 'category': 'medical',
        'calculation_type': 'fixed', 'default_value': Decimal('1250.00'),
        'is_taxable': True, 'is_statutory': False, 'display_order': 6,
        'description': 'Monthly medical allowance',
    },
    {
        'name': 'Leave Travel Allowance', 'code': 'LTA',
        'component_type': 'earning', 'category': 'lta',
        'calculation_type': 'percent_of_basic', 'default_value': Decimal('10.00'),
        'is_taxable': True, 'is_statutory': False, 'display_order': 7,
        'description': 'LTA - 10% of Basic',
    },
    # Deductions
    {
        'name': 'PF (Employee)', 'code': 'PF_EE',
        'component_type': 'deduction', 'category': 'pf_employee',
        'calculation_type': 'percent_of_basic', 'default_value': Decimal('12.00'),
        'is_taxable': False, 'is_statutory': True, 'display_order': 10,
        'description': 'Employee provident fund contribution - 12% of Basic (max 15000)',
    },
    {
        'name': 'PF (Employer)', 'code': 'PF_ER',
        'component_type': 'deduction', 'category': 'pf_employer',
        'calculation_type': 'percent_of_basic', 'default_value': Decimal('12.00'),
        'is_taxable': False, 'is_statutory': True, 'display_order': 11,
        'description': 'Employer provident fund contribution - 12% of Basic (max 15000)',
    },
    {
        'name': 'ESI (Employee)', 'code': 'ESI_EE',
        'component_type': 'deduction', 'category': 'esi_employee',
        'calculation_type': 'percent_of_gross', 'default_value': Decimal('0.75'),
        'is_taxable': False, 'is_statutory': True, 'display_order': 12,
        'description': 'Employee ESI contribution - 0.75% of Gross',
    },
    {
        'name': 'ESI (Employer)', 'code': 'ESI_ER',
        'component_type': 'deduction', 'category': 'esi_employer',
        'calculation_type': 'percent_of_gross', 'default_value': Decimal('3.25'),
        'is_taxable': False, 'is_statutory': True, 'display_order': 13,
        'description': 'Employer ESI contribution - 3.25% of Gross',
    },
    {
        'name': 'Professional Tax', 'code': 'PT',
        'component_type': 'deduction', 'category': 'professional_tax',
        'calculation_type': 'fixed', 'default_value': Decimal('200.00'),
        'is_taxable': False, 'is_statutory': True, 'display_order': 14,
        'description': 'State professional tax (Maharashtra)',
    },
    {
        'name': 'TDS', 'code': 'TDS',
        'component_type': 'deduction', 'category': 'tds',
        'calculation_type': 'fixed', 'default_value': Decimal('0.00'),
        'is_taxable': False, 'is_statutory': True, 'display_order': 15,
        'description': 'Tax deducted at source - computed from tax projection',
    },
]

# ---------------------------------------------------------------------------
# Salary structure definitions
# ---------------------------------------------------------------------------

SALARY_STRUCTURES = [
    {'name': 'Standard Structure - Junior', 'code': 'SS-JR', 'base_amount': Decimal('400000')},
    {'name': 'Standard Structure - Mid-Level', 'code': 'SS-ML', 'base_amount': Decimal('800000')},
    {'name': 'Standard Structure - Senior', 'code': 'SS-SR', 'base_amount': Decimal('1500000')},
]

# ---------------------------------------------------------------------------
# Reimbursement claim samples
# ---------------------------------------------------------------------------

REIMBURSEMENT_SAMPLES = [
    {'category': 'medical', 'description': 'Annual health check-up at Apollo Hospital', 'amount': Decimal('5500.00')},
    {'category': 'fuel', 'description': 'Fuel expenses for client site visits - January', 'amount': Decimal('3200.00')},
    {'category': 'mobile', 'description': 'Mobile recharge and broadband bill - Q3', 'amount': Decimal('4500.00')},
    {'category': 'books', 'description': 'Technical books and O\'Reilly subscription', 'amount': Decimal('2800.00')},
    {'category': 'lta', 'description': 'Travel to hometown for annual vacation', 'amount': Decimal('15000.00')},
]


class Command(BaseCommand):
    help = 'Seed the database with payroll module data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR(
                'No tenants found. Run "python manage.py seed_data" first.'
            ))
            return

        self.stdout.write('Seeding payroll data...\n')

        for tenant in tenants:
            set_current_tenant(tenant)
            self.stdout.write(f'  Tenant: {tenant.name}')

            employees = list(Employee.all_objects.filter(
                tenant=tenant, status='active'))
            job_grades = list(JobGrade.all_objects.filter(tenant=tenant))

            if not employees:
                self.stdout.write(self.style.WARNING(
                    '    Skipping - no active employees found'
                ))
                continue

            # 1. Pay Components
            pay_components = self._create_pay_components(tenant)
            self.stdout.write(f'    Created {len(pay_components)} pay components')

            # 2. Salary Structures
            structures = self._create_salary_structures(tenant, job_grades)
            self.stdout.write(f'    Created {len(structures)} salary structures')

            # 3. Salary Structure Components
            ssc_count = self._create_structure_components(
                tenant, structures, pay_components)
            self.stdout.write(f'    Created {ssc_count} salary structure components')

            # 4. Employee Salary Assignments
            assignments = self._create_employee_salary_assignments(
                tenant, employees, structures, pay_components)
            self.stdout.write(f'    Created {len(assignments)} employee salary assignments')

            # 5. PF Configuration
            self._create_pf_configuration(tenant)
            self.stdout.write('    Created PF configuration')

            # 6. ESI Configuration
            self._create_esi_configuration(tenant)
            self.stdout.write('    Created ESI configuration')

            # 7. Professional Tax Slabs
            pt_slabs = self._create_pt_slabs(tenant)
            self.stdout.write(f'    Created {len(pt_slabs)} professional tax slabs')

            # 8. LWF Configuration
            self._create_lwf_configuration(tenant)
            self.stdout.write('    Created LWF configuration')

            # 9. Payroll Periods & Entries
            periods = self._create_payroll_periods(
                tenant, employees, assignments, pay_components)
            self.stdout.write(f'    Created {len(periods)} payroll periods with entries')

            # 10. Tax Regime Choices
            regime_count = self._create_tax_regime_choices(tenant, employees)
            self.stdout.write(f'    Created {regime_count} tax regime choices')

            # 11. Reimbursements
            reimb_count = self._create_reimbursements(tenant, employees)
            self.stdout.write(f'    Created {reimb_count} reimbursement claims')

            self.stdout.write(f'    Completed: {tenant.name}\n')

        set_current_tenant(None)
        self.stdout.write(self.style.SUCCESS(
            '\nPayroll data seeded successfully!'))

    # ------------------------------------------------------------------
    # Pay Components
    # ------------------------------------------------------------------
    def _create_pay_components(self, tenant):
        components = []
        for data in PAY_COMPONENTS:
            comp, _ = PayComponent.objects.get_or_create(
                tenant=tenant,
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'component_type': data['component_type'],
                    'category': data['category'],
                    'calculation_type': data['calculation_type'],
                    'default_value': data['default_value'],
                    'is_taxable': data['is_taxable'],
                    'is_statutory': data['is_statutory'],
                    'is_active': True,
                    'display_order': data['display_order'],
                    'description': data['description'],
                },
            )
            components.append(comp)
        return components

    # ------------------------------------------------------------------
    # Salary Structures
    # ------------------------------------------------------------------
    def _create_salary_structures(self, tenant, job_grades):
        structures = []
        # Try to link structures to job grades by level if available
        grade_map = {
            0: None,  # Junior: link to lowest grades
            1: None,  # Mid: link to mid grades
            2: None,  # Senior: link to highest grades
        }
        if job_grades:
            sorted_grades = sorted(job_grades, key=lambda g: g.level)
            third = max(1, len(sorted_grades) // 3)
            grade_map[0] = sorted_grades[0]
            grade_map[1] = sorted_grades[min(third, len(sorted_grades) - 1)]
            grade_map[2] = sorted_grades[min(third * 2, len(sorted_grades) - 1)]

        for idx, data in enumerate(SALARY_STRUCTURES):
            structure, _ = SalaryStructure.objects.get_or_create(
                tenant=tenant,
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'job_grade': grade_map.get(idx),
                    'base_amount': data['base_amount'],
                    'is_active': True,
                    'description': f"Standard salary structure with base CTC of {data['base_amount']:,.0f}",
                },
            )
            structures.append(structure)
        return structures

    # ------------------------------------------------------------------
    # Salary Structure Components
    # ------------------------------------------------------------------
    def _create_structure_components(self, tenant, structures, pay_components):
        count = 0
        for structure in structures:
            for comp in pay_components:
                _, created = SalaryStructureComponent.objects.get_or_create(
                    tenant=tenant,
                    salary_structure=structure,
                    pay_component=comp,
                    defaults={
                        'calculation_type': comp.calculation_type,
                        'value': comp.default_value,
                    },
                )
                if created:
                    count += 1
        return count

    # ------------------------------------------------------------------
    # Employee Salary Assignments
    # ------------------------------------------------------------------
    def _create_employee_salary_assignments(self, tenant, employees,
                                             structures, pay_components):
        assignments = []

        for emp in employees:
            # Check if employee already has an active salary assignment
            existing = EmployeeSalaryStructure.all_objects.filter(
                tenant=tenant, employee=emp, status='active').first()
            if existing:
                assignments.append(existing)
                continue

            # Determine CTC from employee salary or random
            annual_salary = emp.salary or Decimal(str(random.randint(300000, 2000000)))
            ctc = annual_salary

            # Pick structure based on CTC range
            if ctc < Decimal('500000'):
                structure = structures[0]  # Junior
            elif ctc < Decimal('1000000'):
                structure = structures[1]  # Mid-Level
            else:
                structure = structures[2]  # Senior

            effective_from = emp.date_of_joining or date(2024, 4, 1)

            # Calculate gross and net
            monthly_ctc = ctc / 12
            basic_monthly = monthly_ctc * Decimal('0.40')
            hra_monthly = basic_monthly * Decimal('0.50')
            da_monthly = basic_monthly * Decimal('0.05')
            lta_monthly = basic_monthly * Decimal('0.10')
            conv_monthly = Decimal('1600.00')
            med_monthly = Decimal('1250.00')

            gross_monthly = (
                basic_monthly + hra_monthly + da_monthly
                + lta_monthly + conv_monthly + med_monthly
            )
            # Special allowance = CTC/12 - gross - employer contributions
            pf_employer = min(basic_monthly * Decimal('0.12'), Decimal('1800'))
            esi_employer = (
                gross_monthly * Decimal('0.0325')
                if gross_monthly <= Decimal('21000') else Decimal('0')
            )
            special_monthly = monthly_ctc - gross_monthly - pf_employer - esi_employer
            if special_monthly < 0:
                special_monthly = Decimal('0')
            gross_monthly += special_monthly

            # Deductions
            pf_employee = min(basic_monthly * Decimal('0.12'), Decimal('1800'))
            esi_employee = (
                gross_monthly * Decimal('0.0075')
                if gross_monthly <= Decimal('21000') else Decimal('0')
            )
            pt = Decimal('200')
            total_deductions = pf_employee + esi_employee + pt
            net_monthly = gross_monthly - total_deductions

            emp_salary = EmployeeSalaryStructure.objects.create(
                tenant=tenant,
                employee=emp,
                salary_structure=structure,
                ctc=ctc,
                gross_salary=gross_monthly.quantize(Decimal('0.01')),
                net_salary=net_monthly.quantize(Decimal('0.01')),
                effective_from=effective_from,
                status='active',
                remarks=f'Auto-assigned by payroll seeder',
            )

            # Create EmployeeSalaryComponent records
            component_amounts = {
                'BASIC': basic_monthly,
                'HRA': hra_monthly,
                'DA': da_monthly,
                'SPECIAL': special_monthly,
                'CONV': conv_monthly,
                'MED': med_monthly,
                'LTA': lta_monthly,
                'PF_EE': pf_employee,
                'PF_ER': pf_employer,
                'ESI_EE': esi_employee,
                'ESI_ER': esi_employer,
                'PT': pt,
                'TDS': Decimal('0'),
            }

            for comp in pay_components:
                monthly_amt = component_amounts.get(comp.code, Decimal('0'))
                annual_amt = monthly_amt * 12
                EmployeeSalaryComponent.objects.create(
                    tenant=tenant,
                    employee_salary=emp_salary,
                    pay_component=comp,
                    monthly_amount=monthly_amt.quantize(Decimal('0.01')),
                    annual_amount=annual_amt.quantize(Decimal('0.01')),
                    is_overridden=False,
                )

            assignments.append(emp_salary)

        return assignments

    # ------------------------------------------------------------------
    # PF Configuration
    # ------------------------------------------------------------------
    def _create_pf_configuration(self, tenant):
        PFConfiguration.objects.get_or_create(
            tenant=tenant,
            effective_from=date(2024, 4, 1),
            defaults={
                'pf_number': f'MH/{fake.bothify("???").upper()}/{fake.numerify("#####")}/000/{fake.numerify("#######")}',
                'employee_contribution_rate': Decimal('12.00'),
                'employer_contribution_rate': Decimal('12.00'),
                'eps_rate': Decimal('8.33'),
                'admin_charge_rate': Decimal('0.50'),
                'edli_rate': Decimal('0.50'),
                'pf_ceiling': Decimal('15000.00'),
                'is_active': True,
            },
        )

    # ------------------------------------------------------------------
    # ESI Configuration
    # ------------------------------------------------------------------
    def _create_esi_configuration(self, tenant):
        ESIConfiguration.objects.get_or_create(
            tenant=tenant,
            effective_from=date(2024, 4, 1),
            defaults={
                'esi_number': fake.numerify('##-##-######-###-####'),
                'employee_rate': Decimal('0.75'),
                'employer_rate': Decimal('3.25'),
                'wage_ceiling': Decimal('21000.00'),
                'is_active': True,
            },
        )

    # ------------------------------------------------------------------
    # Professional Tax Slabs (Maharashtra)
    # ------------------------------------------------------------------
    def _create_pt_slabs(self, tenant):
        slabs = []
        slab_data = [
            (Decimal('0'), Decimal('7500'), Decimal('0')),
            (Decimal('7501'), Decimal('10000'), Decimal('175')),
            (Decimal('10001'), Decimal('999999'), Decimal('200')),
        ]
        for salary_from, salary_to, tax_amount in slab_data:
            slab, _ = ProfessionalTaxSlab.objects.get_or_create(
                tenant=tenant,
                state='Maharashtra',
                salary_from=salary_from,
                salary_to=salary_to,
                defaults={
                    'tax_amount': tax_amount,
                    'is_active': True,
                    'effective_from': date(2024, 4, 1),
                },
            )
            slabs.append(slab)
        return slabs

    # ------------------------------------------------------------------
    # LWF Configuration (Maharashtra)
    # ------------------------------------------------------------------
    def _create_lwf_configuration(self, tenant):
        LWFConfiguration.objects.get_or_create(
            tenant=tenant,
            state='Maharashtra',
            defaults={
                'employee_contribution': Decimal('6.00'),
                'employer_contribution': Decimal('18.00'),
                'frequency': 'half_yearly',
                'is_active': True,
                'effective_from': date(2024, 1, 1),
            },
        )

    # ------------------------------------------------------------------
    # Payroll Periods, Entries & Components
    # ------------------------------------------------------------------
    def _create_payroll_periods(self, tenant, employees, assignments,
                                 pay_components):
        periods = []
        today = date.today()

        # Build a lookup from employee to their salary assignment
        emp_salary_map = {}
        for assignment in assignments:
            emp_salary_map[assignment.employee_id] = assignment

        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        # Create payroll periods for the last 3 months
        for month_offset in range(3, 0, -1):
            period_date = today.replace(day=1) - timedelta(days=month_offset * 28)
            month = period_date.month
            year = period_date.year
            month_name = period_date.strftime('%B')

            # Start and end dates of the month
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            start_date = date(year, month, 1)
            payment_date = end_date + timedelta(days=1)  # 1st of next month

            period, created = PayrollPeriod.objects.get_or_create(
                tenant=tenant,
                month=month,
                year=year,
                defaults={
                    'name': f'{month_name} {year}',
                    'start_date': start_date,
                    'end_date': end_date,
                    'payment_date': payment_date,
                    'status': 'paid',
                    'employee_count': len(employees),
                    'processed_by': random.choice(managers),
                    'processed_at': timezone.now() - timedelta(days=month_offset * 28),
                    'approved_by': random.choice(managers),
                    'approved_at': timezone.now() - timedelta(days=month_offset * 28 - 2),
                    'remarks': f'Payroll for {month_name} {year}',
                },
            )

            if created:
                total_gross = Decimal('0')
                total_deductions = Decimal('0')
                total_net = Decimal('0')

                # Create payroll entries for each employee
                for emp in employees:
                    emp_sal = emp_salary_map.get(emp.id)
                    if not emp_sal:
                        continue

                    gross = emp_sal.gross_salary
                    # Gather deduction components
                    deduction_total = Decimal('0')
                    emp_components = list(
                        EmployeeSalaryComponent.all_objects.filter(
                            tenant=tenant, employee_salary=emp_sal))

                    for ec in emp_components:
                        if ec.pay_component.component_type == 'deduction':
                            deduction_total += ec.monthly_amount

                    net_pay = gross - deduction_total
                    days_in_month = (end_date - start_date).days + 1
                    days_present = days_in_month - random.randint(0, 2)
                    days_absent = days_in_month - days_present
                    lop_days = Decimal(str(max(0, days_absent - 1)))
                    lop_amount = (gross / days_in_month * lop_days).quantize(
                        Decimal('0.01'))

                    entry = PayrollEntry.objects.create(
                        tenant=tenant,
                        payroll_period=period,
                        employee=emp,
                        employee_salary=emp_sal,
                        gross_earnings=gross,
                        total_deductions=deduction_total.quantize(Decimal('0.01')),
                        net_pay=(net_pay - lop_amount).quantize(Decimal('0.01')),
                        days_payable=days_in_month,
                        days_present=days_present,
                        days_absent=days_absent,
                        lop_days=lop_days,
                        lop_amount=lop_amount,
                        status='paid',
                    )

                    # Create PayrollEntryComponent for each component
                    for ec in emp_components:
                        PayrollEntryComponent.objects.create(
                            tenant=tenant,
                            payroll_entry=entry,
                            pay_component=ec.pay_component,
                            amount=ec.monthly_amount,
                        )

                    total_gross += gross
                    total_deductions += deduction_total
                    total_net += net_pay - lop_amount

                period.total_gross = total_gross.quantize(Decimal('0.01'))
                period.total_deductions = total_deductions.quantize(Decimal('0.01'))
                period.total_net = total_net.quantize(Decimal('0.01'))
                period.save()

            periods.append(period)

        return periods

    # ------------------------------------------------------------------
    # Tax Regime Choices
    # ------------------------------------------------------------------
    def _create_tax_regime_choices(self, tenant, employees):
        count = 0
        for emp in employees:
            _, created = TaxRegimeChoice.objects.get_or_create(
                tenant=tenant,
                employee=emp,
                financial_year='2025-26',
                defaults={
                    'regime': random.choice(['new', 'new', 'new', 'old']),
                    'locked': False,
                },
            )
            if created:
                count += 1
        return count

    # ------------------------------------------------------------------
    # Reimbursements
    # ------------------------------------------------------------------
    def _create_reimbursements(self, tenant, employees):
        count = 0
        statuses = ['draft', 'submitted', 'approved', 'approved', 'paid']
        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        selected = random.sample(employees, min(5, len(employees)))
        for emp in selected:
            sample = random.choice(REIMBURSEMENT_SAMPLES)
            status = random.choice(statuses)
            claim_date = fake.date_between(start_date='-60d', end_date='today')
            approved_by = random.choice(managers) if status in (
                'approved', 'paid') else None
            approved_at = (
                timezone.now() - timedelta(days=random.randint(1, 15))
            ) if approved_by else None

            approved_amount = sample['amount'] if status in (
                'approved', 'paid') else Decimal('0')

            Reimbursement.objects.create(
                tenant=tenant,
                employee=emp,
                category=sample['category'],
                description=sample['description'],
                amount=sample['amount'],
                approved_amount=approved_amount,
                claim_date=claim_date,
                receipt_date=claim_date - timedelta(days=random.randint(0, 5)),
                status=status,
                approved_by=approved_by,
                approved_at=approved_at,
                rejection_reason='Insufficient documentation.' if status == 'rejected' else '',
            )
            count += 1
        return count
