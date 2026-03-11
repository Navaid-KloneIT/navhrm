import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.organization.models import Department
from apps.compliance.models import (
    LaborLaw, LaborLawCompliance,
    EmploymentContract, ContractAmendment,
    CompliancePolicy, PolicyVersion, PolicyAcknowledgment,
    DisciplinaryIncident, WarningRecord, DisciplinaryAppeal,
    Grievance, GrievanceInvestigation,
    MusterRoll, WageRegister, InspectionReport,
)


class Command(BaseCommand):
    help = 'Seed compliance module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding compliance data for {tenant.name}...')
            employees = list(Employee.all_objects.filter(tenant=tenant, status='active'))

            if len(employees) < 5:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - insufficient employees.'))
                continue

            departments = list(Department.all_objects.filter(tenant=tenant, is_active=True))

            self._seed_labor_laws(tenant, employees, departments)
            self._seed_employment_contracts(tenant, employees)
            self._seed_compliance_policies(tenant, employees, departments)
            self._seed_disciplinary_incidents(tenant, employees)
            self._seed_grievances(tenant, employees)
            self._seed_statutory_registers(tenant, employees, departments)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding compliance data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Compliance module data seeding complete!'))

    # -----------------------------------------------------------------------
    # Labor Laws & Compliance Records
    # -----------------------------------------------------------------------
    def _seed_labor_laws(self, tenant, employees, departments):
        if LaborLaw.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Labor laws already exist, skipping...')
            return

        today = date.today()
        laws_data = [
            {
                'name': 'Minimum Wages Act',
                'jurisdiction': 'Federal',
                'category': 'wages',
                'description': 'Establishes minimum wage requirements for all categories of workers.',
                'compliance_requirements': 'Pay at least the minimum wage as notified; maintain wage records.',
                'penalties': 'Fine up to $10,000 per violation; imprisonment up to 6 months for repeat offenses.',
            },
            {
                'name': 'Factories Act - Working Hours',
                'jurisdiction': 'Federal',
                'category': 'working_hours',
                'description': 'Regulates working hours, overtime, and rest intervals for factory workers.',
                'compliance_requirements': 'Maximum 48 hours per week; overtime at double rate; mandatory rest intervals.',
                'penalties': 'Fine up to $5,000; potential closure order for repeated violations.',
            },
            {
                'name': 'Occupational Safety and Health Act',
                'jurisdiction': 'Federal',
                'category': 'safety',
                'description': 'Ensures safe and healthy working conditions for employees.',
                'compliance_requirements': 'Conduct safety audits quarterly; provide PPE; report workplace injuries within 24 hours.',
                'penalties': 'Fine up to $50,000 per serious violation; criminal prosecution for willful violations.',
            },
            {
                'name': 'Equal Employment Opportunity Act',
                'jurisdiction': 'Federal',
                'category': 'discrimination',
                'description': 'Prohibits discrimination based on race, gender, age, religion, or disability.',
                'compliance_requirements': 'Maintain non-discriminatory hiring practices; provide diversity training annually.',
                'penalties': 'Compensatory and punitive damages; injunctive relief; attorney fees.',
            },
        ]

        compliance_statuses = ['compliant', 'non_compliant', 'partial', 'under_review']

        for i, law_data in enumerate(laws_data):
            law = LaborLaw.all_objects.create(
                tenant=tenant,
                effective_date=today - timedelta(days=random.randint(365, 1800)),
                status='active',
                notes='Regularly reviewed for compliance.',
                **law_data,
            )

            # Create 1-2 compliance records per law
            for j in range(random.randint(1, 2)):
                dept = departments[j % len(departments)] if departments else None
                review_dt = today - timedelta(days=random.randint(0, 90))
                LaborLawCompliance.all_objects.create(
                    tenant=tenant,
                    labor_law=law,
                    department=dept,
                    compliance_status=random.choice(compliance_statuses),
                    review_date=review_dt,
                    next_review_date=review_dt + timedelta(days=90),
                    responsible_person=random.choice(employees),
                    compliance_notes=f'Review conducted for {law.name} compliance.',
                    action_required='Update internal policies to align with latest amendments.' if j == 0 else '',
                )

        self.stdout.write(f'  Created {len(laws_data)} labor laws with compliance records.')

    # -----------------------------------------------------------------------
    # Employment Contracts & Amendments
    # -----------------------------------------------------------------------
    def _seed_employment_contracts(self, tenant, employees):
        if EmploymentContract.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Employment contracts already exist, skipping...')
            return

        today = date.today()
        contract_types = ['permanent', 'fixed_term', 'probation', 'consultant', 'part_time']
        contract_statuses = ['active', 'active', 'active', 'expired', 'draft']

        amendment_types = ['salary_revision', 'designation_change', 'terms_update', 'extension']
        amendment_statuses = ['approved', 'approved', 'pending', 'draft']

        contracts = []
        for i, emp in enumerate(employees[:5]):
            ct = contract_types[i % len(contract_types)]
            start = today - timedelta(days=random.randint(180, 900))
            end = start + timedelta(days=365) if ct in ('fixed_term', 'probation', 'consultant') else None
            contract = EmploymentContract.all_objects.create(
                tenant=tenant,
                employee=emp,
                contract_type=ct,
                contract_number=f'CTR-{tenant.pk}-{1000 + i}',
                start_date=start,
                end_date=end,
                terms=f'Standard {ct.replace("_", " ")} employment terms and conditions as per company policy.',
                salary_details=f'Base salary as per grade; annual increment subject to performance review.',
                probation_period_months=3 if ct == 'probation' else 0,
                notice_period_days=random.choice([30, 60, 90]),
                status=contract_statuses[i % len(contract_statuses)],
                signed_date=start - timedelta(days=random.randint(1, 14)),
                signed_by=employees[0],
                notes='',
            )
            contracts.append(contract)

        # Create 1-2 amendments per contract
        for contract in contracts:
            for j in range(random.randint(1, 2)):
                a_type = random.choice(amendment_types)
                eff_date = contract.start_date + timedelta(days=random.randint(90, 300))
                ContractAmendment.all_objects.create(
                    tenant=tenant,
                    contract=contract,
                    amendment_type=a_type,
                    amendment_date=eff_date - timedelta(days=random.randint(5, 15)),
                    description=f'{a_type.replace("_", " ").title()} amendment for {contract.employee.first_name}.',
                    old_value='Previous terms as per original contract.',
                    new_value='Updated terms effective from amendment date.',
                    effective_date=eff_date,
                    approved_by=employees[0],
                    status=random.choice(amendment_statuses),
                )

        self.stdout.write(f'  Created {len(contracts)} employment contracts with amendments.')

    # -----------------------------------------------------------------------
    # Compliance Policies, Versions & Acknowledgments
    # -----------------------------------------------------------------------
    def _seed_compliance_policies(self, tenant, employees, departments):
        if CompliancePolicy.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Compliance policies already exist, skipping...')
            return

        today = date.today()
        policies_data = [
            {
                'title': 'Anti-Harassment Policy',
                'category': 'anti_harassment',
                'description': 'Policy to prevent and address workplace harassment.',
                'content': 'All employees must treat colleagues with respect and dignity. '
                           'Harassment of any kind including verbal, physical, or sexual is strictly prohibited. '
                           'Violations will result in disciplinary action up to and including termination.',
            },
            {
                'title': 'Code of Conduct',
                'category': 'conduct',
                'description': 'Organization-wide code of conduct for all employees.',
                'content': 'Employees shall conduct themselves with integrity, honesty, and professionalism. '
                           'Conflicts of interest must be disclosed. Company resources shall be used responsibly.',
            },
            {
                'title': 'Health and Safety Policy',
                'category': 'safety',
                'description': 'Workplace health and safety guidelines and procedures.',
                'content': 'The organization is committed to providing a safe working environment. '
                           'All employees must follow safety protocols, report hazards, and participate in safety drills.',
            },
            {
                'title': 'Data Privacy Policy',
                'category': 'data_privacy',
                'description': 'Policy governing collection, use, and protection of personal data.',
                'content': 'Personal data must be collected only for legitimate purposes. '
                           'Access is restricted to authorized personnel. Breaches must be reported within 24 hours.',
            },
        ]

        policy_statuses = ['active', 'active', 'active', 'under_review']

        for i, pol_data in enumerate(policies_data):
            eff_date = today - timedelta(days=random.randint(90, 365))
            dept = departments[i % len(departments)] if departments and i > 1 else None
            policy = CompliancePolicy.all_objects.create(
                tenant=tenant,
                version='1.0',
                effective_date=eff_date,
                status=policy_statuses[i],
                approved_by=employees[0],
                department=dept,
                **pol_data,
            )

            # Create a version history entry
            PolicyVersion.all_objects.create(
                tenant=tenant,
                policy=policy,
                version_number='1.0',
                changes_summary='Initial version of the policy.',
                content=pol_data['content'],
                created_by=employees[0],
                effective_date=eff_date,
            )

            # Create acknowledgments for a few employees
            ack_employees = random.sample(employees, min(4, len(employees)))
            for emp in ack_employees:
                PolicyAcknowledgment.all_objects.create(
                    tenant=tenant,
                    policy=policy,
                    employee=emp,
                    acknowledged_date=timezone.now() - timedelta(days=random.randint(0, 60)),
                    is_acknowledged=random.choice([True, True, True, False]),
                    notes='',
                )

        self.stdout.write(f'  Created {len(policies_data)} compliance policies with versions and acknowledgments.')

    # -----------------------------------------------------------------------
    # Disciplinary Incidents, Warnings & Appeals
    # -----------------------------------------------------------------------
    def _seed_disciplinary_incidents(self, tenant, employees):
        if DisciplinaryIncident.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Disciplinary incidents already exist, skipping...')
            return

        today = date.today()
        incidents_data = [
            {
                'incident_type': 'absenteeism',
                'severity': 'minor',
                'description': 'Employee was absent for 3 consecutive days without prior approval or notification.',
                'location': 'Main Office',
            },
            {
                'incident_type': 'policy_violation',
                'severity': 'moderate',
                'description': 'Employee accessed restricted data without proper authorization, violating IT security policy.',
                'location': 'IT Department',
            },
            {
                'incident_type': 'misconduct',
                'severity': 'major',
                'description': 'Employee was involved in a verbal altercation with a colleague during a team meeting.',
                'location': 'Conference Room B',
            },
            {
                'incident_type': 'safety_violation',
                'severity': 'critical',
                'description': 'Employee bypassed safety locks on manufacturing equipment, creating a hazardous condition.',
                'location': 'Production Floor',
            },
        ]

        incident_statuses = ['reported', 'under_investigation', 'action_taken', 'closed']
        warning_types = ['verbal', 'written', 'final']
        warning_statuses = ['issued', 'acknowledged', 'resolved']

        incidents = []
        for i, inc_data in enumerate(incidents_data):
            emp = employees[i + 1] if i + 1 < len(employees) else random.choice(employees[1:])
            incident = DisciplinaryIncident.all_objects.create(
                tenant=tenant,
                employee=emp,
                incident_date=today - timedelta(days=random.randint(10, 180)),
                reported_by=employees[0],
                witness=f'{random.choice(employees).first_name} {random.choice(employees).last_name}',
                status=incident_statuses[i],
                resolution_notes='Corrective action plan discussed with employee.' if i >= 2 else '',
                **inc_data,
            )
            incidents.append(incident)

            # Create a warning for each incident
            warning = WarningRecord.all_objects.create(
                tenant=tenant,
                incident=incident,
                employee=emp,
                warning_type=warning_types[i % len(warning_types)],
                issued_date=incident.incident_date + timedelta(days=random.randint(1, 7)),
                issued_by=employees[0],
                reason=f'Warning issued due to {inc_data["incident_type"].replace("_", " ")} incident.',
                action_required='Employee must attend counseling session and submit improvement plan.',
                deadline=incident.incident_date + timedelta(days=30),
                status=random.choice(warning_statuses),
            )

            # Create an appeal for some warnings
            if i >= 2:
                DisciplinaryAppeal.all_objects.create(
                    tenant=tenant,
                    warning=warning,
                    employee=emp,
                    appeal_date=warning.issued_date + timedelta(days=random.randint(3, 10)),
                    grounds='Employee disputes the characterization of the incident and presents mitigating circumstances.',
                    supporting_documents='Written statement from employee; character references from team members.',
                    reviewed_by=employees[0],
                    review_date=warning.issued_date + timedelta(days=random.randint(14, 21)) if i == 3 else None,
                    decision=random.choice(['pending', 'upheld', 'modified']),
                    decision_notes='Appeal reviewed by HR committee.' if i == 3 else '',
                )

        self.stdout.write(f'  Created {len(incidents)} disciplinary incidents with warnings and appeals.')

    # -----------------------------------------------------------------------
    # Grievances & Investigations
    # -----------------------------------------------------------------------
    def _seed_grievances(self, tenant, employees):
        if Grievance.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Grievances already exist, skipping...')
            return

        today = date.today()
        grievances_data = [
            {
                'category': 'compensation',
                'subject': 'Delayed salary increment',
                'description': 'Annual salary increment was promised during appraisal but has not been reflected '
                               'in payroll for the past 3 months despite multiple follow-ups with HR.',
                'priority': 'high',
            },
            {
                'category': 'workplace',
                'subject': 'Inadequate workstation facilities',
                'description': 'The air conditioning in the east wing has been non-functional for two weeks, '
                               'affecting productivity and employee comfort.',
                'priority': 'medium',
            },
            {
                'category': 'management',
                'subject': 'Unfair task distribution',
                'description': 'Workload is being disproportionately assigned to certain team members while '
                               'others have significantly fewer responsibilities.',
                'priority': 'medium',
            },
            {
                'category': 'harassment',
                'subject': 'Hostile behavior by supervisor',
                'description': 'Employee reports repeated instances of belittling comments and unreasonable '
                               'demands from direct supervisor, creating a hostile work environment.',
                'priority': 'critical',
                'is_anonymous': True,
            },
        ]

        grievance_statuses = ['registered', 'under_investigation', 'resolved', 'closed']
        investigation_statuses = ['pending', 'in_progress', 'completed']

        for i, grv_data in enumerate(grievances_data):
            is_anon = grv_data.pop('is_anonymous', False)
            emp = employees[i + 1] if i + 1 < len(employees) else random.choice(employees[1:])
            grv_date = today - timedelta(days=random.randint(5, 120))
            grievance = Grievance.all_objects.create(
                tenant=tenant,
                employee=emp,
                grievance_date=grv_date,
                status=grievance_statuses[i],
                assigned_to=employees[0],
                resolution_date=grv_date + timedelta(days=random.randint(15, 45)) if i >= 2 else None,
                resolution_summary='Issue addressed and resolved satisfactorily.' if i >= 2 else '',
                is_anonymous=is_anon,
                **grv_data,
            )

            # Create investigation for non-trivial grievances
            if i >= 1:
                inv_start = grv_date + timedelta(days=random.randint(1, 5))
                GrievanceInvestigation.all_objects.create(
                    tenant=tenant,
                    grievance=grievance,
                    investigator=employees[0],
                    start_date=inv_start,
                    end_date=inv_start + timedelta(days=random.randint(7, 21)) if i >= 2 else None,
                    findings='Investigation findings documented after interviews with involved parties.' if i >= 2 else '',
                    evidence='Witness statements collected; email correspondence reviewed.' if i >= 2 else '',
                    recommendation='Implement corrective measures and schedule follow-up.' if i >= 2 else '',
                    status=investigation_statuses[i - 1],
                )

        self.stdout.write(f'  Created {len(grievances_data)} grievances with investigations.')

    # -----------------------------------------------------------------------
    # Statutory Registers: Muster Rolls, Wage Registers, Inspection Reports
    # -----------------------------------------------------------------------
    def _seed_statutory_registers(self, tenant, employees, departments):
        if MusterRoll.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Statutory registers already exist, skipping...')
            return

        today = date.today()

        # Muster Rolls - last 3 months
        for offset in range(3):
            m_date = today - timedelta(days=30 * offset)
            month = m_date.month
            year = m_date.year
            dept = departments[offset % len(departments)] if departments else None
            MusterRoll.all_objects.create(
                tenant=tenant,
                month=month,
                year=year,
                department=dept,
                generated_date=date(year, month, 1) + timedelta(days=27),
                generated_by=employees[0],
                total_employees=random.randint(20, 80),
                total_working_days=random.choice([22, 23, 24, 25, 26]),
                notes=f'Muster roll for {month}/{year}.',
                status='final' if offset > 0 else 'draft',
            )

        self.stdout.write(f'  Created 3 muster rolls.')

        # Wage Registers - last 3 months
        for offset in range(3):
            m_date = today - timedelta(days=30 * offset)
            month = m_date.month
            year = m_date.year
            dept = departments[offset % len(departments)] if departments else None
            gross = Decimal(random.randint(500000, 2000000))
            deductions = gross * Decimal('0.18')
            WageRegister.all_objects.create(
                tenant=tenant,
                month=month,
                year=year,
                department=dept,
                generated_date=date(year, month, 1) + timedelta(days=27),
                generated_by=employees[0],
                total_gross=gross,
                total_deductions=deductions.quantize(Decimal('0.01')),
                total_net=(gross - deductions).quantize(Decimal('0.01')),
                notes=f'Wage register for {month}/{year}.',
                status='final' if offset > 0 else 'draft',
            )

        self.stdout.write(f'  Created 3 wage registers.')

        # Inspection Reports
        inspection_data = [
            {
                'inspector_name': 'R. Sharma, Labor Inspector',
                'inspector_designation': 'Senior Labor Inspector',
                'inspection_type': 'routine',
                'areas_inspected': 'Wage records, working hours compliance, safety equipment.',
                'findings': 'All records maintained properly; minor discrepancy in overtime records for 2 employees.',
                'compliance_status': 'compliant',
                'recommendations': 'Update overtime tracking system to prevent future discrepancies.',
                'status': 'closed',
            },
            {
                'inspector_name': 'K. Patel, Safety Officer',
                'inspector_designation': 'Occupational Safety Inspector',
                'inspection_type': 'surprise',
                'areas_inspected': 'Fire exits, safety equipment, first aid kits, emergency protocols.',
                'findings': 'Fire exit on 2nd floor partially blocked; 3 fire extinguishers past expiry date.',
                'compliance_status': 'non_compliant',
                'recommendations': 'Clear fire exits immediately; replace expired fire extinguishers within 7 days.',
                'status': 'follow_up_required',
            },
            {
                'inspector_name': 'M. Singh, Compliance Auditor',
                'inspector_designation': 'Regional Compliance Auditor',
                'inspection_type': 'follow_up',
                'areas_inspected': 'Previously identified non-compliance items; updated safety measures.',
                'findings': 'All previously identified issues have been addressed. Fire exits cleared; extinguishers replaced.',
                'compliance_status': 'compliant',
                'recommendations': 'Continue regular safety audits. Schedule next routine inspection.',
                'status': 'completed',
            },
        ]

        for i, insp_data in enumerate(inspection_data):
            insp_date = today - timedelta(days=random.randint(10, 120))
            dept = departments[i % len(departments)] if departments else None
            InspectionReport.all_objects.create(
                tenant=tenant,
                inspection_date=insp_date,
                department=dept,
                follow_up_date=insp_date + timedelta(days=30) if insp_data['status'] == 'follow_up_required' else None,
                notes='',
                **insp_data,
            )

        self.stdout.write(f'  Created 3 inspection reports.')
