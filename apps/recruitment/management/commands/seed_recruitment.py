import random
from datetime import timedelta, date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.core.models import Tenant, set_current_tenant
from apps.organization.models import Department, Designation
from apps.employees.models import Employee
from apps.recruitment.models import (
    JobTemplate, JobRequisition, RequisitionApproval,
    Candidate, JobApplication,
    InterviewRound, Interview, InterviewFeedback,
    OfferLetter,
)

fake = Faker()

# ---------------------------------------------------------------------------
# Realistic job data
# ---------------------------------------------------------------------------

JOB_TEMPLATES = [
    {
        'title': 'Software Engineer',
        'description': (
            'We are looking for a skilled Software Engineer to join our development team. '
            'You will be responsible for designing, developing, and maintaining software '
            'applications that meet business requirements.'
        ),
        'requirements': (
            '- Bachelor\'s degree in Computer Science or related field\n'
            '- 2+ years of experience in software development\n'
            '- Proficiency in Python, JavaScript, or Java\n'
            '- Experience with web frameworks (Django, React, etc.)\n'
            '- Strong problem-solving and communication skills'
        ),
        'responsibilities': (
            '- Write clean, maintainable, and efficient code\n'
            '- Participate in code reviews and technical discussions\n'
            '- Collaborate with cross-functional teams\n'
            '- Debug and resolve technical issues\n'
            '- Contribute to system design and architecture decisions'
        ),
        'benefits': (
            '- Competitive salary and annual bonus\n'
            '- Health, dental, and vision insurance\n'
            '- Flexible work arrangements\n'
            '- Professional development budget\n'
            '- Paid time off and holidays'
        ),
    },
    {
        'title': 'Product Manager',
        'description': (
            'We are seeking an experienced Product Manager to lead product strategy and '
            'roadmap. You will work closely with engineering, design, and business teams '
            'to deliver impactful products.'
        ),
        'requirements': (
            '- Bachelor\'s degree in Business, Engineering, or related field\n'
            '- 3+ years of product management experience\n'
            '- Strong analytical and data-driven decision making\n'
            '- Excellent communication and stakeholder management\n'
            '- Experience with agile methodologies'
        ),
        'responsibilities': (
            '- Define product vision, strategy, and roadmap\n'
            '- Gather and prioritize product requirements\n'
            '- Work with engineering to deliver features on time\n'
            '- Analyze market trends and competition\n'
            '- Present product updates to stakeholders'
        ),
        'benefits': (
            '- Competitive compensation package\n'
            '- Stock options / equity\n'
            '- Health and wellness benefits\n'
            '- Remote work flexibility\n'
            '- Leadership development programs'
        ),
    },
    {
        'title': 'UX Designer',
        'description': (
            'We are looking for a creative UX Designer to craft intuitive and engaging '
            'user experiences. You will conduct user research, create wireframes, and '
            'design high-fidelity prototypes.'
        ),
        'requirements': (
            '- Bachelor\'s degree in Design, HCI, or related field\n'
            '- 2+ years of UX design experience\n'
            '- Proficiency in Figma, Sketch, or Adobe XD\n'
            '- Strong portfolio demonstrating design process\n'
            '- Understanding of accessibility standards'
        ),
        'responsibilities': (
            '- Conduct user research and usability testing\n'
            '- Create wireframes, prototypes, and design specs\n'
            '- Collaborate with developers for implementation\n'
            '- Maintain and evolve the design system\n'
            '- Advocate for user-centered design principles'
        ),
        'benefits': '',
    },
    {
        'title': 'Data Analyst',
        'description': (
            'We are hiring a Data Analyst to turn raw data into actionable insights. '
            'You will build dashboards, run analyses, and support data-driven decision '
            'making across the organization.'
        ),
        'requirements': (
            '- Bachelor\'s degree in Statistics, Mathematics, or related field\n'
            '- Experience with SQL, Python, and BI tools (Tableau, Power BI)\n'
            '- Strong analytical thinking and attention to detail\n'
            '- Ability to communicate insights to non-technical audiences\n'
            '- Knowledge of statistical methods and data modeling'
        ),
        'responsibilities': (
            '- Analyze large datasets to identify trends and patterns\n'
            '- Build and maintain dashboards and reports\n'
            '- Support business teams with ad-hoc analysis\n'
            '- Ensure data quality and integrity\n'
            '- Document data processes and methodologies'
        ),
        'benefits': '',
    },
    {
        'title': 'HR Business Partner',
        'description': (
            'We are looking for an experienced HR Business Partner to support our growing '
            'teams. You will act as a strategic advisor on people-related matters, including '
            'talent management, employee relations, and organizational development.'
        ),
        'requirements': (
            '- Bachelor\'s degree in Human Resources or related field\n'
            '- 4+ years of HR experience\n'
            '- Strong knowledge of labor laws and HR best practices\n'
            '- Excellent interpersonal and conflict resolution skills\n'
            '- SHRM-CP or PHR certification preferred'
        ),
        'responsibilities': (
            '- Partner with managers on workforce planning\n'
            '- Handle employee relations issues and investigations\n'
            '- Drive performance management processes\n'
            '- Support recruitment and onboarding efforts\n'
            '- Lead HR initiatives and change management'
        ),
        'benefits': '',
    },
    {
        'title': 'DevOps Engineer',
        'description': (
            'We are seeking a DevOps Engineer to build and maintain our CI/CD pipelines, '
            'cloud infrastructure, and monitoring systems. You will work to improve '
            'developer productivity and system reliability.'
        ),
        'requirements': (
            '- Bachelor\'s degree in Computer Science or equivalent experience\n'
            '- 3+ years of DevOps/SRE experience\n'
            '- Proficiency with AWS, GCP, or Azure\n'
            '- Experience with Docker, Kubernetes, and Terraform\n'
            '- Strong scripting skills (Bash, Python)'
        ),
        'responsibilities': (
            '- Design and manage CI/CD pipelines\n'
            '- Automate infrastructure provisioning\n'
            '- Monitor system performance and reliability\n'
            '- Implement security best practices\n'
            '- Collaborate with development teams on deployments'
        ),
        'benefits': '',
    },
]

