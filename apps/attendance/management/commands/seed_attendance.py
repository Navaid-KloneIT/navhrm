import random
from datetime import timedelta, date, time, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.core.models import Tenant, set_current_tenant
from apps.organization.models import Department, Location
from apps.employees.models import Employee
from apps.attendance.models import (
    Shift, ShiftAssignment, Attendance, AttendanceRegularization,
    LeaveType, LeavePolicy, LeaveBalance, LeaveApplication,
    Project, Task, Timesheet, TimeEntry, OvertimeRequest,
    Holiday, FloatingHoliday, HolidayPolicy,
)

fake = Faker()

# ---------------------------------------------------------------------------
# Realistic data pools
# ---------------------------------------------------------------------------

SHIFT_DATA = [
    {'name': 'General Shift', 'code': 'GS', 'start': time(9, 0), 'end': time(18, 0), 'night': False},
    {'name': 'Morning Shift', 'code': 'MS', 'start': time(6, 0), 'end': time(14, 0), 'night': False},
    {'name': 'Afternoon Shift', 'code': 'AS', 'start': time(14, 0), 'end': time(22, 0), 'night': False},
    {'name': 'Night Shift', 'code': 'NS', 'start': time(22, 0), 'end': time(6, 0), 'night': True},
    {'name': 'Flexible Shift', 'code': 'FS', 'start': time(10, 0), 'end': time(19, 0), 'night': False},
]

LEAVE_TYPES_DATA = [
    {'name': 'Sick Leave', 'code': 'SL', 'category': 'sick', 'paid': True, 'max_days': 12, 'color': '#ef4444', 'doc_required': True, 'doc_after': 3},
    {'name': 'Casual Leave', 'code': 'CL', 'category': 'casual', 'paid': True, 'max_days': 12, 'color': '#3b82f6', 'doc_required': False, 'doc_after': 0},
    {'name': 'Earned Leave', 'code': 'EL', 'category': 'earned', 'paid': True, 'max_days': 15, 'color': '#22c55e', 'doc_required': False, 'doc_after': 0},
    {'name': 'Unpaid Leave', 'code': 'UL', 'category': 'unpaid', 'paid': False, 'max_days': 30, 'color': '#6b7280', 'doc_required': False, 'doc_after': 0},
    {'name': 'Compensatory Off', 'code': 'CO', 'category': 'comp_off', 'paid': True, 'max_days': 5, 'color': '#a855f7', 'doc_required': False, 'doc_after': 0},
    {'name': 'Maternity Leave', 'code': 'ML', 'category': 'maternity', 'paid': True, 'max_days': 182, 'color': '#ec4899', 'doc_required': True, 'doc_after': 0},
    {'name': 'Paternity Leave', 'code': 'PL', 'category': 'paternity', 'paid': True, 'max_days': 15, 'color': '#0ea5e9', 'doc_required': True, 'doc_after': 0},
    {'name': 'Bereavement Leave', 'code': 'BL', 'category': 'bereavement', 'paid': True, 'max_days': 5, 'color': '#78716c', 'doc_required': False, 'doc_after': 0},
]

NATIONAL_HOLIDAYS = [
    {'name': "New Year's Day", 'date': date(2026, 1, 1)},
    {'name': 'Republic Day', 'date': date(2026, 1, 26)},
    {'name': 'Independence Day', 'date': date(2026, 8, 15)},
    {'name': 'Gandhi Jayanti', 'date': date(2026, 10, 2)},
    {'name': 'Christmas Day', 'date': date(2026, 12, 25)},
]

COMPANY_HOLIDAYS = [
    {'name': 'Company Foundation Day', 'date': date(2026, 3, 15)},
    {'name': 'Annual Day', 'date': date(2026, 9, 20)},
]

REGIONAL_HOLIDAYS = [
    {'name': 'Holi', 'date': date(2026, 3, 10)},
    {'name': 'Diwali', 'date': date(2026, 10, 20)},
    {'name': 'Eid al-Fitr', 'date': date(2026, 3, 30)},
]

