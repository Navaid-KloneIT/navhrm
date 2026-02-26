"""
Seed sample data for Payout & Reports: Bank Files, Payslips, Payment Register.
Requires: payroll periods and payroll entries to exist (run seed_payroll_runs first).

Usage:
    python manage.py seed_payout
    python manage.py seed_payout --clear   # Clear & re-seed
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant, set_current_tenant
from apps.employees.models import Employee
from apps.payroll.models import (
    PayrollPeriod, PayrollEntry,
    BankFile, Payslip, PaymentRegister,
)

BANK_NAMES = [
    'HDFC Bank', 'ICICI Bank', 'State Bank of India',
    'Axis Bank', 'Kotak Mahindra Bank', 'Punjab National Bank',
    'Bank of Baroda', 'Union Bank of India', 'IndusInd Bank',
    'Yes Bank',
]

BANK_FORMATS = ['hdfc', 'icici', 'sbi', 'axis', 'neft', 'csv']


class Command(BaseCommand):
    help = 'Seed Bank Files, Payslips, and Payment Register with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete existing payout data before seeding',
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

        self.stdout.write('Seeding Payout & Reports data...\n')

        for tenant in tenants:
            set_current_tenant(tenant)
            self.stdout.write(f'  Tenant: {tenant.name}')
            self._seed_tenant(tenant)

        self.stdout.write(self.style.SUCCESS('\nPayout & Reports seeding complete!'))

    def _clear_data(self):
        self.stdout.write('  Clearing existing payout data...')
        PaymentRegister.all_objects.all().delete()
        Payslip.all_objects.all().delete()
        BankFile.all_objects.all().delete()
        self.stdout.write(self.style.WARNING('  Cleared.'))

    def _seed_tenant(self, tenant):
        periods = list(
            PayrollPeriod.all_objects
            .filter(tenant=tenant, status__in=['approved', 'paid'])
            .order_by('-start_date')
        )
        if not periods:
            self.stdout.write(self.style.WARNING(
                '    No approved/paid payroll periods found. '
                'Run "python manage.py seed_payroll_runs" first.'
            ))
            return

        employees = list(
            Employee.all_objects.filter(tenant=tenant, status='active')
        )
        if not employees:
            self.stdout.write(self.style.WARNING('    No active employees found.'))
            return

        bank_file_count = 0
        payslip_count = 0
        payment_count = 0

        for period in periods:
            entries = list(
                PayrollEntry.all_objects
                .filter(
                    tenant=tenant,
                    payroll_period=period,
                    status__in=['approved', 'paid'],
                )
                .select_related('employee')
            )
            if not entries:
                continue

            # --- Bank Files ---
            bank_format = random.choice(BANK_FORMATS)
            format_label = dict(BankFile.BANK_FORMAT_CHOICES).get(bank_format, bank_format)
            total_amount = sum(e.net_pay for e in entries)

            if period.status == 'paid':
                bf_status = random.choice(['generated', 'sent', 'processed'])
            else:
                bf_status = 'generated'

            generated_at = timezone.now() - timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
            )

            bank_file, created = BankFile.all_objects.get_or_create(
                tenant=tenant,
                payroll_period=period,
                bank_format=bank_format,
                defaults={
                    'file_name': f"{format_label}_{period.name}",
                    'total_amount': total_amount,
                    'employee_count': len(entries),
                    'status': bf_status,
                    'generated_at': generated_at,
                    'remarks': f"Auto-generated bank file for {period.name}",
                },
            )
            if created:
                bank_file_count += 1

            # --- Payslips ---
            for entry in entries:
                _, created = Payslip.all_objects.get_or_create(
                    tenant=tenant,
                    payroll_entry=entry,
                    defaults={
                        'employee': entry.employee,
                        'payroll_period': period,
                        'is_emailed': random.random() < 0.7,
                        'emailed_at': (
                            timezone.now() - timedelta(days=random.randint(1, 15))
                            if random.random() < 0.7 else None
                        ),
                        'is_viewed': random.random() < 0.5,
                        'viewed_at': (
                            timezone.now() - timedelta(days=random.randint(1, 10))
                            if random.random() < 0.5 else None
                        ),
                    },
                )
                if created:
                    payslip_count += 1

            # --- Payment Register ---
            for entry in entries:
                emp = entry.employee
                emp_bank = emp.bank_name or random.choice(BANK_NAMES)
                emp_account = emp.bank_account or f"{random.randint(10000000000, 99999999999)}"
                emp_ifsc = emp.ifsc_code or f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))}0{random.randint(100000, 999999)}"

                if period.status == 'paid':
                    pr_status = random.choices(
                        ['processed', 'reconciled', 'failed'],
                        weights=[0.5, 0.4, 0.1],
                    )[0]
                else:
                    pr_status = 'pending'

                payment_mode = random.choices(
                    ['bank_transfer', 'cheque', 'cash'],
                    weights=[0.85, 0.10, 0.05],
                )[0]

                payment_date = None
                if pr_status in ('processed', 'reconciled'):
                    payment_date = period.end_date + timedelta(days=random.randint(1, 5))

                txn_ref = ''
                if pr_status in ('processed', 'reconciled'):
                    txn_ref = f"TXN{random.randint(100000000, 999999999)}"

                failure_reason = ''
                if pr_status == 'failed':
                    failure_reason = random.choice([
                        'Invalid bank account number',
                        'IFSC code mismatch',
                        'Account closed or frozen',
                        'Insufficient funds in company account',
                        'Bank server timeout - retry required',
                    ])

                reconciled_at = None
                if pr_status == 'reconciled':
                    reconciled_at = timezone.now() - timedelta(
                        days=random.randint(1, 15),
                    )

                _, created = PaymentRegister.all_objects.get_or_create(
                    tenant=tenant,
                    payroll_entry=entry,
                    defaults={
                        'payroll_period': period,
                        'employee': emp,
                        'amount': entry.net_pay,
                        'payment_mode': payment_mode,
                        'bank_name': emp_bank,
                        'account_number': emp_account,
                        'ifsc_code': emp_ifsc,
                        'transaction_reference': txn_ref,
                        'payment_date': payment_date,
                        'status': pr_status,
                        'failure_reason': failure_reason,
                        'reconciled_at': reconciled_at,
                    },
                )
                if created:
                    payment_count += 1

        self.stdout.write(
            f'    Bank Files: {bank_file_count}, '
            f'Payslips: {payslip_count}, '
            f'Payment Register: {payment_count}'
        )