JOB_TITLES = [
    'Senior Software Engineer', 'Frontend Developer', 'Backend Developer',
    'Full Stack Developer', 'Mobile Developer', 'QA Engineer',
    'Product Manager', 'Senior Product Manager', 'UX Designer',
    'UI Developer', 'Data Analyst', 'Data Scientist',
    'HR Business Partner', 'Recruiter', 'Marketing Manager',
    'Sales Executive', 'Finance Analyst', 'DevOps Engineer',
    'Cloud Architect', 'Technical Lead', 'Engineering Manager',
    'Content Writer', 'Customer Success Manager', 'Operations Analyst',
]

LOCATIONS = [
    'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Chicago, IL',
    'Seattle, WA', 'Boston, MA', 'Denver, CO', 'Remote',
    'Los Angeles, CA', 'Atlanta, GA', 'Miami, FL', 'Portland, OR',
]

SKILLS_POOL = [
    'Python', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue.js',
    'Django', 'Flask', 'Node.js', 'Java', 'Spring Boot', 'C#', '.NET',
    'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
    'AWS', 'GCP', 'Azure', 'Git', 'CI/CD', 'Agile', 'Scrum',
    'Machine Learning', 'Data Analysis', 'Tableau', 'Power BI',
    'Figma', 'Sketch', 'Adobe XD', 'HTML', 'CSS', 'SASS',
    'REST APIs', 'GraphQL', 'Microservices', 'System Design',
    'Project Management', 'Communication', 'Leadership', 'Problem Solving',
]

COMPANIES = [
    'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix',
    'Salesforce', 'Adobe', 'Spotify', 'Uber', 'Airbnb', 'Stripe',
    'Shopify', 'Slack', 'Zoom', 'Atlassian', 'Twilio', 'Square',
    'Infosys', 'TCS', 'Wipro', 'HCL', 'Tech Mahindra', 'Cognizant',
    'Accenture', 'Deloitte', 'KPMG', 'PwC', 'EY', 'McKinsey',
]

DESIGNATIONS_POOL = [
    'Software Engineer', 'Senior Software Engineer', 'Lead Engineer',
    'Product Manager', 'Associate Product Manager', 'Senior PM',
    'Data Analyst', 'Business Analyst', 'UX Designer', 'UI Developer',
    'QA Analyst', 'DevOps Engineer', 'System Administrator',
    'HR Executive', 'Recruiter', 'Marketing Specialist',
    'Account Manager', 'Sales Representative', 'Operations Coordinator',
]

INTERVIEW_LOCATIONS = [
    'Conference Room A', 'Conference Room B', 'Meeting Room 1',
    'Meeting Room 2', 'Board Room', 'HR Office',
]

VIDEO_LINKS = [
    'https://meet.google.com/abc-defg-hij',
    'https://zoom.us/j/123456789',
    'https://teams.microsoft.com/l/meetup/abc123',
]