RESTRICTED_HOLIDAYS = [
    {'name': 'Good Friday', 'date': date(2026, 4, 3)},
    {'name': 'Buddha Purnima', 'date': date(2026, 5, 12)},
    {'name': 'Guru Nanak Jayanti', 'date': date(2026, 11, 4)},
    {'name': 'Maha Shivaratri', 'date': date(2026, 2, 15)},
]

PROJECT_DATA = [
    {'name': 'Website Redesign', 'code': 'WEB-001', 'client': 'Acme Corp', 'billable': True},
    {'name': 'Mobile App v2.0', 'code': 'MOB-001', 'client': 'TechVision', 'billable': True},
    {'name': 'ERP Integration', 'code': 'ERP-001', 'client': 'GlobalSoft', 'billable': True},
    {'name': 'Internal DevOps', 'code': 'INT-001', 'client': '', 'billable': False},
    {'name': 'Data Migration', 'code': 'DAT-001', 'client': 'Stellar Systems', 'billable': True},
    {'name': 'Security Audit', 'code': 'SEC-001', 'client': '', 'billable': False},
    {'name': 'Customer Portal', 'code': 'CUS-001', 'client': 'Innovate Labs', 'billable': True},
    {'name': 'AI Chatbot', 'code': 'AI-001', 'client': 'TechVision', 'billable': True},
]

TASK_NAMES = [
    'Requirements gathering', 'UI/UX design', 'Frontend development',
    'Backend development', 'API integration', 'Database design',
    'Unit testing', 'Code review', 'Performance optimization',
    'Documentation', 'Deployment', 'Bug fixes', 'User training',
    'Load testing', 'Security review',
]

REGULARIZATION_REASONS_DETAIL = [
    'Was at client site for the entire day, forgot to punch in.',
    'System was down when I tried to punch in the morning.',
    'Worked from home due to heavy rain, forgot to mark attendance.',
    'Had an offsite meeting, could not access the system.',
    'Biometric was not working, informed HR.',
    'Was on official duty at branch office.',
    'Internet outage at home, worked from mobile.',
    'Forgot to punch out in the evening rush.',
]

LEAVE_REASONS = [
    'Not feeling well, need rest.',
    'Family function to attend.',
    'Personal work - bank/government office.',
    'Taking a vacation with family.',
    'Medical appointment scheduled.',
    'Child is unwell, need to take care.',
    'Moving to a new apartment.',
    'Attending a wedding.',
    'Religious festival celebration.',
    'Mental health day.',
    'Parent-teacher meeting at school.',
    'Home repair work scheduled.',
]

OT_REASONS = [
    'Release deadline approaching, need extra hours to complete testing.',
    'Client demo preparation - need to fix critical bugs.',
    'Month-end processing requires extended hours.',
    'Production deployment scheduled for weekend.',
    'Sprint deliverables pending, need extra time.',
    'Urgent client requirement with tight deadline.',
    'System migration planned for off-hours.',
    'Covering for colleague on leave.',
]


