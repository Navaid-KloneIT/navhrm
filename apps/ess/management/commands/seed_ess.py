import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.organization.models import Department
from apps.ess.models import (
    FamilyMember, DocumentRequest, IDCardRequest, AssetRequest,
    Announcement, BirthdayWish, Survey, SurveyQuestion, SurveyResponse,
    Suggestion, HelpDeskTicket, TicketComment,
)


class Command(BaseCommand):
    help = 'Seed employee self-service module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding ESS data for {tenant.name}...')
            employees = list(Employee.objects.filter(tenant=tenant, status='active'))
            departments = list(Department.objects.filter(tenant=tenant))

            if len(employees) < 2:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - not enough employees.'))
                continue

            self._seed_family_members(tenant, employees)
            self._seed_document_requests(tenant, employees)
            self._seed_idcard_requests(tenant, employees)
            self._seed_asset_requests(tenant, employees)
            self._seed_announcements(tenant, employees, departments)
            self._seed_birthday_wishes(tenant, employees)
            surveys = self._seed_surveys(tenant, employees, departments)
            self._seed_survey_responses(tenant, surveys, employees)
            self._seed_suggestions(tenant, employees)
            self._seed_helpdesk_tickets(tenant, employees)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding ESS data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('ESS data seeding complete!'))

    def _seed_family_members(self, tenant, employees):
        family_data = [
            ('Priya Sharma', 'spouse', 'female', 'Teacher'),
            ('Arjun Kumar', 'child', 'male', 'Student'),
            ('Meera Patel', 'spouse', 'female', 'Doctor'),
            ('Rahul Singh', 'child', 'male', 'Student'),
            ('Sunita Devi', 'parent', 'female', 'Retired'),
            ('Anil Gupta', 'parent', 'male', 'Retired'),
            ('Kavita Reddy', 'sibling', 'female', 'Engineer'),
            ('Neha Joshi', 'spouse', 'female', 'Accountant'),
        ]
        for i, emp in enumerate(employees[:6]):
            if emp.family_members.exists():
                continue
            members = random.sample(family_data, min(random.randint(1, 3), len(family_data)))
            for name, relationship, gender, occupation in members:
                FamilyMember.objects.create(
                    tenant=tenant, employee=emp, name=name,
                    relationship=relationship, gender=gender,
                    occupation=occupation,
                    date_of_birth=date(random.randint(1960, 2015), random.randint(1, 12), random.randint(1, 28)),
                    phone=f'+91-98{random.randint(10000000, 99999999)}',
                    is_dependent=relationship in ('spouse', 'child', 'parent'),
                    is_nominee=relationship == 'spouse',
                    nominee_percentage=100 if relationship == 'spouse' else 0,
                    covered_under_insurance=relationship in ('spouse', 'child'),
                )

    def _seed_document_requests(self, tenant, employees):
        doc_types = ['experience_letter', 'salary_certificate', 'employment_certificate',
                     'bonafide_letter', 'address_proof_letter']
        statuses = ['pending', 'processing', 'completed', 'completed', 'rejected']
        purposes = [
            'Required for visa application',
            'Needed for bank loan processing',
            'Required for apartment rental agreement',
            'Needed for higher education admission',
            'Required for government ID proof',
        ]
        for emp in employees[:5]:
            doc_type = random.choice(doc_types)
            status = random.choice(statuses)
            DocumentRequest.objects.get_or_create(
                tenant=tenant, employee=emp, document_type=doc_type,
                defaults={
                    'purpose': random.choice(purposes),
                    'status': status,
                    'copies_needed': random.randint(1, 3),
                    'delivery_method': random.choice(['email', 'print', 'both']),
                    'processed_by': random.choice(employees) if status in ('completed', 'rejected') else None,
                    'processed_at': timezone.now() if status in ('completed', 'rejected') else None,
                    'rejection_reason': 'Employee is still in probation period.' if status == 'rejected' else '',
                }
            )

    def _seed_idcard_requests(self, tenant, employees):
        request_types = ['new', 'replacement', 'renewal', 'update']
        statuses = ['pending', 'approved', 'processing', 'ready', 'delivered', 'rejected']
        reasons = [
            'Lost my ID card during office relocation',
            'ID card is damaged and not scannable',
            'ID card expired, need renewal',
            'Name change after marriage',
            'New employee, need first ID card',
        ]
        for i, emp in enumerate(employees[:4]):
            req_type = request_types[i % len(request_types)]
            status = random.choice(statuses)
            IDCardRequest.objects.get_or_create(
                tenant=tenant, employee=emp, request_type=req_type,
                defaults={
                    'reason': random.choice(reasons),
                    'status': status,
                    'processed_by': random.choice(employees) if status not in ('pending',) else None,
                    'processed_at': timezone.now() if status not in ('pending',) else None,
                    'delivered_at': timezone.now() if status == 'delivered' else None,
                }
            )

    def _seed_asset_requests(self, tenant, employees):
        asset_data = [
            ('laptop', 'MacBook Pro 16"', 'Need for development work with Docker containers'),
            ('monitor', 'Dell 27" 4K Monitor', 'Current monitor has dead pixels'),
            ('headset', 'Jabra Evolve2 75', 'Need noise-cancelling headset for virtual meetings'),
            ('keyboard_mouse', 'Logitech MX Master 3', 'Ergonomic setup for wrist pain'),
            ('access_card', 'Building Access Card', 'Lost building access card'),
            ('furniture', 'Standing Desk', 'Recommended by physiotherapist for back issues'),
        ]
        statuses = ['pending', 'approved', 'allocated', 'rejected', 'pending']
        for i, emp in enumerate(employees[:5]):
            asset_type, name, reason = asset_data[i % len(asset_data)]
            status = random.choice(statuses)
            AssetRequest.objects.get_or_create(
                tenant=tenant, employee=emp, asset_name=name,
                defaults={
                    'asset_type': asset_type,
                    'quantity': 1,
                    'reason': reason,
                    'priority': random.choice(['low', 'medium', 'high', 'urgent']),
                    'status': status,
                    'approved_by': random.choice(employees) if status in ('approved', 'allocated') else None,
                    'approved_at': timezone.now() if status in ('approved', 'allocated') else None,
                    'expected_date': date.today() + timedelta(days=random.randint(7, 30)),
                    'rejection_reason': 'Asset not available in inventory.' if status == 'rejected' else '',
                }
            )

    def _seed_announcements(self, tenant, employees, departments):
        now = timezone.now()
        announcement_data = [
            ('Annual Company Outing - March 2026', 'general', 'high', True,
             'We are excited to announce our annual company outing scheduled for March 15, 2026. '
             'The event will be held at Resort Valley. All employees are invited with their families. '
             'Please RSVP by March 1st through the HR portal.'),
            ('Updated Work From Home Policy', 'policy', 'urgent', True,
             'Effective from April 1, 2026, the company is introducing a hybrid work model. '
             'Employees can work from home up to 3 days per week. Please review the detailed policy '
             'document attached and discuss with your manager.'),
            ('Server Maintenance - Feb 28', 'maintenance', 'normal', False,
             'Scheduled server maintenance will take place on February 28, 2026 from 11 PM to 3 AM IST. '
             'All internal systems including email and HR portal will be temporarily unavailable.'),
            ('Employee of the Month - January 2026', 'achievement', 'normal', False,
             'Congratulations to our Employee of the Month! Your dedication and hard work have been '
             'recognized by the team. Keep up the excellent work!'),
            ('Holi Holiday Notice', 'holiday', 'normal', False,
             'The office will remain closed on March 14, 2026 (Friday) on account of Holi. '
             'Wishing everyone a colorful and joyful Holi!'),
            ('New Health Insurance Benefits', 'policy', 'high', True,
             'We have upgraded our group health insurance plan with enhanced coverage. '
             'Key changes include increased sum insured, dental coverage, and OPD benefits. '
             'Details will be shared in the upcoming town hall.'),
        ]
        for title, category, priority, pinned, content in announcement_data:
            ann, _ = Announcement.objects.get_or_create(
                tenant=tenant, title=title,
                defaults={
                    'content': content,
                    'category': category,
                    'priority': priority,
                    'published_by': random.choice(employees),
                    'publish_date': now - timedelta(days=random.randint(0, 30)),
                    'expiry_date': now + timedelta(days=random.randint(30, 90)),
                    'is_pinned': pinned,
                    'is_active': True,
                }
            )
            if departments and not ann.target_departments.exists():
                if random.random() < 0.3:
                    ann.target_departments.set(random.sample(departments, min(2, len(departments))))

    def _seed_birthday_wishes(self, tenant, employees):
        today = date.today()
        for emp in employees[:4]:
            wishers = random.sample([e for e in employees if e != emp], min(2, len(employees) - 1))
            for wisher in wishers:
                messages = [
                    'Happy Birthday! Wishing you a wonderful year ahead!',
                    'Many happy returns of the day! Hope you have a fantastic birthday!',
                    'Wishing you a very happy birthday! May all your dreams come true!',
                    'Happy Birthday! Thank you for being an amazing colleague!',
                ]
                try:
                    BirthdayWish.objects.get_or_create(
                        tenant=tenant, employee=emp, wished_by=wisher,
                        occasion='birthday', occasion_date=today,
                        defaults={'message': random.choice(messages)}
                    )
                except Exception:
                    pass

    def _seed_surveys(self, tenant, employees, departments):
        survey_data = [
            ('Employee Satisfaction Survey Q1 2026', 'active',
             'Help us understand your experience at the company. Your responses are anonymous.',
             [
                 ('How satisfied are you with your overall work experience?', 'rating', '', True),
                 ('How would you rate the communication from management?', 'rating', '', True),
                 ('Do you feel your work is recognized and appreciated?', 'yes_no', '', True),
                 ('What aspect of the workplace would you most like to improve?', 'single_choice',
                  'Work-life balance|Career growth|Compensation|Work environment|Team collaboration', True),
                 ('Any additional comments or suggestions?', 'text', '', False),
             ]),
            ('Remote Work Feedback Survey', 'active',
             'Share your experience with the hybrid work model to help us improve.',
             [
                 ('How productive do you feel working from home?', 'rating', '', True),
                 ('Do you have adequate equipment for remote work?', 'yes_no', '', True),
                 ('What is your preferred work arrangement?', 'single_choice',
                  'Fully remote|Hybrid (3 days office)|Hybrid (2 days office)|Fully in-office', True),
                 ('What challenges do you face with remote work?', 'multiple_choice',
                  'Internet connectivity|Distractions at home|Communication gaps|Isolation|Equipment issues', True),
             ]),
            ('Training Needs Assessment', 'closed',
             'Help us plan training programs for the next quarter.',
             [
                 ('Which area would you most like to develop?', 'single_choice',
                  'Technical skills|Leadership|Communication|Project management|Domain knowledge', True),
                 ('Rate the effectiveness of past training programs.', 'rating', '', True),
                 ('Would you be interested in mentorship programs?', 'yes_no', '', True),
             ]),
        ]
        surveys = []
        today = date.today()
        for title, status, description, questions in survey_data:
            survey, created = Survey.objects.get_or_create(
                tenant=tenant, title=title,
                defaults={
                    'description': description,
                    'status': status,
                    'created_by': random.choice(employees),
                    'start_date': today - timedelta(days=random.randint(1, 30)),
                    'end_date': today + timedelta(days=random.randint(7, 60)) if status == 'active' else today - timedelta(days=1),
                    'is_anonymous': True,
                }
            )
            surveys.append(survey)
            if created:
                for order, (q_text, q_type, choices, required) in enumerate(questions, 1):
                    SurveyQuestion.objects.create(
                        tenant=tenant, survey=survey,
                        question_text=q_text, question_type=q_type,
                        choices=choices, is_required=required, order=order,
                    )
        return surveys

    def _seed_survey_responses(self, tenant, surveys, employees):
        for survey in surveys:
            if survey.responses.exists():
                continue
            questions = list(survey.questions.all())
            if not questions:
                continue
            respondents = random.sample(employees, min(4, len(employees)))
            for emp in respondents:
                for question in questions:
                    answer_text = ''
                    answer_rating = None
                    if question.question_type == 'rating':
                        answer_rating = random.randint(3, 5)
                    elif question.question_type == 'yes_no':
                        answer_text = random.choice(['Yes', 'No'])
                    elif question.question_type in ('single_choice', 'multiple_choice'):
                        choices = question.get_choices_list()
                        if choices:
                            if question.question_type == 'multiple_choice':
                                answer_text = '|'.join(random.sample(choices, min(2, len(choices))))
                            else:
                                answer_text = random.choice(choices)
                    elif question.question_type == 'text':
                        answer_text = random.choice([
                            'Great initiative, keep it up!',
                            'Would appreciate more team building activities.',
                            'Overall satisfied with the work environment.',
                            'Need better parking facilities.',
                        ])
                    try:
                        SurveyResponse.objects.get_or_create(
                            tenant=tenant, survey=survey,
                            question=question, respondent=emp,
                            defaults={
                                'answer_text': answer_text,
                                'answer_rating': answer_rating,
                            }
                        )
                    except Exception:
                        pass

    def _seed_suggestions(self, tenant, employees):
        suggestion_data = [
            ('Implement Flexible Working Hours', 'workplace',
             'Allow employees to choose their work hours between 7 AM and 7 PM as long as they complete 8 hours.'),
            ('Introduce Pet-Friendly Fridays', 'culture',
             'Allow employees to bring their pets to office on Fridays. This can reduce stress and boost morale.'),
            ('Upgrade Cafeteria Menu', 'workplace',
             'The current cafeteria menu has been the same for months. Suggest rotating menus with healthier options.'),
            ('Automate Leave Approval Workflow', 'process',
             'Current leave approval process requires manual emails. An automated system would save time.'),
            ('Monthly Tech Talks', 'technology',
             'Organize monthly sessions where team members present on new technologies they are exploring.'),
            ('Green Initiative - Reduce Paper Usage', 'policy',
             'Replace all paper-based processes with digital alternatives. Start with visitor logs and expense reports.'),
        ]
        statuses = ['submitted', 'under_review', 'accepted', 'implemented', 'submitted', 'under_review']
        for i, (title, category, description) in enumerate(suggestion_data):
            emp = employees[i % len(employees)]
            status = statuses[i % len(statuses)]
            Suggestion.objects.get_or_create(
                tenant=tenant, title=title,
                defaults={
                    'employee': emp,
                    'category': category,
                    'description': description,
                    'is_anonymous': random.choice([True, False]),
                    'status': status,
                    'reviewed_by': random.choice(employees) if status in ('accepted', 'implemented') else None,
                    'reviewed_at': timezone.now() if status in ('accepted', 'implemented') else None,
                    'admin_response': 'Great idea! We will look into implementing this.' if status == 'accepted' else '',
                    'upvotes': random.randint(0, 25),
                }
            )

    def _seed_helpdesk_tickets(self, tenant, employees):
        ticket_data = [
            ('Salary slip not generated for January', 'payroll', 'high',
             'My salary slip for January 2026 is not showing in the payroll section. '
             'Please check and generate it.'),
            ('Leave balance mismatch', 'leave', 'medium',
             'My leave balance shows 8 days but I believe I should have 12 days. '
             'Could you please verify and correct?'),
            ('Health insurance card not received', 'benefits', 'medium',
             'I enrolled in the health insurance plan last month but have not yet received my insurance card. '
             'Please expedite.'),
            ('VPN access not working', 'it_support', 'urgent',
             'My VPN connection keeps timing out when trying to access internal systems from home. '
             'I have already restarted my laptop and router.'),
            ('AC not working in 3rd floor conference room', 'facilities', 'low',
             'The air conditioning in the 3rd floor conference room (CR-301) has not been working for the past week.'),
            ('Need clarification on new PF policy', 'policy', 'low',
             'The recent circular about changes to PF contribution is confusing. '
             'Could someone explain the impact on take-home salary?'),
        ]
        statuses = ['open', 'in_progress', 'resolved', 'waiting_on_employee', 'closed', 'open']
        comments_data = [
            'Thank you for raising this. We are looking into it.',
            'Could you please provide your employee ID for verification?',
            'The issue has been identified and a fix is in progress.',
            'This has been resolved. Please confirm if the issue persists.',
        ]
        for i, (subject, category, priority, description) in enumerate(ticket_data):
            emp = employees[i % len(employees)]
            status = statuses[i % len(statuses)]
            ticket, created = HelpDeskTicket.objects.get_or_create(
                tenant=tenant, subject=subject, employee=emp,
                defaults={
                    'category': category,
                    'description': description,
                    'priority': priority,
                    'status': status,
                    'assigned_to': random.choice(employees) if status != 'open' else None,
                    'resolved_at': timezone.now() if status in ('resolved', 'closed') else None,
                    'closed_at': timezone.now() if status == 'closed' else None,
                }
            )
            if created and status != 'open':
                hr_employee = random.choice(employees)
                for comment_msg in random.sample(comments_data, min(2, len(comments_data))):
                    TicketComment.objects.create(
                        tenant=tenant, ticket=ticket,
                        author=hr_employee, message=comment_msg,
                    )
