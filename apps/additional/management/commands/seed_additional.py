import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Tenant
from apps.accounts.models import User
from apps.employees.models import Employee
from apps.organization.models import Department, Designation
from apps.additional.models import (
    AssetCategory, Asset, AssetAllocation, AssetMaintenance,
    ExpenseCategory, ExpensePolicy, ExpenseClaim,
    TravelPolicy, TravelRequest, TravelExpense, TravelSettlement,
    TicketCategory, Ticket, TicketComment, KnowledgeBase,
)


class Command(BaseCommand):
    help = 'Seed additional module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding additional module data for {tenant.name}...')
            employees = list(Employee.all_objects.filter(tenant=tenant, status='active'))
            users = list(User.objects.filter(tenant=tenant))

            if len(employees) < 1 or len(users) < 1:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - insufficient data.'))
                continue

            self._seed_asset_categories(tenant)
            self._seed_assets(tenant)
            self._seed_asset_allocations(tenant, employees, users)
            self._seed_asset_maintenance(tenant)
            self._seed_expense_categories(tenant)
            self._seed_expense_policies(tenant)
            self._seed_expense_claims(tenant, employees, users)
            self._seed_travel_policies(tenant)
            self._seed_travel_requests(tenant, employees, users)
            self._seed_ticket_categories(tenant, users)
            self._seed_tickets(tenant, employees, users)
            self._seed_knowledge_base(tenant, users)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding additional data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Additional module data seeding complete!'))

    def _seed_asset_categories(self, tenant):
        if AssetCategory.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Asset categories already exist, skipping...')
            return

        categories = [
            ('Laptop', 'Laptops and notebooks'),
            ('Desktop', 'Desktop computers and workstations'),
            ('Mobile Phone', 'Company mobile phones'),
            ('Furniture', 'Office furniture - desks, chairs, cabinets'),
            ('Vehicle', 'Company vehicles'),
            ('Printer', 'Printers and scanners'),
            ('Projector', 'Projectors and display equipment'),
            ('Networking', 'Routers, switches, and networking equipment'),
        ]

        for name, desc in categories:
            AssetCategory.all_objects.create(tenant=tenant, name=name, description=desc, is_active=True)
        self.stdout.write('  Created 8 asset categories.')

    def _seed_assets(self, tenant):
        if Asset.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Assets already exist, skipping...')
            return

        categories = list(AssetCategory.all_objects.filter(tenant=tenant))
        assets_data = [
            ('Dell Latitude 5540', 'Laptop', 'new', 'available', 85000),
            ('Dell Latitude 5540', 'Laptop', 'good', 'allocated', 85000),
            ('MacBook Pro 14"', 'Laptop', 'new', 'allocated', 195000),
            ('HP EliteDesk 800', 'Desktop', 'good', 'available', 65000),
            ('HP EliteDesk 800', 'Desktop', 'fair', 'allocated', 65000),
            ('iPhone 15 Pro', 'Mobile Phone', 'new', 'allocated', 134900),
            ('Samsung Galaxy S24', 'Mobile Phone', 'good', 'available', 79999),
            ('Ergonomic Chair', 'Furniture', 'good', 'allocated', 15000),
            ('Standing Desk', 'Furniture', 'new', 'available', 25000),
            ('Toyota Innova', 'Vehicle', 'good', 'available', 1800000),
            ('HP LaserJet Pro', 'Printer', 'good', 'available', 35000),
            ('Epson EB-U05', 'Projector', 'fair', 'available', 55000),
            ('Cisco Switch 24-Port', 'Networking', 'good', 'available', 45000),
            ('Dell Latitude 7440', 'Laptop', 'new', 'maintenance', 125000),
            ('Logitech Webcam C920', 'Desktop', 'good', 'available', 8500),
        ]

        cat_map = {c.name: c for c in categories}
        for i, (name, cat_name, condition, status, cost) in enumerate(assets_data, 1):
            category = cat_map.get(cat_name)
            purchase_date = date.today() - timedelta(days=random.randint(30, 730))
            Asset.all_objects.create(
                tenant=tenant,
                asset_id=f'AST-{tenant.slug[:3].upper()}-{i:04d}',
                name=name,
                category=category,
                serial_number=f'SN-{random.randint(100000, 999999)}',
                purchase_date=purchase_date,
                purchase_cost=Decimal(str(cost)),
                warranty_expiry=purchase_date + timedelta(days=365),
                condition=condition,
                status=status,
                location='Head Office',
            )
        self.stdout.write('  Created 15 assets.')

    def _seed_asset_allocations(self, tenant, employees, users):
        if AssetAllocation.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Asset allocations already exist, skipping...')
            return

        allocated_assets = list(Asset.all_objects.filter(tenant=tenant, status='allocated'))
        for asset in allocated_assets:
            emp = random.choice(employees)
            user = random.choice(users)
            allocated_date = date.today() - timedelta(days=random.randint(7, 180))
            AssetAllocation.all_objects.create(
                tenant=tenant,
                asset=asset,
                employee=emp,
                allocated_date=allocated_date,
                allocated_by=user,
                expected_return_date=allocated_date + timedelta(days=365),
                condition_at_allocation=asset.condition,
                status='active',
            )
        self.stdout.write(f'  Created {len(allocated_assets)} asset allocations.')

    def _seed_asset_maintenance(self, tenant):
        if AssetMaintenance.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Asset maintenance already exist, skipping...')
            return

        assets = list(Asset.all_objects.filter(tenant=tenant))[:5]
        types = ['preventive', 'corrective', 'amc']
        statuses = ['scheduled', 'in_progress', 'completed']
        vendors = ['TechCare Services', 'QuickFix IT', 'ProMaintain Solutions']

        for asset in assets:
            mtype = random.choice(types)
            mstatus = random.choice(statuses)
            scheduled = date.today() - timedelta(days=random.randint(0, 60))
            AssetMaintenance.all_objects.create(
                tenant=tenant,
                asset=asset,
                maintenance_type=mtype,
                description=f'{mtype.capitalize()} maintenance for {asset.name}',
                scheduled_date=scheduled,
                completed_date=scheduled + timedelta(days=random.randint(1, 7)) if mstatus == 'completed' else None,
                cost=Decimal(str(random.randint(500, 15000))),
                vendor=random.choice(vendors),
                status=mstatus,
            )
        self.stdout.write(f'  Created {len(assets)} maintenance records.')

    def _seed_expense_categories(self, tenant):
        if ExpenseCategory.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Expense categories already exist, skipping...')
            return

        categories = [
            ('Travel', 'Travel related expenses', 50000),
            ('Food & Entertainment', 'Meals and entertainment', 5000),
            ('Office Supplies', 'Stationery and office items', 10000),
            ('Communication', 'Phone and internet bills', 3000),
            ('Training', 'Training and certification costs', 100000),
            ('Medical', 'Medical expenses not covered by insurance', 25000),
        ]

        for name, desc, limit in categories:
            ExpenseCategory.all_objects.create(
                tenant=tenant, name=name, description=desc,
                max_limit=Decimal(str(limit)), is_active=True,
            )
        self.stdout.write('  Created 6 expense categories.')

    def _seed_expense_policies(self, tenant):
        if ExpensePolicy.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Expense policies already exist, skipping...')
            return

        departments = list(Department.all_objects.filter(tenant=tenant))
        designations = list(Designation.all_objects.filter(tenant=tenant))

        policies = [
            ('General Expense Policy', 'all', None, None, 25000, 500),
            ('Travel Expense Policy', 'all', None, None, 100000, 1000),
            ('Department Head Policy', 'department', departments[0] if departments else None, None, 50000, 2000),
        ]

        if designations:
            policies.append(('Executive Expense Policy', 'designation', None, designations[0], 200000, 5000))

        for name, applies_to, dept, desig, max_amt, receipt_above in policies:
            ExpensePolicy.all_objects.create(
                tenant=tenant, name=name, applies_to=applies_to,
                department=dept, designation=desig,
                max_amount=Decimal(str(max_amt)),
                requires_receipt_above=Decimal(str(receipt_above)),
                is_active=True,
            )
        self.stdout.write(f'  Created {len(policies)} expense policies.')

    def _seed_expense_claims(self, tenant, employees, users):
        if ExpenseClaim.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Expense claims already exist, skipping...')
            return

        categories = list(ExpenseCategory.all_objects.filter(tenant=tenant))
        statuses = ['draft', 'submitted', 'approved', 'rejected', 'reimbursed']
        titles = [
            'Client meeting lunch', 'Office supplies purchase', 'Cab to airport',
            'Team dinner', 'Conference registration', 'Medical checkup',
            'Internet bill reimbursement', 'Book purchase', 'Parking charges',
            'Hotel stay for client visit', 'Flight tickets', 'Office furniture repair',
        ]

        for i, title in enumerate(titles):
            emp = random.choice(employees)
            cat = random.choice(categories) if categories else None
            status = random.choice(statuses)
            expense_date = date.today() - timedelta(days=random.randint(1, 90))

            claim = ExpenseClaim.all_objects.create(
                tenant=tenant,
                employee=emp,
                title=title,
                category=cat,
                amount=Decimal(str(random.randint(500, 50000))),
                expense_date=expense_date,
                description=f'{title} - expense claim',
                status=status,
                submitted_date=expense_date + timedelta(days=1) if status != 'draft' else None,
                approved_by=random.choice(users) if status in ['approved', 'reimbursed'] else None,
                approved_date=expense_date + timedelta(days=3) if status in ['approved', 'reimbursed'] else None,
                rejection_reason='Amount exceeds policy limit' if status == 'rejected' else '',
                reimbursement_date=expense_date + timedelta(days=10) if status == 'reimbursed' else None,
            )
        self.stdout.write(f'  Created {len(titles)} expense claims.')

    def _seed_travel_policies(self, tenant):
        if TravelPolicy.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Travel policies already exist, skipping...')
            return

        policies = [
            ('Economy Travel', 'Standard travel policy for all employees', 'economy', 2000, 5000),
            ('Business Travel', 'For senior managers and above', 'business', 4000, 10000),
            ('Executive Travel', 'For C-level executives', 'first', 8000, 25000),
        ]

        for name, desc, tclass, daily, hotel in policies:
            TravelPolicy.all_objects.create(
                tenant=tenant, name=name, description=desc,
                travel_class=tclass,
                daily_allowance=Decimal(str(daily)),
                hotel_limit=Decimal(str(hotel)),
                is_active=True,
            )
        self.stdout.write('  Created 3 travel policies.')

    def _seed_travel_requests(self, tenant, employees, users):
        if TravelRequest.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Travel requests already exist, skipping...')
            return

        purposes = [
            'Client meeting in Mumbai', 'Annual conference attendance',
            'Branch office visit', 'Training workshop', 'Vendor negotiation',
            'Project kickoff meeting', 'Sales pitch to potential client',
            'Team building offsite',
        ]
        locations = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata']
        statuses = ['draft', 'submitted', 'approved', 'completed', 'rejected']

        for purpose in purposes:
            emp = random.choice(employees)
            status = random.choice(statuses)
            dep_date = date.today() + timedelta(days=random.randint(-30, 60))
            ret_date = dep_date + timedelta(days=random.randint(1, 7))
            from_loc = random.choice(locations)
            to_loc = random.choice([l for l in locations if l != from_loc])
            estimated = random.randint(5000, 100000)
            advance = status in ['approved', 'completed']

            tr = TravelRequest.all_objects.create(
                tenant=tenant,
                employee=emp,
                purpose=purpose,
                travel_type=random.choice(['domestic', 'international']),
                from_location=from_loc,
                to_location=to_loc,
                departure_date=dep_date,
                return_date=ret_date,
                estimated_cost=Decimal(str(estimated)),
                advance_required=advance,
                advance_amount=Decimal(str(int(estimated * 0.5))) if advance else Decimal('0'),
                status=status,
                approved_by=random.choice(users) if status in ['approved', 'completed'] else None,
                approved_date=dep_date - timedelta(days=2) if status in ['approved', 'completed'] else None,
                rejection_reason='Budget constraints' if status == 'rejected' else '',
            )

            # Add expenses for approved/completed requests
            if status in ['approved', 'completed']:
                expense_types = ['flight', 'hotel', 'cab', 'food']
                for etype in random.sample(expense_types, random.randint(2, 4)):
                    TravelExpense.all_objects.create(
                        tenant=tenant,
                        travel_request=tr,
                        expense_type=etype,
                        amount=Decimal(str(random.randint(500, 30000))),
                        description=f'{etype.capitalize()} expense',
                        date=dep_date + timedelta(days=random.randint(0, 3)),
                    )

            # Add settlement for completed requests
            if status == 'completed':
                total_exp = tr.total_expenses
                adv = tr.advance_amount
                TravelSettlement.all_objects.create(
                    tenant=tenant,
                    travel_request=tr,
                    total_expenses=total_exp,
                    advance_given=adv,
                    settlement_amount=total_exp - adv,
                    status='settled',
                    settled_date=ret_date + timedelta(days=5),
                )

        self.stdout.write(f'  Created {len(purposes)} travel requests with expenses.')

    def _seed_ticket_categories(self, tenant, users):
        if TicketCategory.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Ticket categories already exist, skipping...')
            return

        departments = list(Department.all_objects.filter(tenant=tenant))
        dept_map = {d.name.lower(): d for d in departments}

        categories = [
            ('IT Support', 'Hardware, software, and network issues', 'engineering', 4, 24),
            ('HR Query', 'Leave, payroll, and policy queries', 'hr', 8, 48),
            ('Facilities', 'Office maintenance and facilities', 'operations', 12, 72),
            ('Finance', 'Expense, reimbursement, and payment issues', 'finance', 8, 48),
            ('Admin', 'General administrative requests', None, 24, 72),
        ]

        for name, desc, dept_key, sla_resp, sla_res in categories:
            dept = None
            if dept_key:
                for d_name, d in dept_map.items():
                    if dept_key in d_name.lower():
                        dept = d
                        break

            TicketCategory.all_objects.create(
                tenant=tenant, name=name, description=desc,
                department=dept,
                default_assignee=random.choice(users) if users else None,
                sla_response_hours=sla_resp,
                sla_resolution_hours=sla_res,
                is_active=True,
            )
        self.stdout.write('  Created 5 ticket categories.')

    def _seed_tickets(self, tenant, employees, users):
        if Ticket.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Tickets already exist, skipping...')
            return

        categories = list(TicketCategory.all_objects.filter(tenant=tenant))
        tickets_data = [
            ('Laptop not booting', 'My laptop shows a black screen after the logo', 'high', 'IT Support'),
            ('VPN connection issue', 'Cannot connect to company VPN from home', 'medium', 'IT Support'),
            ('Leave balance incorrect', 'My leave balance shows 5 days less than expected', 'medium', 'HR Query'),
            ('Salary slip not generated', 'January salary slip not visible in ESS portal', 'high', 'HR Query'),
            ('AC not working', 'Air conditioning in meeting room 3 is not working', 'low', 'Facilities'),
            ('Parking pass request', 'Need a new parking pass for my vehicle', 'low', 'Facilities'),
            ('Reimbursement delayed', 'My approved reimbursement from December is pending', 'high', 'Finance'),
            ('Tax declaration help', 'Need guidance on tax saving investments', 'medium', 'Finance'),
            ('ID card replacement', 'Lost my employee ID card, need replacement', 'medium', 'Admin'),
            ('Visitor pass request', 'Need visitor passes for 5 people next Monday', 'low', 'Admin'),
            ('Email access issue', 'Cannot access company email on phone', 'medium', 'IT Support'),
            ('Office chair broken', 'Hydraulic mechanism of my office chair is broken', 'low', 'Facilities'),
            ('PF withdrawal query', 'How to apply for partial PF withdrawal?', 'medium', 'HR Query'),
            ('Printer not working', 'Floor 2 printer showing error E05', 'low', 'IT Support'),
            ('Travel reimbursement', 'Pending travel reimbursement for Bangalore trip', 'medium', 'Finance'),
        ]

        statuses = ['open', 'assigned', 'in_progress', 'resolved', 'closed']
        priorities = ['low', 'medium', 'high', 'critical']

        cat_map = {c.name: c for c in categories}

        for subject, desc, priority, cat_name in tickets_data:
            cat = cat_map.get(cat_name)
            status = random.choice(statuses)
            emp = random.choice(employees)
            assigned = random.choice(users) if status != 'open' else None

            ticket = Ticket.all_objects.create(
                tenant=tenant,
                employee=emp,
                category=cat,
                subject=subject,
                description=desc,
                priority=priority,
                status=status,
                assigned_to=assigned,
                resolution='Issue has been resolved.' if status in ['resolved', 'closed'] else '',
                resolved_date=timezone.now() - timedelta(days=random.randint(1, 10)) if status in ['resolved', 'closed'] else None,
                closed_date=timezone.now() - timedelta(days=random.randint(0, 5)) if status == 'closed' else None,
                satisfaction_rating=random.randint(3, 5) if status == 'closed' else None,
                satisfaction_feedback='Good support!' if status == 'closed' else '',
            )

            # Add 1-3 comments per ticket
            for _ in range(random.randint(1, 3)):
                TicketComment.all_objects.create(
                    tenant=tenant,
                    ticket=ticket,
                    user=random.choice(users),
                    comment=random.choice([
                        'Looking into this issue.',
                        'Can you provide more details?',
                        'This has been escalated to the concerned team.',
                        'Working on the resolution.',
                        'Issue reproduced, fixing now.',
                        'Please check and confirm if the issue persists.',
                    ]),
                    is_internal=random.choice([True, False]),
                )

        self.stdout.write(f'  Created {len(tickets_data)} tickets with comments.')

    def _seed_knowledge_base(self, tenant, users):
        if KnowledgeBase.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Knowledge base articles already exist, skipping...')
            return

        categories = list(TicketCategory.all_objects.filter(tenant=tenant))
        articles = [
            ('How to Connect to Company VPN', 'Step 1: Download the VPN client from the IT portal.\nStep 2: Install and open the application.\nStep 3: Enter your employee credentials.\nStep 4: Select the nearest server and click Connect.'),
            ('Leave Application Process', 'To apply for leave:\n1. Login to ESS portal\n2. Navigate to Leave > Apply Leave\n3. Select leave type and dates\n4. Add reason and submit\n5. Your manager will receive an approval notification'),
            ('Expense Reimbursement Guide', 'How to submit expense claims:\n1. Collect all receipts and bills\n2. Go to Expenses > Claims > Create\n3. Fill in the details and upload receipts\n4. Submit for approval\n5. Track status in the Claims list'),
            ('IT Equipment Request Process', 'To request new IT equipment:\n1. Raise a ticket under IT Support category\n2. Specify the equipment needed and justification\n3. IT team will review and approve\n4. Equipment will be allocated within 5 business days'),
            ('Office Facility Booking', 'Conference rooms and facilities can be booked through:\n1. Navigate to Facilities > Room Booking\n2. Select date, time, and room\n3. Add meeting details and participants\n4. Confirm booking'),
            ('Tax Declaration FAQ', 'Common questions about tax declarations:\n- When is the deadline? March 31st of each financial year\n- What proofs are needed? Investment receipts, rent receipts, etc.\n- How to submit? Through ESS portal > Tax Declaration'),
        ]

        for title, content in articles:
            cat = random.choice(categories) if categories else None
            author = random.choice(users) if users else None
            KnowledgeBase.all_objects.create(
                tenant=tenant,
                title=title,
                category=cat,
                content=content,
                author=author,
                is_published=True,
                view_count=random.randint(10, 500),
            )
        self.stdout.write(f'  Created {len(articles)} knowledge base articles.')