class Command(BaseCommand):
    help = 'Seed the database with attendance & leave module data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=60,
            help='Number of past days to generate attendance for (default: 60)'
        )

    def handle(self, *args, **options):
        num_days = options['days']

        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR(
                'No tenants found. Run "python manage.py seed_data" first.'
            ))
            return

        self.stdout.write('Seeding attendance & leave data...\n')

        for tenant in tenants:
            set_current_tenant(tenant)
            self.stdout.write(f'  Tenant: {tenant.name}')

            employees = list(Employee.all_objects.filter(
                tenant=tenant, status='active'))
            departments = list(Department.all_objects.filter(tenant=tenant))
            locations = list(Location.all_objects.filter(tenant=tenant))

            if not employees:
                self.stdout.write(self.style.WARNING(
                    f'    Skipping - no active employees found'
                ))
                continue

            # 1. Shifts
            shifts = self._create_shifts(tenant)
            self.stdout.write(f'    Created {len(shifts)} shifts')

            # 2. Shift Assignments
            assignments = self._create_shift_assignments(
                tenant, employees, shifts)
            self.stdout.write(f'    Created {len(assignments)} shift assignments')

            # 3. Holidays
            holidays = self._create_holidays(tenant, locations)
            self.stdout.write(f'    Created {len(holidays)} holidays')

            # 4. Holiday Policies
            policies = self._create_holiday_policies(
                tenant, holidays, locations, departments)
            self.stdout.write(f'    Created {len(policies)} holiday policies')

            # 5. Leave Types
            leave_types = self._create_leave_types(tenant)
            self.stdout.write(f'    Created {len(leave_types)} leave types')

            # 6. Leave Policies
            leave_policies = self._create_leave_policies(
                tenant, leave_types)
            self.stdout.write(f'    Created {len(leave_policies)} leave policies')

            # 7. Leave Balances
            balances = self._create_leave_balances(
                tenant, employees, leave_types)
            self.stdout.write(f'    Created {len(balances)} leave balances')

            # 8. Leave Applications
            leave_apps = self._create_leave_applications(
                tenant, employees, leave_types, balances)
            self.stdout.write(f'    Created {len(leave_apps)} leave applications')

            # 9. Attendance Records
            holiday_dates = {h.date for h in holidays}
            records = self._create_attendance_records(
                tenant, employees, shifts, holiday_dates, leave_apps, num_days)
            self.stdout.write(f'    Created {len(records)} attendance records')

            # 10. Regularizations
            regularizations = self._create_regularizations(
                tenant, employees, records)
            self.stdout.write(f'    Created {len(regularizations)} regularization requests')

            # 11. Floating Holidays
            floating = self._create_floating_holidays(
                tenant, employees, holidays)
            self.stdout.write(f'    Created {len(floating)} floating holiday selections')

            # 12. Projects
            projects = self._create_projects(tenant, employees)
            self.stdout.write(f'    Created {len(projects)} projects')

            # 13. Tasks
            tasks = self._create_tasks(tenant, projects, employees)
            self.stdout.write(f'    Created {len(tasks)} tasks')

            # 14. Timesheets & Time Entries
            timesheets, entries = self._create_timesheets(
                tenant, employees, projects, tasks)
            self.stdout.write(
                f'    Created {len(timesheets)} timesheets with {len(entries)} time entries')

            # 15. Overtime Requests
            overtimes = self._create_overtime_requests(
                tenant, employees, projects)
            self.stdout.write(f'    Created {len(overtimes)} overtime requests')

            self.stdout.write(f'    Completed: {tenant.name}\n')

        set_current_tenant(None)
        self.stdout.write(self.style.SUCCESS(
            '\nAttendance & leave data seeded successfully!'))

    # ------------------------------------------------------------------
    # Shifts
    # ------------------------------------------------------------------
    def _create_shifts(self, tenant):
        shifts = []
        for data in SHIFT_DATA:
            shifts.append(Shift.objects.create(
                tenant=tenant,
                name=data['name'],
                code=data['code'],
                start_time=data['start'],
                end_time=data['end'],
                grace_period_minutes=random.choice([10, 15, 15, 30]),
                half_day_threshold_hours=Decimal('4.0'),
                full_day_threshold_hours=Decimal('8.0'),
                is_night_shift=data['night'],
                is_active=True,
                description=f"{data['name']} - {data['start'].strftime('%H:%M')} to {data['end'].strftime('%H:%M')}",
            ))
        return shifts

    # ------------------------------------------------------------------
    # Shift Assignments
    # ------------------------------------------------------------------
    def _create_shift_assignments(self, tenant, employees, shifts):
        assignments = []
        general_shift = shifts[0]  # General Shift is default

        for emp in employees:
            # 70% get general shift, 30% get random shift
            shift = general_shift if random.random() < 0.7 else random.choice(shifts)
            assignments.append(ShiftAssignment.objects.create(
                tenant=tenant,
                employee=emp,
                shift=shift,
                effective_from=emp.date_of_joining or date(2025, 1, 1),
                effective_to=None,
                is_active=True,
            ))
        return assignments

    # ------------------------------------------------------------------
    # Holidays
    # ------------------------------------------------------------------
    def _create_holidays(self, tenant, locations):
        holidays = []
        location = locations[0] if locations else None

        for h in NATIONAL_HOLIDAYS:
            holidays.append(Holiday.objects.create(
                tenant=tenant,
                name=h['name'],
                date=h['date'],
                holiday_type='national',
                year=h['date'].year,
                is_active=True,
            ))

        for h in COMPANY_HOLIDAYS:
            holidays.append(Holiday.objects.create(
                tenant=tenant,
                name=h['name'],
                date=h['date'],
                holiday_type='company',
                year=h['date'].year,
                is_active=True,
            ))

        for h in REGIONAL_HOLIDAYS:
            holidays.append(Holiday.objects.create(
                tenant=tenant,
                name=h['name'],
                date=h['date'],
                holiday_type='regional',
                location=location,
                year=h['date'].year,
                is_active=True,
            ))

        for h in RESTRICTED_HOLIDAYS:
            holidays.append(Holiday.objects.create(
                tenant=tenant,
                name=h['name'],
                date=h['date'],
                holiday_type='restricted',
                year=h['date'].year,
                is_active=True,
            ))

        return holidays

    # ------------------------------------------------------------------
    # Holiday Policies
    # ------------------------------------------------------------------
    def _create_holiday_policies(self, tenant, holidays, locations, departments):
        policies = []

        policy = HolidayPolicy.objects.create(
            tenant=tenant,
            name='Standard Holiday Policy 2026',
            description='Applicable to all full-time employees across all locations.',
            location=locations[0] if locations else None,
            applicable_employment_types='full_time,part_time',
            max_floating_holidays=2,
            year=2026,
            is_active=True,
        )
        national_and_company = [
            h for h in holidays if h.holiday_type in ('national', 'company')]
        policy.holidays.set(national_and_company)
        policies.append(policy)

        if departments:
            policy2 = HolidayPolicy.objects.create(
                tenant=tenant,
                name='Engineering Holiday Policy 2026',
                description='Additional holidays for engineering teams.',
                department=departments[0],
                applicable_employment_types='full_time',
                max_floating_holidays=3,
                year=2026,
                is_active=True,
            )
            policy2.holidays.set(holidays[:10])
            policies.append(policy2)

        return policies

    # ------------------------------------------------------------------
    # Leave Types
    # ------------------------------------------------------------------
    def _create_leave_types(self, tenant):
        leave_types = []
        for lt in LEAVE_TYPES_DATA:
            leave_types.append(LeaveType.objects.create(
                tenant=tenant,
                name=lt['name'],
                code=lt['code'],
                category=lt['category'],
                is_paid=lt['paid'],
                max_days_per_year=Decimal(str(lt['max_days'])),
                max_consecutive_days=lt['max_days'] if lt['category'] in ('maternity', 'paternity') else random.choice([3, 5, None]),
                requires_approval=True,
                requires_document=lt['doc_required'],
                document_after_days=lt['doc_after'],
                is_active=True,
                description=f"{lt['name']} for all eligible employees.",
                color_code=lt['color'],
            ))
        return leave_types

    # ------------------------------------------------------------------
    # Leave Policies
    # ------------------------------------------------------------------
    def _create_leave_policies(self, tenant, leave_types):
        policies = []
        accrual_map = {
            'sick': ('monthly', Decimal('1.0')),
            'casual': ('monthly', Decimal('1.0')),
            'earned': ('monthly', Decimal('1.25')),
            'unpaid': ('none', Decimal('0')),
            'comp_off': ('none', Decimal('0')),
            'maternity': ('annual', Decimal('182.0')),
            'paternity': ('annual', Decimal('15.0')),
            'bereavement': ('annual', Decimal('5.0')),
        }

        for lt in leave_types:
            accrual_freq, accrual_amt = accrual_map.get(
                lt.category, ('annual', Decimal('1.0')))

            carry_forward = lt.category in ('earned', 'sick')
            encashment = lt.category == 'earned'

            policies.append(LeavePolicy.objects.create(
                tenant=tenant,
                name=f'{lt.name} Policy',
                leave_type=lt,
                accrual_frequency=accrual_freq,
                accrual_amount=accrual_amt,
                allow_carry_forward=carry_forward,
                max_carry_forward_days=Decimal('5') if carry_forward else Decimal('0'),
                carry_forward_expiry_months=3 if carry_forward else 0,
                allow_encashment=encashment,
                max_encashment_days=Decimal('10') if encashment else Decimal('0'),
                applicable_from_days=0 if lt.category in ('sick', 'casual', 'unpaid') else 90,
                applicable_employment_types='full_time,part_time' if lt.category != 'comp_off' else 'full_time',
                prorate_for_joining=lt.category in ('earned', 'sick', 'casual'),
                is_active=True,
            ))
        return policies

    # ------------------------------------------------------------------
    # Leave Balances
    # ------------------------------------------------------------------
    def _create_leave_balances(self, tenant, employees, leave_types):
        balances = []
        year = 2026

        # Only create for common leave types (first 5)
        common_types = leave_types[:5]

        for emp in employees:
            for lt in common_types:
                allocated = float(lt.max_days_per_year)
                used = round(random.uniform(0, allocated * 0.6), 1)
                carried = round(random.uniform(0, 3), 1) if lt.category in ('earned', 'sick') else 0

                balances.append(LeaveBalance.objects.create(
                    tenant=tenant,
                    employee=emp,
                    leave_type=lt,
                    year=year,
                    allocated=Decimal(str(allocated)),
                    used=Decimal(str(used)),
                    carried_forward=Decimal(str(carried)),
                    adjustment=Decimal('0'),
                    encashed=Decimal('0'),
                ))
        return balances

    # ------------------------------------------------------------------
    # Leave Applications
    # ------------------------------------------------------------------
    def _create_leave_applications(self, tenant, employees, leave_types, balances):
        applications = []
        common_types = leave_types[:5]
        statuses = ['pending', 'pending', 'approved', 'approved', 'approved',
                    'rejected', 'cancelled']
        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        # Create 2-4 leave applications per employee (for ~40% of employees)
        selected_employees = random.sample(
            employees, min(len(employees), max(5, len(employees) * 4 // 10)))

        for emp in selected_employees:
            num_apps = random.randint(1, 3)
            for _ in range(num_apps):
                lt = random.choice(common_types)
                status = random.choice(statuses)
                from_date = fake.date_between(
                    start_date='-60d', end_date='+30d')
                duration = random.choice([1, 1, 1, 2, 2, 3, 5])
                to_date = from_date + timedelta(days=duration - 1)

                from_day = random.choice(['full_day', 'full_day', 'first_half'])
                to_day = 'full_day' if duration > 1 else from_day

                # Calculate total days
                total = float(duration)
                if from_day != 'full_day':
                    total -= 0.5
                if duration > 1 and to_day != 'full_day':
                    total -= 0.5

                approved_by = random.choice(managers) if status in ('approved', 'rejected') else None
                approved_at = timezone.now() - timedelta(
                    days=random.randint(1, 30)) if approved_by else None

                app = LeaveApplication.objects.create(
                    tenant=tenant,
                    employee=emp,
                    leave_type=lt,
                    from_date=from_date,
                    to_date=to_date,
                    from_day_type=from_day,
                    to_day_type=to_day,
                    total_days=Decimal(str(total)),
                    reason=random.choice(LEAVE_REASONS),
                    status=status,
                    approved_by=approved_by,
                    approved_at=approved_at,
                    rejection_reason='Insufficient leave balance.' if status == 'rejected' else '',
                    cancellation_reason='Plans changed.' if status == 'cancelled' else '',
                    cancelled_at=timezone.now() - timedelta(
                        days=random.randint(1, 10)) if status == 'cancelled' else None,
                )
                applications.append(app)

        return applications

    # ------------------------------------------------------------------
    # Attendance Records
    # ------------------------------------------------------------------
    def _create_attendance_records(self, tenant, employees, shifts,
                                    holiday_dates, leave_apps, num_days):
        records = []
        today = date.today()

        # Build leave date lookup: {(emp_id, date): True}
        leave_dates = set()
        for app in leave_apps:
            if app.status == 'approved':
                d = app.from_date
                while d <= app.to_date:
                    leave_dates.add((app.employee_id, d))
                    d += timedelta(days=1)

        # Generate attendance for last num_days for each employee
        # (limit to 15 employees for performance)
        selected = random.sample(employees, min(15, len(employees)))

        for emp in selected:
            # Find assigned shift
            assignment = ShiftAssignment.all_objects.filter(
                tenant=tenant, employee=emp, is_active=True).first()
            shift = assignment.shift if assignment else shifts[0]

            for day_offset in range(num_days, 0, -1):
                current_date = today - timedelta(days=day_offset)
                weekday = current_date.weekday()

                # Weekend
                if weekday >= 5:
                    records.append(Attendance(
                        tenant=tenant, employee=emp, date=current_date,
                        shift=shift, status='weekend', source='system'))
                    continue

                # Holiday
                if current_date in holiday_dates:
                    records.append(Attendance(
                        tenant=tenant, employee=emp, date=current_date,
                        shift=shift, status='holiday', source='system'))
                    continue

                # On leave
                if (emp.id, current_date) in leave_dates:
                    records.append(Attendance(
                        tenant=tenant, employee=emp, date=current_date,
                        shift=shift, status='on_leave', source='system'))
                    continue

                # Normal working day - 85% present, 5% absent, 5% half_day, 5% not_marked
                roll = random.random()
                if roll < 0.85:
                    # Present
                    grace = shift.grace_period_minutes
                    late_chance = random.random()
                    if late_chance < 0.15:
                        late_mins = random.randint(grace + 1, grace + 60)
                        check_in_dt = datetime.combine(
                            current_date, shift.start_time
                        ) + timedelta(minutes=late_mins)
                        is_late = True
                    else:
                        early_mins = random.randint(0, grace)
                        check_in_dt = datetime.combine(
                            current_date, shift.start_time
                        ) - timedelta(minutes=random.randint(0, 15)) + timedelta(minutes=early_mins)
                        is_late = False
                        late_mins = 0

                    # Check out
                    work_hours = random.uniform(7.5, 10.0)
                    check_out_dt = check_in_dt + timedelta(hours=work_hours)

                    total_hours = round(work_hours, 2)
                    overtime = round(max(0, total_hours - 8.0), 2)

                    early_dep = random.random() < 0.05
                    early_dep_mins = random.randint(10, 60) if early_dep else 0

                    check_in_aware = timezone.make_aware(check_in_dt)
                    check_out_aware = timezone.make_aware(check_out_dt)

                    records.append(Attendance(
                        tenant=tenant, employee=emp, date=current_date,
                        check_in=check_in_aware, check_out=check_out_aware,
                        shift=shift, status='present',
                        total_hours=Decimal(str(total_hours)),
                        overtime_hours=Decimal(str(overtime)),
                        is_late=is_late,
                        late_minutes=late_mins if is_late else 0,
                        is_early_departure=early_dep,
                        early_departure_minutes=early_dep_mins,
                        source='web',
                    ))
                elif roll < 0.90:
                    records.append(Attendance(
                        tenant=tenant, employee=emp, date=current_date,
                        shift=shift, status='absent', source='system'))
                elif roll < 0.95:
                    # Half day
                    check_in_dt = datetime.combine(
                        current_date, shift.start_time)
                    check_out_dt = check_in_dt + timedelta(hours=4)
                    check_in_aware = timezone.make_aware(check_in_dt)
                    check_out_aware = timezone.make_aware(check_out_dt)

                    records.append(Attendance(
                        tenant=tenant, employee=emp, date=current_date,
                        check_in=check_in_aware, check_out=check_out_aware,
                        shift=shift, status='half_day',
                        total_hours=Decimal('4.0'), source='web'))
                else:
                    records.append(Attendance(
                        tenant=tenant, employee=emp, date=current_date,
                        shift=shift, status='not_marked', source='system'))

        # Bulk create for performance
        Attendance.objects.bulk_create(records, ignore_conflicts=True)
        return records

    # ------------------------------------------------------------------
    # Regularizations
    # ------------------------------------------------------------------
    def _create_regularizations(self, tenant, employees, records):
        regularizations = []
        statuses = ['pending', 'pending', 'approved', 'approved', 'rejected']
        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        # Pick some absent/not_marked records to regularize
        eligible = [r for r in records if r.status in ('absent', 'not_marked')]
        selected = random.sample(eligible, min(15, len(eligible)))

        for record in selected:
            status = random.choice(statuses)
            reviewed_by = random.choice(managers) if status in ('approved', 'rejected') else None

            # Fetch the actual attendance from DB (bulk_create doesn't set pk)
            att = Attendance.all_objects.filter(
                tenant=tenant, employee=record.employee,
                date=record.date).first()

            req_check_in = timezone.make_aware(
                datetime.combine(record.date, time(9, 0)))
            req_check_out = timezone.make_aware(
                datetime.combine(record.date, time(18, 0)))

            regularizations.append(AttendanceRegularization.objects.create(
                tenant=tenant,
                employee=record.employee,
                attendance=att,
                date=record.date,
                requested_check_in=req_check_in,
                requested_check_out=req_check_out,
                requested_status='present',
                reason=random.choice([
                    'forgot_punch', 'system_error', 'on_duty',
                    'work_from_home', 'other']),
                reason_detail=random.choice(REGULARIZATION_REASONS_DETAIL),
                status=status,
                reviewed_by=reviewed_by,
                reviewed_at=timezone.now() - timedelta(
                    days=random.randint(1, 10)) if reviewed_by else None,
                review_comments='Verified and approved.' if status == 'approved'
                    else 'No supporting evidence provided.' if status == 'rejected'
                    else '',
            ))

        return regularizations

    # ------------------------------------------------------------------
    # Floating Holidays
    # ------------------------------------------------------------------
    def _create_floating_holidays(self, tenant, employees, holidays):
        floating = []
        restricted = [h for h in holidays if h.holiday_type == 'restricted']
        if not restricted:
            return floating

        # ~30% of employees select floating holidays
        selected = random.sample(
            employees, min(len(employees), max(3, len(employees) * 3 // 10)))

        for emp in selected:
            # Each employee picks 1-2 floating holidays
            picks = random.sample(restricted, min(2, len(restricted)))
            for holiday in picks:
                floating.append(FloatingHoliday.objects.create(
                    tenant=tenant,
                    holiday=holiday,
                    employee=emp,
                    status=random.choice(['selected', 'selected', 'availed']),
                    selected_date=holiday.date,
                    notes=f'Selected {holiday.name} as floating holiday.',
                ))

        return floating

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------
    def _create_projects(self, tenant, employees):
        projects = []
        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        for data in PROJECT_DATA:
            start = fake.date_between(start_date='-180d', end_date='-30d')
            end = start + timedelta(days=random.randint(60, 365))
            status = random.choice(
                ['active', 'active', 'active', 'on_hold', 'completed'])

            project = Project.objects.create(
                tenant=tenant,
                name=data['name'],
                code=data['code'],
                description=fake.paragraph(nb_sentences=3),
                client_name=data['client'],
                manager=random.choice(managers),
                start_date=start,
                end_date=end,
                budget_hours=Decimal(str(random.randint(200, 2000))),
                hourly_rate=Decimal(str(random.randint(50, 200))) if data['billable'] else Decimal('0'),
                status=status,
                is_billable=data['billable'],
            )
            # Add 3-8 members
            members = random.sample(
                employees, min(random.randint(3, 8), len(employees)))
            project.members.set(members)
            projects.append(project)

        return projects

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------
    def _create_tasks(self, tenant, projects, employees):
        tasks = []
        for project in projects:
            num_tasks = random.randint(3, 6)
            selected_names = random.sample(
                TASK_NAMES, min(num_tasks, len(TASK_NAMES)))
            members = list(project.members.all())

            for name in selected_names:
                tasks.append(Task.objects.create(
                    tenant=tenant,
                    project=project,
                    name=name,
                    description=fake.sentence(),
                    assigned_to=random.choice(members) if members else random.choice(employees),
                    estimated_hours=Decimal(str(random.randint(4, 40))),
                    status=random.choice(['open', 'in_progress', 'in_progress', 'completed']),
                    due_date=fake.date_between(
                        start_date='-30d', end_date='+60d'),
                ))
        return tasks

    # ------------------------------------------------------------------
    # Timesheets & Time Entries
    # ------------------------------------------------------------------
    def _create_timesheets(self, tenant, employees, projects, tasks):
        timesheets = []
        entries = []
        statuses = ['draft', 'submitted', 'submitted', 'approved', 'approved', 'rejected']

        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        # Create timesheets for last 4 weeks for ~30% of employees
        selected = random.sample(
            employees, min(len(employees), max(3, len(employees) * 3 // 10)))

        today = date.today()
        active_projects = [p for p in projects if p.status == 'active']
        if not active_projects:
            active_projects = projects[:3]

        for emp in selected:
            for week_offset in range(4):
                week_start = today - timedelta(
                    days=today.weekday() + (week_offset * 7))
                week_end = week_start + timedelta(days=6)
                status = random.choice(statuses)

                approved_by = random.choice(managers) if status in ('approved', 'rejected') else None

                ts = Timesheet.objects.create(
                    tenant=tenant,
                    employee=emp,
                    week_start_date=week_start,
                    week_end_date=week_end,
                    status=status,
                    submitted_at=timezone.now() - timedelta(
                        days=random.randint(1, 7)) if status != 'draft' else None,
                    approved_by=approved_by,
                    approved_at=timezone.now() - timedelta(
                        days=random.randint(0, 3)) if approved_by else None,
                    rejection_reason='Missing project details. Please update.' if status == 'rejected' else '',
                    notes=fake.sentence() if random.random() > 0.5 else '',
                )

                # Create 3-5 time entries per timesheet
                total_h = Decimal('0')
                billable_h = Decimal('0')
                num_entries = random.randint(3, 5)

                for _ in range(num_entries):
                    project = random.choice(active_projects)
                    project_tasks = [t for t in tasks if t.project_id == project.id]
                    task = random.choice(project_tasks) if project_tasks else None
                    entry_date = week_start + timedelta(
                        days=random.randint(0, 4))
                    hours = Decimal(str(random.choice([2, 3, 4, 4, 6, 8])))
                    is_billable = project.is_billable

                    entry = TimeEntry.objects.create(
                        tenant=tenant,
                        timesheet=ts,
                        employee=emp,
                        project=project,
                        task=task,
                        date=entry_date,
                        hours=hours,
                        description=fake.sentence(),
                        is_billable=is_billable,
                    )
                    entries.append(entry)
                    total_h += hours
                    if is_billable:
                        billable_h += hours

                ts.total_hours = total_h
                ts.billable_hours = billable_h
                ts.save()
                timesheets.append(ts)

        return timesheets, entries

    # ------------------------------------------------------------------
    # Overtime Requests
    # ------------------------------------------------------------------
    def _create_overtime_requests(self, tenant, employees, projects):
        overtimes = []
        statuses = ['pending', 'pending', 'approved', 'approved', 'rejected', 'cancelled']
        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        active_projects = [p for p in projects if p.status == 'active']

        # ~20% of employees have OT requests
        selected = random.sample(
            employees, min(len(employees), max(3, len(employees) * 2 // 10)))

        for emp in selected:
            num_ot = random.randint(1, 3)
            for _ in range(num_ot):
                status = random.choice(statuses)
                ot_date = fake.date_between(start_date='-30d', end_date='+7d')
                planned = Decimal(str(random.choice([2, 3, 4, 4, 6])))
                actual = planned - Decimal(str(random.choice([0, 0, 0, 1]))) if status == 'approved' else Decimal('0')

                approved_by = random.choice(managers) if status in ('approved', 'rejected') else None

                overtimes.append(OvertimeRequest.objects.create(
                    tenant=tenant,
                    employee=emp,
                    date=ot_date,
                    ot_type=random.choice(['weekday', 'weekday', 'weekend', 'holiday']),
                    planned_hours=planned,
                    actual_hours=actual,
                    reason=random.choice(OT_REASONS),
                    project=random.choice(active_projects) if active_projects and random.random() > 0.3 else None,
                    status=status,
                    approved_by=approved_by,
                    approved_at=timezone.now() - timedelta(
                        days=random.randint(1, 10)) if approved_by else None,
                    rejection_reason='OT not pre-approved by manager.' if status == 'rejected' else '',
                    generate_comp_off=random.random() > 0.7,
                ))

        return overtimes
