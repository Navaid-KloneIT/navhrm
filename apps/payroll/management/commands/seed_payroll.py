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
    TaxRegimeChoice, InvestmentDeclaration, TaxComputation,
    BankFile, Payslip, PaymentRegister, Reimbursement,
)

fake = Faker('en_IN')

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
    {'category': 'food', 'description': 'Meal expenses during late night shifts - December', 'amount': Decimal('2100.00')},
    {'category': 'fuel', 'description': 'Cab expenses for weekend deployment support', 'amount': Decimal('4800.00')},
    {'category': 'medical', 'description': 'Dental treatment at Clove Dental', 'amount': Decimal('8500.00')},
    {'category': 'mobile', 'description': 'Postpaid plan upgrade for WFH connectivity', 'amount': Decimal('1200.00')},
    {'category': 'other', 'description': 'Co-working space membership for remote work', 'amount': Decimal('6000.00')},
]

# ---------------------------------------------------------------------------
# Investment declaration templates
# ---------------------------------------------------------------------------

DECLARATION_TEMPLATES = [
    {'section': '80c', 'description': 'PPF contribution for FY 2025-26', 'amount': Decimal('150000.00')},
    {'section': '80c', 'description': 'ELSS Mutual Fund (Axis Long Term Equity)', 'amount': Decimal('50000.00')},
    {'section': '80c', 'description': 'Life Insurance Premium - LIC Jeevan Anand', 'amount': Decimal('35000.00')},
    {'section': '80c', 'description': 'Children tuition fees (2 children)', 'amount': Decimal('80000.00')},
    {'section': '80c', 'description': 'NSC investment', 'amount': Decimal('25000.00')},
    {'section': '80c', 'description': 'Sukanya Samriddhi Yojana deposit', 'amount': Decimal('50000.00')},
    {'section': '80c', 'description': '5-year Tax Saving FD - SBI', 'amount': Decimal('100000.00')},
    {'section': '80d', 'description': 'Health insurance premium - self and family (Star Health)', 'amount': Decimal('25000.00')},
    {'section': '80d', 'description': 'Health insurance for parents (senior citizen)', 'amount': Decimal('50000.00')},
    {'section': '80d', 'description': 'Preventive health check-up', 'amount': Decimal('5000.00')},
    {'section': '80ccd1b', 'description': 'NPS Tier-1 additional contribution', 'amount': Decimal('50000.00')},
    {'section': '80ccd2', 'description': 'Employer NPS contribution (10% of Basic)', 'amount': Decimal('48000.00')},
    {'section': '80e', 'description': 'Education loan interest - MBA from IIM', 'amount': Decimal('85000.00')},
    {'section': '80tta', 'description': 'Savings bank interest (SBI + HDFC)', 'amount': Decimal('10000.00')},
    {'section': '24b', 'description': 'Home loan interest - HDFC Ltd', 'amount': Decimal('200000.00')},
    {'section': 'hra', 'description': 'Rent paid to landlord - Bangalore', 'amount': Decimal('240000.00')},
    {'section': 'hra', 'description': 'Rent paid - Mumbai (Andheri West)', 'amount': Decimal('360000.00')},
    {'section': 'lta', 'description': 'Travel to Kerala with family', 'amount': Decimal('30000.00')},
    {'section': '80g', 'description': 'Donation to PM CARES Fund', 'amount': Decimal('10000.00')},
    {'section': '80g', 'description': 'Donation to CRY (Child Rights and You)', 'amount': Decimal('15000.00')},
]

# ---------------------------------------------------------------------------
# Salary hold reasons
# ---------------------------------------------------------------------------

HOLD_REASONS = [
    'Pending exit clearance - IT assets not returned',
    'Disciplinary inquiry in progress - under investigation',
    'Probation review pending - performance below expectations',
    'Salary account details under verification with bank',
    'Pending background verification completion',
    'Notice period buyout dispute - under HR review',
]

# ---------------------------------------------------------------------------
# Salary revision reasons
# ---------------------------------------------------------------------------

REVISION_REASONS = [
    'Annual appraisal - Exceeded Expectations rating',
    'Annual appraisal - Meets Expectations rating',
    'Promotion to Senior Engineer role',
    'Market correction - retention adjustment',
    'Role change from IC to team lead',
    'Mid-year performance bonus adjustment',
    'Designation upgrade with revised compensation',
]

# ---------------------------------------------------------------------------
# Indian bank details for payment register
# ---------------------------------------------------------------------------

BANK_NAMES = [
    'HDFC Bank', 'ICICI Bank', 'State Bank of India', 'Axis Bank',
    'Kotak Mahindra Bank', 'Yes Bank', 'IndusInd Bank', 'Punjab National Bank',
    'Bank of Baroda', 'Canara Bank', 'Union Bank of India', 'IDBI Bank',
]