ROUND_NAMES = [
    ('Phone Screening', 1),
    ('Technical Round 1', 2),
    ('Technical Round 2', 3),
    ('System Design', 4),
    ('HR Round', 5),
    ('Managerial Round', 6),
    ('Culture Fit', 7),
]

STRENGTHS = [
    'Strong problem-solving skills and analytical thinking',
    'Excellent communication and presentation abilities',
    'Deep technical knowledge and hands-on experience',
    'Good cultural fit with team values',
    'Strong leadership potential and initiative',
    'Quick learner with adaptable mindset',
    'Solid understanding of system design principles',
    'Great collaboration and teamwork skills',
]

WEAKNESSES = [
    'Could improve on time management skills',
    'Needs more experience with distributed systems',
    'Could benefit from stronger presentation skills',
    'Limited experience with cloud technologies',
    'Would benefit from more leadership experience',
    'Needs to develop deeper domain knowledge',
    'Could improve debugging and troubleshooting speed',
    'Relatively less experience for the role level',
]

BENEFITS_TEXT = (
    '- Competitive base salary + annual performance bonus\n'
    '- Health, dental, and vision insurance\n'
    '- 401(k) retirement plan with company match\n'
    '- Flexible work hours and remote work options\n'
    '- Professional development budget ($2,000/year)\n'
    '- Paid parental leave\n'
    '- Gym membership reimbursement'
)

TERMS_TEXT = (
    '1. This offer is contingent upon successful completion of background verification.\n'
    '2. You will be subject to the company\'s employment policies and code of conduct.\n'
    '3. This offer is valid for 7 days from the date of issuance.\n'
    '4. The probation period is as mentioned above, during which either party may '
    'terminate employment with 15 days written notice.\n'
    '5. Post probation, a 30-day notice period applies for resignation.'
)


class Command(BaseCommand):
    help = 'Seed the database with recruitment module data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--candidates', type=int, default=30,
            help='Number of candidates per tenant (default: 30)'
        )
        parser.add_argument(
            '--jobs', type=int, default=10,
            help='Number of job requisitions per tenant (default: 10)'
        )

    def handle(self, *args, **options):
        num_candidates = options['candidates']
        num_jobs = options['jobs']

        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR(
                'No tenants found. Run "python manage.py seed_data" first.'
            ))
            return

        self.stdout.write('Seeding recruitment data...\n')

        for tenant in tenants:
            set_current_tenant(tenant)
            self.stdout.write(f'  Tenant: {tenant.name}')

            departments = list(Department.objects.filter(tenant=tenant))
            designations = list(Designation.objects.filter(tenant=tenant))
            employees = list(Employee.objects.filter(tenant=tenant, status='active'))

            if not departments or not employees:
                self.stdout.write(self.style.WARNING(
                    f'    Skipping - no departments or employees found'
                ))
                continue

            templates = self._create_job_templates(tenant)
            self.stdout.write(f'    Created {len(templates)} job templates')

            jobs = self._create_job_requisitions(
                tenant, departments, designations, employees, num_jobs
            )
            self.stdout.write(f'    Created {len(jobs)} job requisitions')

            self._create_approvals(tenant, jobs, employees)

            rounds = self._create_interview_rounds(tenant, jobs)
            self.stdout.write(f'    Created interview rounds for {len(rounds)} jobs')

            candidates = self._create_candidates(tenant, num_candidates)
            self.stdout.write(f'    Created {len(candidates)} candidates')

            applications = self._create_applications(tenant, jobs, candidates)
            self.stdout.write(f'    Created {len(applications)} applications')

            interviews = self._create_interviews(
                tenant, applications, rounds, employees
            )
            self.stdout.write(f'    Created {len(interviews)} interviews')

            feedbacks = self._create_feedback(tenant, interviews, employees)
            self.stdout.write(f'    Created {len(feedbacks)} interview feedbacks')

            offers = self._create_offers(
                tenant, applications, departments, employees
            )
            self.stdout.write(f'    Created {len(offers)} offer letters')

            self.stdout.write(f'    Completed: {tenant.name}\n')

        set_current_tenant(None)
        self.stdout.write(self.style.SUCCESS('\nRecruitment data seeded successfully!'))

    # ------------------------------------------------------------------
    # Job Templates
    # ------------------------------------------------------------------
    def _create_job_templates(self, tenant):
        templates = []
        for data in JOB_TEMPLATES:
            templates.append(JobTemplate.objects.create(
                tenant=tenant,
                title=data['title'],
                description=data['description'],
                requirements=data['requirements'],
                responsibilities=data['responsibilities'],
                benefits=data['benefits'],
                is_active=True,
            ))
        return templates

    # ------------------------------------------------------------------
    # Job Requisitions
    # ------------------------------------------------------------------
    def _create_job_requisitions(self, tenant, departments, designations, employees, count):
        jobs = []
        statuses = ['draft', 'pending_approval', 'approved', 'published',
                     'published', 'published', 'on_hold', 'closed']
        priorities = ['low', 'medium', 'medium', 'high', 'urgent']
        emp_types = ['full_time', 'full_time', 'full_time', 'part_time', 'contract', 'intern']

        for i in range(count):
            title = random.choice(JOB_TITLES)
            dept = random.choice(departments)
            desig = random.choice(designations) if designations else None
            status = random.choice(statuses)
            location = random.choice(LOCATIONS)
            emp_type = random.choice(emp_types)
            exp_min = random.choice([0, 1, 2, 3, 5])
            exp_max = exp_min + random.randint(2, 5)
            sal_min = Decimal(str(random.randint(40, 150) * 1000))
            sal_max = sal_min + Decimal(str(random.randint(10, 50) * 1000))
            positions = random.randint(1, 5)
            filled = random.randint(0, positions - 1) if status == 'closed' else 0

            publish_date = None
            closing_date = None
            is_published = False
            if status in ('published', 'closed'):
                publish_date = fake.date_between(start_date='-90d', end_date='-10d')
                closing_date = publish_date + timedelta(days=random.randint(30, 90))
                is_published = True
            elif status == 'approved':
                publish_date = fake.date_between(start_date='-30d', end_date='today')

            requested_by = random.choice(employees) if employees else None
            approved_by = random.choice(employees) if status not in ('draft', 'pending_approval') else None

            desc_lines = [
                f'We are looking for a talented {title} to join our {dept.name} team.',
                f'This is an exciting opportunity to work on challenging projects.',
                fake.paragraph(nb_sentences=3),
            ]

            req_lines = [
                f'- {random.randint(2, 8)}+ years of relevant experience',
                f'- Bachelor\'s degree in a relevant field',
                f'- {random.choice(SKILLS_POOL)} proficiency',
                f'- {random.choice(SKILLS_POOL)} experience',
                f'- Strong communication and teamwork skills',
            ]

            job = JobRequisition.objects.create(
                tenant=tenant,
                title=title,
                code=f'JR-{tenant.slug[:4].upper()}-{i+1:03d}',
                department=dept,
                designation=desig,
                location=location,
                employment_type=emp_type,
                experience_min=exp_min,
                experience_max=exp_max,
                salary_min=sal_min,
                salary_max=sal_max,
                description='\n'.join(desc_lines),
                requirements='\n'.join(req_lines),
                responsibilities=(
                    f'- Lead and contribute to {dept.name} projects\n'
                    f'- Collaborate with cross-functional teams\n'
                    f'- Mentor junior team members\n'
                    f'- Participate in planning and estimation\n'
                    f'- Maintain documentation and best practices'
                ),
                benefits=BENEFITS_TEXT if random.random() > 0.3 else '',
                positions=positions,
                filled_positions=filled,
                status=status,
                priority=random.choice(priorities),
                requested_by=requested_by,
                approved_by=approved_by,
                publish_date=publish_date,
                closing_date=closing_date,
                is_published=is_published,
            )
            jobs.append(job)

        return jobs

    # ------------------------------------------------------------------
    # Requisition Approvals
    # ------------------------------------------------------------------
    def _create_approvals(self, tenant, jobs, employees):
        for job in jobs:
            if job.status in ('draft',):
                continue
            managers = [e for e in employees
                        if e.designation and e.designation.job_grade
                        and e.designation.job_grade.level >= 5]
            if not managers:
                managers = employees[:3]

            approver = random.choice(managers)
            approval_status = 'approved'
            if job.status == 'pending_approval':
                approval_status = 'pending'
            elif job.status == 'cancelled':
                approval_status = 'rejected'

            RequisitionApproval.objects.create(
                tenant=tenant,
                requisition=job,
                approver=approver,
                level=1,
                status=approval_status,
                comments=fake.sentence() if approval_status != 'pending' else '',
                acted_on=timezone.now() - timedelta(days=random.randint(1, 30))
                if approval_status != 'pending' else None,
            )

    # ------------------------------------------------------------------
    # Interview Rounds
    # ------------------------------------------------------------------
    def _create_interview_rounds(self, tenant, jobs):
        rounds_map = {}
        published_jobs = [j for j in jobs if j.status in ('published', 'approved', 'closed')]

        for job in published_jobs:
            num_rounds = random.randint(2, 4)
            selected_rounds = random.sample(ROUND_NAMES, min(num_rounds, len(ROUND_NAMES)))
            selected_rounds.sort(key=lambda r: r[1])

            rounds = []
            for idx, (name, _) in enumerate(selected_rounds):
                rounds.append(InterviewRound.objects.create(
                    tenant=tenant,
                    requisition=job,
                    name=name,
                    round_number=idx + 1,
                    description=f'{name} for {job.title}',
                    is_active=True,
                ))
            rounds_map[job.pk] = rounds

        return rounds_map

    # ------------------------------------------------------------------
    # Candidates
    # ------------------------------------------------------------------
    def _create_candidates(self, tenant, count):
        candidates = []
        sources = ['career_page', 'referral', 'job_portal', 'social_media',
                    'recruitment_agency', 'direct', 'other']

        for _ in range(count):
            exp = round(random.uniform(0, 15), 1)
            current_sal = Decimal(str(random.randint(30, 200) * 1000)) if exp > 1 else None
            expected_sal = (
                current_sal * Decimal(str(random.uniform(1.1, 1.4)))
            ).quantize(Decimal('1')) if current_sal else Decimal(str(random.randint(35, 80) * 1000))

            num_skills = random.randint(3, 8)
            skills = ', '.join(random.sample(SKILLS_POOL, num_skills))

            candidate = Candidate.objects.create(
                tenant=tenant,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number()[:20],
                current_company=random.choice(COMPANIES) if exp > 1 else '',
                current_designation=random.choice(DESIGNATIONS_POOL) if exp > 1 else '',
                experience_years=Decimal(str(exp)),
                current_salary=current_sal,
                expected_salary=expected_sal,
                skills=skills,
                location=random.choice(LOCATIONS),
                linkedin_url=f'https://linkedin.com/in/{fake.user_name()}' if random.random() > 0.3 else '',
                source=random.choice(sources),
                notes=fake.sentence() if random.random() > 0.5 else '',
                is_active=random.random() > 0.1,
            )
            candidates.append(candidate)

        return candidates

    # ------------------------------------------------------------------
    # Job Applications
    # ------------------------------------------------------------------
    def _create_applications(self, tenant, jobs, candidates):
        applications = []
        app_statuses = ['applied', 'screening', 'shortlisted', 'interview',
                        'offered', 'hired', 'rejected', 'withdrawn']

        published_jobs = [j for j in jobs if j.status in ('published', 'closed')]
        if not published_jobs:
            published_jobs = jobs[:3]

        used_pairs = set()

        for job in published_jobs:
            num_applicants = random.randint(3, min(8, len(candidates)))
            job_candidates = random.sample(candidates, num_applicants)

            for candidate in job_candidates:
                pair = (job.pk, candidate.pk)
                if pair in used_pairs:
                    continue
                used_pairs.add(pair)

                status = random.choice(app_statuses)
                source = candidate.source

                app = JobApplication(
                    tenant=tenant,
                    job=job,
                    candidate=candidate,
                    cover_letter=fake.paragraph(nb_sentences=3) if random.random() > 0.4 else '',
                    status=status,
                    source=source,
                    notes=fake.sentence() if random.random() > 0.6 else '',
                    rating=random.randint(1, 5) if status not in ('applied',) else None,
                )
                app.save()
                applications.append(app)

        return applications

    # ------------------------------------------------------------------
    # Interviews
    # ------------------------------------------------------------------
    def _create_interviews(self, tenant, applications, rounds_map, employees):
        interviews = []
        interview_apps = [a for a in applications
                          if a.status in ('interview', 'offered', 'hired', 'shortlisted')]

        for app in interview_apps:
            job_rounds = rounds_map.get(app.job.pk, [])
            num_interviews = random.randint(1, min(3, max(len(job_rounds), 1)))

            for i in range(num_interviews):
                round_obj = job_rounds[i] if i < len(job_rounds) else None
                round_name = round_obj.name if round_obj else random.choice(ROUND_NAMES)[0]

                sched_date = fake.date_between(start_date='-60d', end_date='+14d')
                sched_time = time(
                    hour=random.choice([9, 10, 11, 14, 15, 16]),
                    minute=random.choice([0, 30]),
                )
                mode = random.choice(['in_person', 'phone', 'video'])

                if mode == 'video':
                    loc = random.choice(VIDEO_LINKS)
                elif mode == 'phone':
                    loc = ''
                else:
                    loc = random.choice(INTERVIEW_LOCATIONS)

                is_past = sched_date < date.today()
                if is_past:
                    status = random.choice(['completed', 'completed', 'completed', 'no_show'])
                    result = random.choice(['pass', 'pass', 'fail', 'on_hold']) if status == 'completed' else 'pending'
                else:
                    status = 'scheduled'
                    result = 'pending'

                interview = Interview.objects.create(
                    tenant=tenant,
                    application=app,
                    round=round_obj,
                    round_name=round_name,
                    scheduled_date=sched_date,
                    scheduled_time=sched_time,
                    duration_minutes=random.choice([30, 45, 60, 60, 90]),
                    location=loc,
                    mode=mode,
                    status=status,
                    notes=fake.sentence() if random.random() > 0.5 else '',
                    overall_rating=random.randint(2, 5) if status == 'completed' else None,
                    result=result,
                )

                # Assign 1-3 interviewers
                num_interviewers = random.randint(1, min(3, len(employees)))
                selected_interviewers = random.sample(employees, num_interviewers)
                interview.interviewers.set(selected_interviewers)

                interviews.append(interview)

        return interviews

    # ------------------------------------------------------------------
    # Interview Feedback
    # ------------------------------------------------------------------
    def _create_feedback(self, tenant, interviews, employees):
        feedbacks = []
        completed = [iv for iv in interviews if iv.status == 'completed']

        for interview in completed:
            interviewers = list(interview.interviewers.all())
            if not interviewers:
                interviewers = [random.choice(employees)]

            for interviewer in interviewers:
                recommendations = ['strong_hire', 'hire', 'hire', 'no_hire', 'strong_no_hire']

                feedback = InterviewFeedback.objects.create(
                    tenant=tenant,
                    interview=interview,
                    interviewer=interviewer,
                    technical_rating=random.randint(2, 5),
                    communication_rating=random.randint(2, 5),
                    cultural_fit_rating=random.randint(2, 5),
                    overall_rating=random.randint(2, 5),
                    strengths=random.choice(STRENGTHS),
                    weaknesses=random.choice(WEAKNESSES),
                    comments=fake.paragraph(nb_sentences=2),
                    recommendation=random.choice(recommendations),
                )
                feedbacks.append(feedback)

        return feedbacks

    # ------------------------------------------------------------------
    # Offer Letters
    # ------------------------------------------------------------------
    def _create_offers(self, tenant, applications, departments, employees):
        offers = []
        offered_apps = [a for a in applications
                        if a.status in ('offered', 'hired')]

        managers = [e for e in employees
                    if e.designation and e.designation.job_grade
                    and e.designation.job_grade.level >= 5]
        if not managers:
            managers = employees[:3]

        offer_statuses = ['draft', 'pending_approval', 'approved', 'sent',
                          'accepted', 'rejected', 'withdrawn']

        for app in offered_apps:
            sal_min = app.job.salary_min or Decimal('50000')
            sal_max = app.job.salary_max or Decimal('120000')
            offered_salary = Decimal(str(
                random.randint(int(sal_min), int(sal_max))
            ))

            status = 'accepted' if app.status == 'hired' else random.choice(offer_statuses)
            joining = fake.date_between(start_date='+15d', end_date='+90d')
            expiry = joining - timedelta(days=7)

            approved_by_emp = random.choice(managers)
            approved_date = (
                timezone.now() - timedelta(days=random.randint(1, 20))
            ) if status not in ('draft', 'pending_approval') else None

            response_date = (
                timezone.now() - timedelta(days=random.randint(1, 10))
            ) if status in ('accepted', 'rejected') else None

            offer = OfferLetter.objects.create(
                tenant=tenant,
                application=app,
                offered_designation=app.job.title,
                offered_department=app.job.department or random.choice(departments),
                offered_salary=offered_salary,
                salary_currency='USD',
                joining_date=joining,
                expiry_date=expiry,
                probation_months=random.choice([3, 6, 6]),
                benefits=BENEFITS_TEXT,
                terms_conditions=TERMS_TEXT,
                status=status,
                approved_by=approved_by_emp if approved_date else None,
                approved_date=approved_date,
                candidate_response_date=response_date,
                remarks=fake.sentence() if random.random() > 0.6 else '',
            )
            offers.append(offer)

        return offers