IFSC_PREFIXES = {
    'HDFC Bank': 'HDFC0',
    'ICICI Bank': 'ICIC0',
    'State Bank of India': 'SBIN0',
    'Axis Bank': 'UTIB0',
    'Kotak Mahindra Bank': 'KKBK0',
    'Yes Bank': 'YESB0',
    'IndusInd Bank': 'INDB0',
    'Punjab National Bank': 'PUNB0',
    'Bank of Baroda': 'BARB0',
    'Canara Bank': 'CNRB0',
    'Union Bank of India': 'UBIN0',
    'IDBI Bank': 'IBKL0',
}


class Command(BaseCommand):
    help = 'Seed the database with comprehensive payroll module demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing payroll data before seeding',
        )

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR(
                'No tenants found. Run "python manage.py seed_data" first.'
            ))
            return

        if options['clear']:
            self._clear_payroll_data()

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

            managers = [e for e in employees
                        if e.designation and e.designation.job_grade
                        and e.designation.job_grade.level >= 5]
            if not managers:
                managers = employees[:3]

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

            # 7. Professional Tax Slabs (Maharashtra + Karnataka)
            pt_slabs = self._create_pt_slabs(tenant)
            self.stdout.write(f'    Created {len(pt_slabs)} professional tax slabs')

            # 8. LWF Configuration
            self._create_lwf_configuration(tenant)
            self.stdout.write('    Created LWF configuration')

            # 9. Payroll Periods & Entries
            periods = self._create_payroll_periods(
                tenant, employees, assignments, pay_components, managers)
            self.stdout.write(f'    Created {len(periods)} payroll periods with entries')

            # 10. Statutory Contributions
            stat_count = self._create_statutory_contributions(tenant, periods)
            self.stdout.write(f'    Created {stat_count} statutory contribution records')

            # 11. Salary Holds
            hold_count = self._create_salary_holds(
                tenant, employees, periods, managers)
            self.stdout.write(f'    Created {hold_count} salary holds')

            # 12. Salary Revisions
            rev_count = self._create_salary_revisions(
                tenant, employees, assignments, structures,
                pay_components, managers)
            self.stdout.write(f'    Created {rev_count} salary revisions')

            # 13. Tax Regime Choices
            regime_count = self._create_tax_regime_choices(tenant, employees)
            self.stdout.write(f'    Created {regime_count} tax regime choices')

            # 14. Investment Declarations
            decl_count = self._create_investment_declarations(
                tenant, employees, managers)
            self.stdout.write(f'    Created {decl_count} investment declarations')

            # 15. Tax Computations
            tax_count = self._create_tax_computations(
                tenant, employees, assignments)
            self.stdout.write(f'    Created {tax_count} tax computation records')

            # 16. Bank Files
            bf_count = self._create_bank_files(tenant, periods, managers)
            self.stdout.write(f'    Created {bf_count} bank files')

            # 17. Payslips
            slip_count = self._create_payslips(tenant, periods)
            self.stdout.write(f'    Created {slip_count} payslips')

            # 18. Payment Register
            pr_count = self._create_payment_register(tenant, periods)
            self.stdout.write(f'    Created {pr_count} payment register entries')

            # 19. Reimbursements
            reimb_count = self._create_reimbursements(
                tenant, employees, managers)
            self.stdout.write(f'    Created {reimb_count} reimbursement claims')

            self.stdout.write(self.style.SUCCESS(
                f'    Completed: {tenant.name}\n'))

        set_current_tenant(None)
        self.stdout.write(self.style.SUCCESS(
            '\nPayroll data seeded successfully!'))

    # ------------------------------------------------------------------
    # Clear existing data
    # ------------------------------------------------------------------
    def _clear_payroll_data(self):
        self.stdout.write('Clearing existing payroll data...')
        models_to_clear = [
            PaymentRegister, Payslip, BankFile, Reimbursement,
            TaxComputation, InvestmentDeclaration, TaxRegimeChoice,
            StatutoryContribution, SalaryRevision, SalaryHold,
            PayrollEntryComponent, PayrollEntry, PayrollPeriod,
            EmployeeSalaryComponent, EmployeeSalaryStructure,
            SalaryStructureComponent, SalaryStructure, PayComponent,
            PFConfiguration, ESIConfiguration, ProfessionalTaxSlab,
            LWFConfiguration,
        ]
        for model in models_to_clear:
            count = model.all_objects.all().delete()[0]
            if count:
                self.stdout.write(f'  Deleted {count} {model.__name__} records')
        self.stdout.write('')

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
        grade_map = {0: None, 1: None, 2: None}
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
            existing = EmployeeSalaryStructure.all_objects.filter(
                tenant=tenant, employee=emp, status='active').first()
            if existing:
                assignments.append(existing)
                continue

            annual_salary = emp.salary or Decimal(str(random.randint(300000, 2000000)))
            ctc = annual_salary

            if ctc < Decimal('500000'):
                structure = structures[0]
            elif ctc < Decimal('1000000'):
                structure = structures[1]
            else:
                structure = structures[2]

            effective_from = emp.date_of_joining or date(2024, 4, 1)

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
            pf_employer = min(basic_monthly * Decimal('0.12'), Decimal('1800'))
            esi_employer = (
                gross_monthly * Decimal('0.0325')
                if gross_monthly <= Decimal('21000') else Decimal('0')
            )
            special_monthly = monthly_ctc - gross_monthly - pf_employer - esi_employer
            if special_monthly < 0:
                special_monthly = Decimal('0')
            gross_monthly += special_monthly

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
                remarks='Auto-assigned by payroll seeder',
            )

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
    # Professional Tax Slabs (Maharashtra + Karnataka)
    # ------------------------------------------------------------------
    def _create_pt_slabs(self, tenant):
        slabs = []
        slab_data = [
            # Maharashtra
            ('Maharashtra', Decimal('0'), Decimal('7500'), Decimal('0')),
            ('Maharashtra', Decimal('7501'), Decimal('10000'), Decimal('175')),
            ('Maharashtra', Decimal('10001'), Decimal('999999'), Decimal('200')),
            # Karnataka
            ('Karnataka', Decimal('0'), Decimal('15000'), Decimal('0')),
            ('Karnataka', Decimal('15001'), Decimal('25000'), Decimal('200')),
            ('Karnataka', Decimal('25001'), Decimal('999999'), Decimal('200')),
        ]
        for state, salary_from, salary_to, tax_amount in slab_data:
            slab, _ = ProfessionalTaxSlab.objects.get_or_create(
                tenant=tenant,
                state=state,
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
    # LWF Configuration (Maharashtra + Karnataka)
    # ------------------------------------------------------------------
    def _create_lwf_configuration(self, tenant):
        lwf_data = [
            ('Maharashtra', Decimal('6.00'), Decimal('18.00'), 'half_yearly'),
            ('Karnataka', Decimal('20.00'), Decimal('40.00'), 'annual'),
        ]
        for state, ee_contrib, er_contrib, freq in lwf_data:
            LWFConfiguration.objects.get_or_create(
                tenant=tenant,
                state=state,
                defaults={
                    'employee_contribution': ee_contrib,
                    'employer_contribution': er_contrib,
                    'frequency': freq,
                    'is_active': True,
                    'effective_from': date(2024, 1, 1),
                },
            )

    # ------------------------------------------------------------------
    # Payroll Periods, Entries & Components
    # ------------------------------------------------------------------
    def _create_payroll_periods(self, tenant, employees, assignments,
                                 pay_components, managers):
        periods = []
        today = date.today()

        emp_salary_map = {}
        for assignment in assignments:
            emp_salary_map[assignment.employee_id] = assignment

        # Create payroll periods for the last 6 months
        for month_offset in range(6, 0, -1):
            period_date = today.replace(day=1) - timedelta(days=month_offset * 28)
            month = period_date.month
            year = period_date.year
            month_name = period_date.strftime('%B')

            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            start_date = date(year, month, 1)
            payment_date = end_date + timedelta(days=1)

            # Vary statuses: older months are paid, recent ones may be in different stages
            if month_offset >= 3:
                period_status = 'paid'
            elif month_offset == 2:
                period_status = 'approved'
            elif month_offset == 1:
                period_status = random.choice(['processed', 'draft'])
            else:
                period_status = 'draft'

            period, created = PayrollPeriod.objects.get_or_create(
                tenant=tenant,
                month=month,
                year=year,
                defaults={
                    'name': f'{month_name} {year}',
                    'start_date': start_date,
                    'end_date': end_date,
                    'payment_date': payment_date if period_status == 'paid' else None,
                    'status': period_status,
                    'employee_count': len(employees),
                    'processed_by': random.choice(managers) if period_status != 'draft' else None,
                    'processed_at': (
                        timezone.now() - timedelta(days=month_offset * 28)
                    ) if period_status != 'draft' else None,
                    'approved_by': (
                        random.choice(managers)
                    ) if period_status in ('approved', 'paid') else None,
                    'approved_at': (
                        timezone.now() - timedelta(days=month_offset * 28 - 2)
                    ) if period_status in ('approved', 'paid') else None,
                    'remarks': f'Payroll for {month_name} {year}',
                },
            )

            if created:
                total_gross = Decimal('0')
                total_deductions = Decimal('0')
                total_net = Decimal('0')

                for emp in employees:
                    emp_sal = emp_salary_map.get(emp.id)
                    if not emp_sal:
                        continue

                    gross = emp_sal.gross_salary
                    deduction_total = Decimal('0')
                    emp_components = list(
                        EmployeeSalaryComponent.all_objects.filter(
                            tenant=tenant, employee_salary=emp_sal))

                    for ec in emp_components:
                        if ec.pay_component.component_type == 'deduction':
                            deduction_total += ec.monthly_amount

                    net_pay = gross - deduction_total
                    days_in_month = (end_date - start_date).days + 1
                    days_present = days_in_month - random.randint(0, 3)
                    days_absent = days_in_month - days_present
                    lop_days = Decimal(str(max(0, days_absent - 1)))
                    lop_amount = (gross / days_in_month * lop_days).quantize(
                        Decimal('0.01'))

                    # Add some variety with bonus and arrears for paid months
                    bonus_amount = Decimal('0')
                    arrears_amount = Decimal('0')
                    if period_status == 'paid' and random.random() < 0.1:
                        bonus_amount = Decimal(str(random.randint(2000, 10000)))
                    if period_status == 'paid' and random.random() < 0.05:
                        arrears_amount = Decimal(str(random.randint(1000, 5000)))

                    entry_status = period_status if period_status != 'draft' else 'draft'
                    if period_status == 'paid':
                        entry_status = 'paid'
                    elif period_status == 'approved':
                        entry_status = 'approved'
                    elif period_status == 'processed':
                        entry_status = 'calculated'

                    entry = PayrollEntry.objects.create(
                        tenant=tenant,
                        payroll_period=period,
                        employee=emp,
                        employee_salary=emp_sal,
                        gross_earnings=gross,
                        total_deductions=deduction_total.quantize(Decimal('0.01')),
                        net_pay=(net_pay - lop_amount + bonus_amount + arrears_amount).quantize(Decimal('0.01')),
                        days_payable=days_in_month,
                        days_present=days_present,
                        days_absent=days_absent,
                        lop_days=lop_days,
                        lop_amount=lop_amount,
                        bonus_amount=bonus_amount,
                        arrears_amount=arrears_amount,
                        status=entry_status,
                    )

                    for ec in emp_components:
                        PayrollEntryComponent.objects.create(
                            tenant=tenant,
                            payroll_entry=entry,
                            pay_component=ec.pay_component,
                            amount=ec.monthly_amount,
                        )

                    total_gross += gross
                    total_deductions += deduction_total
                    total_net += net_pay - lop_amount + bonus_amount + arrears_amount

                period.total_gross = total_gross.quantize(Decimal('0.01'))
                period.total_deductions = total_deductions.quantize(Decimal('0.01'))
                period.total_net = total_net.quantize(Decimal('0.01'))
                period.save()

            periods.append(period)

        return periods

    # ------------------------------------------------------------------
    # Statutory Contributions (PF, ESI, PT per employee per period)
    # ------------------------------------------------------------------
    def _create_statutory_contributions(self, tenant, periods):
        count = 0
        for period in periods:
            entries = list(PayrollEntry.all_objects.filter(
                tenant=tenant, payroll_period=period))
            for entry in entries:
                existing = StatutoryContribution.all_objects.filter(
                    tenant=tenant, payroll_entry=entry).exists()
                if existing:
                    continue

                emp_sal = entry.employee_salary
                if not emp_sal:
                    continue

                # Get component amounts for this employee
                emp_comps = {
                    ec.pay_component.code: ec.monthly_amount
                    for ec in EmployeeSalaryComponent.all_objects.filter(
                        tenant=tenant, employee_salary=emp_sal)
                }

                basic = emp_comps.get('BASIC', Decimal('0'))
                gross = entry.gross_earnings

                # PF Employee (12% of Basic, max on 15000)
                pf_base = min(basic, Decimal('15000'))
                pf_ee = (pf_base * Decimal('0.12')).quantize(Decimal('0.01'))
                StatutoryContribution.objects.create(
                    tenant=tenant,
                    payroll_entry=entry,
                    employee=entry.employee,
                    payroll_period=period,
                    contribution_type='pf_employee',
                    amount=pf_ee,
                    base_amount=pf_base,
                )
                count += 1

                # PF Employer (12% of Basic, max on 15000)
                pf_er = (pf_base * Decimal('0.12')).quantize(Decimal('0.01'))
                StatutoryContribution.objects.create(
                    tenant=tenant,
                    payroll_entry=entry,
                    employee=entry.employee,
                    payroll_period=period,
                    contribution_type='pf_employer',
                    amount=pf_er,
                    base_amount=pf_base,
                )
                count += 1

                # EPS (8.33% of Basic, max on 15000 - part of employer share)
                eps = (pf_base * Decimal('0.0833')).quantize(Decimal('0.01'))
                StatutoryContribution.objects.create(
                    tenant=tenant,
                    payroll_entry=entry,
                    employee=entry.employee,
                    payroll_period=period,
                    contribution_type='eps',
                    amount=eps,
                    base_amount=pf_base,
                )
                count += 1

                # ESI Employee (0.75% of gross if gross <= 21000)
                if gross <= Decimal('21000'):
                    esi_ee = (gross * Decimal('0.0075')).quantize(Decimal('0.01'))
                    StatutoryContribution.objects.create(
                        tenant=tenant,
                        payroll_entry=entry,
                        employee=entry.employee,
                        payroll_period=period,
                        contribution_type='esi_employee',
                        amount=esi_ee,
                        base_amount=gross,
                    )
                    count += 1

                    # ESI Employer (3.25% of gross)
                    esi_er = (gross * Decimal('0.0325')).quantize(Decimal('0.01'))
                    StatutoryContribution.objects.create(
                        tenant=tenant,
                        payroll_entry=entry,
                        employee=entry.employee,
                        payroll_period=period,
                        contribution_type='esi_employer',
                        amount=esi_er,
                        base_amount=gross,
                    )
                    count += 1

                # Professional Tax
                StatutoryContribution.objects.create(
                    tenant=tenant,
                    payroll_entry=entry,
                    employee=entry.employee,
                    payroll_period=period,
                    contribution_type='pt',
                    amount=Decimal('200.00'),
                    base_amount=gross,
                )
                count += 1

        return count

    # ------------------------------------------------------------------
    # Salary Holds
    # ------------------------------------------------------------------
    def _create_salary_holds(self, tenant, employees, periods, managers):
        count = 0
        if len(employees) < 3 or not periods:
            return count

        # Create 2-3 salary holds
        held_employees = random.sample(employees, min(3, len(employees)))

        for emp in held_employees:
            existing = SalaryHold.all_objects.filter(
                tenant=tenant, employee=emp).exists()
            if existing:
                continue

            reason = random.choice(HOLD_REASONS)
            is_released = random.random() < 0.4

            hold = SalaryHold.objects.create(
                tenant=tenant,
                employee=emp,
                payroll_period=random.choice(periods) if random.random() < 0.7 else None,
                reason=reason,
                held_by=random.choice(managers),
                status='released' if is_released else 'active',
                released_by=random.choice(managers) if is_released else None,
                released_at=(
                    timezone.now() - timedelta(days=random.randint(1, 10))
                ) if is_released else None,
                release_remarks=(
                    'Clearance completed. All assets returned and verified.'
                ) if is_released else '',
            )
            count += 1

        return count

    # ------------------------------------------------------------------
    # Salary Revisions
    # ------------------------------------------------------------------
    def _create_salary_revisions(self, tenant, employees, assignments,
                                   structures, pay_components, managers):
        count = 0
        if len(employees) < 4:
            return count

        emp_salary_map = {a.employee_id: a for a in assignments}

        # Create 3-4 salary revisions
        revised_employees = random.sample(
            employees, min(4, len(employees)))

        statuses = ['draft', 'pending', 'approved', 'applied']

        for emp in revised_employees:
            existing = SalaryRevision.all_objects.filter(
                tenant=tenant, employee=emp).exists()
            if existing:
                continue

            old_assignment = emp_salary_map.get(emp.id)
            if not old_assignment:
                continue

            old_ctc = old_assignment.ctc
            # Hike between 8-25%
            hike_pct = Decimal(str(random.randint(8, 25))) / Decimal('100')
            new_ctc = (old_ctc * (1 + hike_pct)).quantize(Decimal('0.01'))

            status = random.choice(statuses)
            effective_from = date(2025, 4, 1)
            revision_date = fake.date_between(
                start_date=date(2025, 3, 1), end_date=date(2025, 3, 31))

            arrears_amount = Decimal('0')
            new_assignment = None
            if status == 'applied':
                # Create a new salary assignment for the applied revision
                arrears_months = random.randint(1, 3)
                monthly_diff = (new_ctc - old_ctc) / 12
                arrears_amount = (monthly_diff * arrears_months).quantize(Decimal('0.01'))

                # Pick appropriate structure
                if new_ctc < Decimal('500000'):
                    structure = structures[0]
                elif new_ctc < Decimal('1000000'):
                    structure = structures[1]
                else:
                    structure = structures[2]

                monthly_ctc = new_ctc / 12
                basic = monthly_ctc * Decimal('0.40')
                hra = basic * Decimal('0.50')
                da = basic * Decimal('0.05')
                lta = basic * Decimal('0.10')
                conv = Decimal('1600')
                med = Decimal('1250')
                gross = basic + hra + da + lta + conv + med
                pf_er = min(basic * Decimal('0.12'), Decimal('1800'))
                esi_er = gross * Decimal('0.0325') if gross <= Decimal('21000') else Decimal('0')
                special = monthly_ctc - gross - pf_er - esi_er
                if special < 0:
                    special = Decimal('0')
                gross += special
                pf_ee = min(basic * Decimal('0.12'), Decimal('1800'))
                esi_ee = gross * Decimal('0.0075') if gross <= Decimal('21000') else Decimal('0')
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
                    remarks=f'Revised CTC after annual appraisal - {hike_pct*100:.0f}% hike',
                )

                # Mark old assignment as revised
                old_assignment.status = 'revised'
                old_assignment.effective_to = effective_from - timedelta(days=1)
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
                    monthly_amt = component_amounts.get(comp.code, Decimal('0'))
                    EmployeeSalaryComponent.objects.create(
                        tenant=tenant,
                        employee_salary=new_assignment,
                        pay_component=comp,
                        monthly_amount=monthly_amt.quantize(Decimal('0.01')),
                        annual_amount=(monthly_amt * 12).quantize(Decimal('0.01')),
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
                arrears_from=date(2025, 1, 1) if arrears_amount > 0 else None,
                arrears_amount=arrears_amount,
                reason=random.choice(REVISION_REASONS),
                status=status,
                approved_by=(
                    random.choice(managers)
                ) if status in ('approved', 'applied') else None,
                approved_at=(
                    timezone.now() - timedelta(days=random.randint(1, 15))
                ) if status in ('approved', 'applied') else None,
            )
            count += 1

        return count

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
                    'locked': random.random() < 0.3,
                },
            )
            if created:
                count += 1
        return count

    # ------------------------------------------------------------------
    # Investment Declarations
    # ------------------------------------------------------------------
    def _create_investment_declarations(self, tenant, employees, managers):
        count = 0
        statuses = ['draft', 'submitted', 'submitted', 'verified', 'verified']

        for emp in employees:
            existing = InvestmentDeclaration.all_objects.filter(
                tenant=tenant, employee=emp,
                financial_year='2025-26').exists()
            if existing:
                continue

            # Each employee gets 2-5 random declarations
            num_declarations = random.randint(2, 5)
            selected = random.sample(
                DECLARATION_TEMPLATES,
                min(num_declarations, len(DECLARATION_TEMPLATES)))

            for tmpl in selected:
                status = random.choice(statuses)
                declared_amount = tmpl['amount']
                # Vary amounts slightly
                variance = Decimal(str(random.randint(-5000, 5000)))
                declared_amount = max(Decimal('1000'), declared_amount + variance)

                verified_amount = Decimal('0')
                verified_by = None
                verified_at = None
                rejection_reason = ''

                if status == 'verified':
                    verified_amount = declared_amount
                    verified_by = random.choice(managers)
                    verified_at = timezone.now() - timedelta(
                        days=random.randint(5, 30))
                elif status == 'rejected':
                    rejection_reason = random.choice([
                        'Document not legible. Please re-upload.',
                        'Amount mismatch between receipt and declaration.',
                        'Receipt date outside the financial year.',
                        'Incomplete documentation submitted.',
                    ])
                    verified_by = random.choice(managers)
                    verified_at = timezone.now() - timedelta(
                        days=random.randint(5, 30))

                InvestmentDeclaration.objects.create(
                    tenant=tenant,
                    employee=emp,
                    financial_year='2025-26',
                    section=tmpl['section'],
                    description=tmpl['description'],
                    declared_amount=declared_amount.quantize(Decimal('0.01')),
                    verified_amount=verified_amount.quantize(Decimal('0.01')),
                    status=status,
                    verified_by=verified_by,
                    verified_at=verified_at,
                    rejection_reason=rejection_reason,
                )
                count += 1

        return count

    # ------------------------------------------------------------------
    # Tax Computations
    # ------------------------------------------------------------------
    def _create_tax_computations(self, tenant, employees, assignments):
        count = 0
        emp_salary_map = {a.employee_id: a for a in assignments}

        for emp in employees:
            existing = TaxComputation.all_objects.filter(
                tenant=tenant, employee=emp,
                financial_year='2025-26').exists()
            if existing:
                continue

            emp_sal = emp_salary_map.get(emp.id)
            if not emp_sal:
                continue

            ctc = emp_sal.ctc
            regime_choice = TaxRegimeChoice.all_objects.filter(
                tenant=tenant, employee=emp,
                financial_year='2025-26').first()
            regime = regime_choice.regime if regime_choice else 'new'

            total_income = ctc
            standard_deduction = Decimal('75000')

            if regime == 'old':
                # Old regime: more exemptions and deductions
                hra_exempt = min(
                    emp_sal.gross_salary * Decimal('0.20') * 12,
                    Decimal('200000'))
                total_exemptions = standard_deduction + hra_exempt
                deductions_80c = min(
                    Decimal(str(random.randint(100000, 150000))),
                    Decimal('150000'))
                deductions_other = Decimal(str(random.randint(20000, 75000)))
            else:
                # New regime: standard deduction only
                total_exemptions = standard_deduction
                deductions_80c = Decimal('0')
                deductions_other = Decimal('0')

            taxable_income = max(
                Decimal('0'),
                total_income - total_exemptions - deductions_80c - deductions_other)

            # Simplified tax calculation
            if regime == 'new':
                # New regime slabs (FY 2025-26)
                tax = self._calc_new_regime_tax(taxable_income)
            else:
                # Old regime slabs
                tax = self._calc_old_regime_tax(taxable_income)

            education_cess = (tax * Decimal('0.04')).quantize(Decimal('0.01'))
            total_tax = tax + education_cess

            # TDS deducted year to date (assume ~8 months passed)
            months_elapsed = random.randint(6, 10)
            monthly_tds = (total_tax / 12).quantize(Decimal('0.01'))
            tds_ytd = (monthly_tds * months_elapsed).quantize(Decimal('0.01'))
            remaining_tax = max(Decimal('0'), total_tax - tds_ytd)

            TaxComputation.objects.create(
                tenant=tenant,
                employee=emp,
                financial_year='2025-26',
                regime=regime,
                total_income=total_income.quantize(Decimal('0.01')),
                total_exemptions=total_exemptions.quantize(Decimal('0.01')),
                total_deductions_80c=deductions_80c.quantize(Decimal('0.01')),
                total_deductions_other=deductions_other.quantize(Decimal('0.01')),
                taxable_income=taxable_income.quantize(Decimal('0.01')),
                tax_on_income=tax.quantize(Decimal('0.01')),
                education_cess=education_cess,
                total_tax_liability=total_tax.quantize(Decimal('0.01')),
                tds_deducted_ytd=tds_ytd,
                remaining_tax=remaining_tax.quantize(Decimal('0.01')),
                monthly_tds=monthly_tds,
            )
            count += 1

        return count

    def _calc_new_regime_tax(self, taxable_income):
        """New tax regime slabs FY 2025-26."""
        tax = Decimal('0')
        slabs = [
            (Decimal('400000'), Decimal('0')),
            (Decimal('400000'), Decimal('0.05')),
            (Decimal('400000'), Decimal('0.10')),
            (Decimal('400000'), Decimal('0.15')),
            (Decimal('400000'), Decimal('0.20')),
            (Decimal('999999999'), Decimal('0.30')),
        ]
        remaining = taxable_income
        for slab_limit, rate in slabs:
            if remaining <= 0:
                break
            taxable_in_slab = min(remaining, slab_limit)
            tax += taxable_in_slab * rate
            remaining -= taxable_in_slab
        return tax.quantize(Decimal('0.01'))

    def _calc_old_regime_tax(self, taxable_income):
        """Old tax regime slabs."""
        tax = Decimal('0')
        slabs = [
            (Decimal('250000'), Decimal('0')),
            (Decimal('250000'), Decimal('0.05')),
            (Decimal('500000'), Decimal('0.20')),
            (Decimal('999999999'), Decimal('0.30')),
        ]
        remaining = taxable_income
        for slab_limit, rate in slabs:
            if remaining <= 0:
                break
            taxable_in_slab = min(remaining, slab_limit)
            tax += taxable_in_slab * rate
            remaining -= taxable_in_slab
        return tax.quantize(Decimal('0.01'))

    # ------------------------------------------------------------------
    # Bank Files
    # ------------------------------------------------------------------
    def _create_bank_files(self, tenant, periods, managers):
        count = 0
        bank_formats = ['hdfc', 'icici', 'sbi', 'neft']

        for period in periods:
            existing = BankFile.all_objects.filter(
                tenant=tenant, payroll_period=period).exists()
            if existing:
                continue

            if period.status not in ('approved', 'paid'):
                continue

            bank_format = random.choice(bank_formats)
            month_str = f"{period.year}{period.month:02d}"
            file_name = f"SALARY_{bank_format.upper()}_{month_str}.txt"

            status = 'processed' if period.status == 'paid' else 'generated'

            BankFile.objects.create(
                tenant=tenant,
                payroll_period=period,
                file_name=file_name,
                bank_format=bank_format,
                total_amount=period.total_net,
                employee_count=period.employee_count,
                status=status,
                generated_by=random.choice(managers),
                generated_at=timezone.now() - timedelta(
                    days=random.randint(1, 30)),
                remarks=f'Bank file for {period.name} - {bank_format.upper()} format',
            )
            count += 1

        return count

    # ------------------------------------------------------------------
    # Payslips
    # ------------------------------------------------------------------
    def _create_payslips(self, tenant, periods):
        count = 0
        for period in periods:
            if period.status not in ('approved', 'paid'):
                continue

            entries = PayrollEntry.all_objects.filter(
                tenant=tenant, payroll_period=period)

            for entry in entries:
                existing = Payslip.all_objects.filter(
                    tenant=tenant, payroll_entry=entry).exists()
                if existing:
                    continue

                is_emailed = period.status == 'paid' and random.random() < 0.8
                is_viewed = is_emailed and random.random() < 0.6

                Payslip.objects.create(
                    tenant=tenant,
                    payroll_entry=entry,
                    employee=entry.employee,
                    payroll_period=period,
                    is_emailed=is_emailed,
                    emailed_at=(
                        timezone.now() - timedelta(days=random.randint(1, 25))
                    ) if is_emailed else None,
                    is_viewed=is_viewed,
                    viewed_at=(
                        timezone.now() - timedelta(days=random.randint(1, 20))
                    ) if is_viewed else None,
                )
                count += 1

        return count

    # ------------------------------------------------------------------
    # Payment Register
    # ------------------------------------------------------------------
    def _create_payment_register(self, tenant, periods):
        count = 0
        for period in periods:
            if period.status != 'paid':
                continue

            entries = PayrollEntry.all_objects.filter(
                tenant=tenant, payroll_period=period)

            for entry in entries:
                existing = PaymentRegister.all_objects.filter(
                    tenant=tenant, payroll_entry=entry).exists()
                if existing:
                    continue

                bank_name = random.choice(BANK_NAMES)
                ifsc_prefix = IFSC_PREFIXES.get(bank_name, 'HDFC0')
                ifsc_code = ifsc_prefix + fake.numerify('######')

                # Most are processed/reconciled for paid periods
                pr_status = random.choice([
                    'reconciled', 'reconciled', 'reconciled', 'processed'])

                PaymentRegister.objects.create(
                    tenant=tenant,
                    payroll_period=period,
                    employee=entry.employee,
                    payroll_entry=entry,
                    amount=entry.net_pay,
                    payment_mode='bank_transfer',
                    bank_name=bank_name,
                    account_number=fake.numerify('################'),
                    ifsc_code=ifsc_code,
                    transaction_reference=f'UTR{fake.numerify("################")}',
                    payment_date=period.payment_date,
                    status=pr_status,
                    reconciled_at=(
                        timezone.now() - timedelta(days=random.randint(1, 20))
                    ) if pr_status == 'reconciled' else None,
                )
                count += 1

        return count

    # ------------------------------------------------------------------
    # Reimbursements
    # ------------------------------------------------------------------
    def _create_reimbursements(self, tenant, employees, managers):
        count = 0
        statuses = ['draft', 'submitted', 'submitted', 'approved',
                     'approved', 'paid', 'rejected']

        # 60% of employees submit at least one reimbursement
        num_claimants = max(3, int(len(employees) * 0.6))
        selected = random.sample(employees, min(num_claimants, len(employees)))

        for emp in selected:
            # Each claimant gets 1-3 reimbursements
            num_claims = random.randint(1, 3)
            samples = random.sample(
                REIMBURSEMENT_SAMPLES,
                min(num_claims, len(REIMBURSEMENT_SAMPLES)))

            for sample in samples:
                status = random.choice(statuses)
                claim_date = fake.date_between(
                    start_date='-90d', end_date='today')
                approved_by = (
                    random.choice(managers)
                ) if status in ('approved', 'paid') else None
                approved_at = (
                    timezone.now() - timedelta(days=random.randint(1, 15))
                ) if approved_by else None

                # Vary the amount slightly
                amount = sample['amount'] + Decimal(
                    str(random.randint(-500, 1000)))
                amount = max(Decimal('500'), amount)

                approved_amount = amount if status in (
                    'approved', 'paid') else Decimal('0')
                # Sometimes partial approval
                if status in ('approved', 'paid') and random.random() < 0.15:
                    approved_amount = (
                        amount * Decimal(str(random.randint(70, 95)))
                        / Decimal('100')
                    ).quantize(Decimal('0.01'))

                rejection_reason = ''
                if status == 'rejected':
                    rejection_reason = random.choice([
                        'Insufficient documentation. Please attach original receipts.',
                        'Claim amount exceeds policy limit for this category.',
                        'Duplicate claim - already submitted for this period.',
                        'Receipt date is older than 90 days. Not eligible per policy.',
                    ])

                Reimbursement.objects.create(
                    tenant=tenant,
                    employee=emp,
                    category=sample['category'],
                    description=sample['description'],
                    amount=amount.quantize(Decimal('0.01')),
                    approved_amount=approved_amount.quantize(Decimal('0.01')),
                    claim_date=claim_date,
                    receipt_date=claim_date - timedelta(
                        days=random.randint(0, 10)),
                    status=status,
                    approved_by=approved_by,
                    approved_at=approved_at,
                    rejection_reason=rejection_reason,
                )
                count += 1

        return count
