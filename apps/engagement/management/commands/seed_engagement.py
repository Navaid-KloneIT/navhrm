import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.engagement.models import (
    EngagementSurvey, EngagementSurveyQuestion, EngagementSurveyQuestionOption,
    EngagementSurveyResponse, EngagementSurveyAnswer, EngagementActionPlan,
    WellbeingProgram, WellbeingResource, WellnessChallenge, ChallengeParticipant,
    FlexibleWorkArrangement, RemoteWorkPolicy, WorkLifeBalanceAssessment,
    EAPProgram, CounselingSession, EAPUtilization,
    CompanyValue, CultureAssessment, CultureAssessmentResponse, ValueNomination,
    TeamEvent, EventParticipant, InterestGroup, InterestGroupMember,
    VolunteerActivity, VolunteerParticipant,
)


class Command(BaseCommand):
    help = 'Seed employee engagement & wellbeing module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding engagement data for {tenant.name}...')
            employees = list(Employee.all_objects.filter(tenant=tenant, status='active'))

            if len(employees) < 5:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - insufficient employees.'))
                continue

            self._seed_surveys(tenant, employees)
            self._seed_wellbeing_programs(tenant, employees)
            self._seed_work_life_balance(tenant, employees)
            self._seed_eap(tenant, employees)
            self._seed_culture_values(tenant, employees)
            self._seed_social_connect(tenant, employees)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding engagement data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Engagement & wellbeing module data seeding complete!'))

    # =========================================================================
    # SUB-MODULE 1: ENGAGEMENT SURVEYS
    # =========================================================================

    def _seed_surveys(self, tenant, employees):
        if EngagementSurvey.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Surveys already exist, skipping...')
            return

        survey_data = [
            ('Q1 2026 Pulse Survey', 'pulse', 'Quick check on team morale and engagement levels.'),
            ('Employee Net Promoter Score - March 2026', 'enps', 'How likely are you to recommend this company as a great place to work?'),
            ('Annual Engagement Survey 2026', 'engagement', 'Comprehensive annual survey covering all aspects of employee engagement.'),
            ('Remote Work Satisfaction Survey', 'custom', 'Understanding employee satisfaction with remote work arrangements.'),
        ]

        surveys = []
        for title, stype, desc in survey_data:
            start = date.today() - timedelta(days=random.randint(0, 60))
            survey = EngagementSurvey.all_objects.create(
                tenant=tenant,
                title=title,
                description=desc,
                survey_type=stype,
                status=random.choice(['draft', 'active', 'closed']),
                start_date=start,
                end_date=start + timedelta(days=random.randint(14, 45)),
                is_anonymous=random.choice([True, False]),
                target_audience=random.choice(['all', 'department', 'designation']),
                is_active=True,
            )
            surveys.append(survey)

        # Add questions to each survey
        question_sets = {
            'pulse': [
                ('How satisfied are you with your current role?', 'rating'),
                ('Do you feel valued by your manager?', 'yes_no'),
                ('What could we improve?', 'text'),
            ],
            'enps': [
                ('On a scale of 1-10, how likely are you to recommend this company?', 'scale'),
                ('What is the primary reason for your score?', 'text'),
            ],
            'engagement': [
                ('I feel motivated to go above and beyond at work.', 'rating'),
                ('I have the resources I need to do my job well.', 'rating'),
                ('My manager provides regular feedback.', 'rating'),
                ('I see a clear career path for myself here.', 'rating'),
                ('I feel a sense of belonging in my team.', 'rating'),
                ('What would make this a better workplace?', 'text'),
            ],
            'custom': [
                ('How productive do you feel working remotely?', 'rating'),
                ('Do you have a dedicated home office space?', 'yes_no'),
                ('What challenges do you face with remote work?', 'text'),
                ('Preferred work arrangement:', 'single_choice'),
            ],
        }

        for survey in surveys:
            questions_for_type = question_sets.get(survey.survey_type, [])
            for order, (q_text, q_type) in enumerate(questions_for_type, 1):
                question = EngagementSurveyQuestion.all_objects.create(
                    tenant=tenant,
                    survey=survey,
                    question_text=q_text,
                    question_type=q_type,
                    order=order,
                    is_required=True,
                )
                # Add options for single_choice questions
                if q_type == 'single_choice':
                    for opt_order, opt_text in enumerate(['Fully Remote', 'Hybrid (3 days office)', 'Hybrid (2 days office)', 'Fully In-Office'], 1):
                        EngagementSurveyQuestionOption.all_objects.create(
                            tenant=tenant,
                            question=question,
                            option_text=opt_text,
                            order=opt_order,
                        )

        # Add responses for active/closed surveys
        for survey in surveys:
            if survey.status in ('active', 'closed'):
                respondents = random.sample(employees, min(random.randint(3, 8), len(employees)))
                for emp in respondents:
                    response = EngagementSurveyResponse.all_objects.create(
                        tenant=tenant,
                        survey=survey,
                        employee=None if survey.is_anonymous else emp,
                        submitted_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                        is_complete=True,
                    )
                    for question in survey.questions.all():
                        answer_kwargs = {
                            'tenant': tenant,
                            'response': response,
                            'question': question,
                        }
                        if question.question_type == 'rating':
                            answer_kwargs['rating_value'] = random.randint(1, 5)
                        elif question.question_type == 'scale':
                            answer_kwargs['rating_value'] = random.randint(1, 10)
                        elif question.question_type == 'yes_no':
                            answer_kwargs['text_answer'] = random.choice(['Yes', 'No'])
                        elif question.question_type == 'text':
                            answer_kwargs['text_answer'] = random.choice([
                                'More team activities and social events.',
                                'Better communication from leadership.',
                                'More flexible work arrangements.',
                                'Career development opportunities.',
                                'Recognition for good work.',
                            ])
                        elif question.question_type == 'single_choice':
                            options = list(question.options.all())
                            if options:
                                answer_kwargs['selected_option'] = random.choice(options)
                        EngagementSurveyAnswer.all_objects.create(**answer_kwargs)

        # Add action plans
        action_plan_data = [
            ('Improve Manager Feedback Loop', 'Implement bi-weekly 1:1 meetings between managers and reports.'),
            ('Launch Recognition Program', 'Create peer-to-peer recognition system with rewards.'),
            ('Career Path Framework', 'Define clear career progression for all departments.'),
            ('Team Building Initiative', 'Monthly team activities to improve collaboration.'),
        ]

        for title, desc in action_plan_data:
            EngagementActionPlan.all_objects.create(
                tenant=tenant,
                survey=random.choice(surveys),
                title=title,
                description=desc,
                assigned_to=random.choice(employees),
                priority=random.choice(['low', 'medium', 'high', 'critical']),
                status=random.choice(['pending', 'in_progress', 'completed']),
                due_date=date.today() + timedelta(days=random.randint(14, 90)),
                is_active=True,
            )

        self.stdout.write('  Created 4 surveys with questions, responses, and action plans.')

    # =========================================================================
    # SUB-MODULE 2: WELLBEING PROGRAMS
    # =========================================================================

    def _seed_wellbeing_programs(self, tenant, employees):
        if WellbeingProgram.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Wellbeing programs already exist, skipping...')
            return

        program_data = [
            ('Mindfulness at Work', 'mindfulness', 'Weekly guided meditation sessions for stress reduction.'),
            ('Fitness Friday', 'physical_health', 'Group exercise sessions every Friday afternoon.'),
            ('Financial Wellness Workshop', 'financial', 'Monthly sessions on budgeting, investing, and retirement planning.'),
            ('Mental Health First Aid', 'mental_health', 'Training program to recognize and respond to mental health issues.'),
            ('Healthy Eating Challenge', 'nutrition', 'Month-long challenge to improve dietary habits.'),
            ('Social Connection Series', 'social', 'Regular social activities to build team bonds.'),
        ]

        for name, category, desc in program_data:
            start = date.today() - timedelta(days=random.randint(0, 90))
            WellbeingProgram.all_objects.create(
                tenant=tenant,
                name=name,
                description=desc,
                category=category,
                status=random.choice(['draft', 'active', 'completed']),
                start_date=start,
                end_date=start + timedelta(days=random.randint(30, 180)),
                max_participants=random.choice([0, 20, 30, 50]),
                is_active=True,
            )

        # Wellbeing Resources
        resource_data = [
            ('Managing Stress at Work', 'article', 'mental_health', 'Practical tips for managing workplace stress.'),
            ('Desk Yoga Routine', 'video', 'physical_health', '15-minute yoga routine you can do at your desk.'),
            ('Mindful Leadership Podcast', 'podcast', 'mindfulness', 'Weekly podcast on mindful leadership practices.'),
            ('Financial Planning Guide', 'guide', 'financial', 'Step-by-step guide to personal financial planning.'),
            ('Healthy Recipe Collection', 'tool', 'nutrition', 'Curated collection of healthy meal prep recipes.'),
            ('Building Resilience Webinar', 'webinar', 'mental_health', 'Expert-led webinar on building personal resilience.'),
            ('Sleep Hygiene Tips', 'article', 'physical_health', 'Evidence-based tips for better sleep quality.'),
            ('Meditation for Beginners', 'video', 'mindfulness', 'Guided meditation series for beginners.'),
        ]

        for title, rtype, category, desc in resource_data:
            WellbeingResource.all_objects.create(
                tenant=tenant,
                title=title,
                description=desc,
                resource_type=rtype,
                category=category,
                url='',
                is_featured=random.choice([True, False]),
                is_active=True,
            )

        # Wellness Challenges
        challenge_data = [
            ('10K Steps Daily', 'steps', Decimal('10000'), 'steps'),
            ('21-Day Meditation', 'meditation', Decimal('21'), 'sessions'),
            ('Hydration Challenge', 'hydration', Decimal('8'), 'glasses/day'),
            ('30-Day Fitness', 'exercise', Decimal('30'), 'workouts'),
            ('Sleep Well Challenge', 'sleep', Decimal('56'), 'hours/week'),
        ]

        challenges = []
        for title, ctype, target, unit in challenge_data:
            start = date.today() - timedelta(days=random.randint(0, 30))
            challenge = WellnessChallenge.all_objects.create(
                tenant=tenant,
                title=title,
                description=f'Join the {title} challenge and improve your {ctype}!',
                challenge_type=ctype,
                start_date=start,
                end_date=start + timedelta(days=random.randint(21, 45)),
                goal_target=target,
                goal_unit=unit,
                status=random.choice(['active', 'completed']),
                is_active=True,
            )
            challenges.append(challenge)

        # Add participants to challenges
        for challenge in challenges:
            participants = random.sample(employees, min(random.randint(3, 8), len(employees)))
            for emp in participants:
                progress = challenge.goal_target * Decimal(str(random.uniform(0.2, 1.0)))
                ChallengeParticipant.all_objects.create(
                    tenant=tenant,
                    challenge=challenge,
                    employee=emp,
                    progress=progress.quantize(Decimal('0.01')),
                    completed_at=timezone.now() if progress >= challenge.goal_target else None,
                )

        self.stdout.write('  Created 6 programs, 8 resources, 5 challenges with participants.')

    # =========================================================================
    # SUB-MODULE 3: WORK-LIFE BALANCE
    # =========================================================================

    def _seed_work_life_balance(self, tenant, employees):
        if FlexibleWorkArrangement.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Work-life balance data already exists, skipping...')
            return

        # Flexible Work Arrangements
        arrangement_types = ['remote', 'hybrid', 'flexible_hours', 'compressed_week', 'job_sharing']
        statuses = ['pending', 'approved', 'approved', 'approved', 'rejected']  # weighted toward approved

        for emp in employees[:10]:
            approver = random.choice([e for e in employees if e != emp])
            start = date.today() - timedelta(days=random.randint(0, 180))
            status = random.choice(statuses)
            FlexibleWorkArrangement.all_objects.create(
                tenant=tenant,
                employee=emp,
                arrangement_type=random.choice(arrangement_types),
                status=status,
                start_date=start,
                end_date=start + timedelta(days=random.randint(90, 365)),
                days_per_week=random.choice([3, 4, 5]),
                approved_by=approver if status == 'approved' else None,
                notes=f'Work arrangement request for {emp.first_name}.',
                is_active=status == 'approved',
            )

        # Remote Work Policies
        policy_data = [
            ('Standard Remote Work Policy', 'Guidelines for employees working remotely on a regular basis.',
             'Employees with 6+ months tenure in good standing.',
             'Laptop, monitor, keyboard, mouse, headset provided.',
             'Available during core hours (10am-4pm), respond to messages within 1 hour.'),
            ('Hybrid Work Policy', 'Framework for hybrid work arrangement with in-office and remote days.',
             'All full-time employees eligible.',
             'Company laptop provided. Home office stipend of $500/year.',
             'In-office on Tuesday and Thursday. Remote other days.'),
            ('Compressed Work Week Policy', 'Work 40 hours in 4 days instead of 5.',
             'Employees in non-client-facing roles with manager approval.',
             'Standard office equipment.',
             'Available during extended hours on working days (8am-6pm).'),
        ]

        for name, desc, eligibility, equipment, comm in policy_data:
            RemoteWorkPolicy.all_objects.create(
                tenant=tenant,
                name=name,
                description=desc,
                eligibility_criteria=eligibility,
                equipment_provided=equipment,
                communication_expectations=comm,
                is_active=True,
            )

        # Work-Life Balance Assessments
        for emp in employees[:8]:
            WorkLifeBalanceAssessment.all_objects.create(
                tenant=tenant,
                employee=emp,
                assessment_date=date.today() - timedelta(days=random.randint(0, 90)),
                work_satisfaction=random.randint(2, 5),
                life_satisfaction=random.randint(2, 5),
                stress_level=random.randint(1, 4),
                notes=random.choice([
                    'Feeling balanced with current hybrid arrangement.',
                    'Would benefit from more flexible hours.',
                    'Workload has been manageable this quarter.',
                    'Need better boundaries between work and personal time.',
                    '',
                ]),
            )

        self.stdout.write('  Created 10 arrangements, 3 policies, 8 assessments.')

    # =========================================================================
    # SUB-MODULE 4: EMPLOYEE ASSISTANCE
    # =========================================================================

    def _seed_eap(self, tenant, employees):
        if EAPProgram.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  EAP data already exists, skipping...')
            return

        program_data = [
            ('Employee Counseling Service', 'counseling', 'MindWell Partners', 'Phone: 1800-XXX-XXXX\nEmail: support@mindwell.example'),
            ('Legal Aid Assistance', 'legal', 'LegalShield Pro', 'Phone: 1800-XXX-YYYY\nPortal: legal.example'),
            ('Financial Advisory Service', 'financial', 'WealthWise Advisors', 'Phone: 1800-XXX-ZZZZ\nEmail: advice@wealthwise.example'),
            ('Career Coaching Program', 'career', 'GrowthPath Inc.', 'Email: coaching@growthpath.example'),
            ('Family Support Services', 'family', 'FamilyCare Network', 'Helpline: 1800-XXX-AAAA'),
        ]

        programs = []
        for name, stype, provider, contact in program_data:
            program = EAPProgram.all_objects.create(
                tenant=tenant,
                name=name,
                description=f'{name} - provided by {provider} for all employees.',
                provider=provider,
                contact_info=contact,
                service_type=stype,
                is_active=True,
            )
            programs.append(program)

        # Counseling Sessions
        counselors = ['Dr. Sarah Mitchell', 'Dr. James Wilson', 'Dr. Priya Sharma', 'Lisa Chen, LCSW']
        session_types = ['individual', 'individual', 'group', 'crisis']

        for i in range(12):
            emp = random.choice(employees)
            program = random.choice(programs)
            session_date = timezone.now() - timedelta(days=random.randint(0, 90))
            CounselingSession.all_objects.create(
                tenant=tenant,
                employee=emp,
                program=program,
                session_type=random.choice(session_types),
                session_date=session_date,
                duration_minutes=random.choice([30, 45, 60, 90]),
                status=random.choice(['scheduled', 'completed', 'completed', 'completed']),
                counselor_name=random.choice(counselors),
                is_confidential=True,
                notes='',
            )

        # EAP Utilization records
        for program in programs:
            for quarter in range(3):
                period_start = date(2026, 1 + quarter * 3, 1)
                period_end = date(2026, 3 + quarter * 3, 28) if quarter < 2 else date(2026, 3, 14)
                if period_start > date.today():
                    continue
                EAPUtilization.all_objects.create(
                    tenant=tenant,
                    program=program,
                    period_start=period_start,
                    period_end=period_end,
                    total_sessions=random.randint(5, 40),
                    total_participants=random.randint(3, 20),
                    satisfaction_score=Decimal(str(round(random.uniform(3.5, 5.0), 1))),
                )

        self.stdout.write('  Created 5 EAP programs, 12 sessions, utilization records.')

    # =========================================================================
    # SUB-MODULE 5: CULTURE & VALUES
    # =========================================================================

    def _seed_culture_values(self, tenant, employees):
        if CompanyValue.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Culture & values data already exists, skipping...')
            return

        value_data = [
            ('Innovation', 'We embrace creativity and continuously seek better ways to serve.', 'ri-lightbulb-line'),
            ('Integrity', 'We act with honesty, transparency, and ethical standards.', 'ri-shield-check-line'),
            ('Collaboration', 'We work together across teams and boundaries to achieve shared goals.', 'ri-team-line'),
            ('Customer Focus', 'We put our customers at the center of everything we do.', 'ri-user-heart-line'),
            ('Excellence', 'We strive for the highest quality in our work and outcomes.', 'ri-award-line'),
            ('Respect', 'We treat everyone with dignity and value diverse perspectives.', 'ri-hand-heart-line'),
        ]

        values = []
        for order, (name, desc, icon) in enumerate(value_data, 1):
            value = CompanyValue.all_objects.create(
                tenant=tenant,
                name=name,
                description=desc,
                icon=icon,
                order=order,
                is_active=True,
            )
            values.append(value)

        # Culture Assessments
        assessment_data = [
            ('Q1 2026 Culture Assessment', 'Quarterly culture alignment check for all employees.'),
            ('Annual Culture Audit 2026', 'Comprehensive annual assessment of organizational culture.'),
        ]

        assessments = []
        for title, desc in assessment_data:
            assessment = CultureAssessment.all_objects.create(
                tenant=tenant,
                title=title,
                description=desc,
                assessment_date=date.today() - timedelta(days=random.randint(0, 60)),
                status=random.choice(['active', 'completed']),
                created_by=random.choice(employees),
            )
            assessments.append(assessment)

        # Assessment Responses
        for assessment in assessments:
            respondents = random.sample(employees, min(random.randint(5, 10), len(employees)))
            for emp in respondents:
                CultureAssessmentResponse.all_objects.create(
                    tenant=tenant,
                    assessment=assessment,
                    employee=emp,
                    alignment_score=random.randint(2, 5),
                    comments=random.choice([
                        'Strong alignment with company values.',
                        'We could do better in living our collaboration value.',
                        'Innovation is truly part of our DNA.',
                        'More focus needed on work-life balance.',
                        '',
                    ]),
                )

        # Value Nominations
        nomination_reasons = [
            'Went above and beyond to help a colleague meet a tight deadline.',
            'Proposed an innovative solution that saved the team 20 hours per week.',
            'Demonstrated exceptional integrity in handling a difficult client situation.',
            'Organized a cross-team knowledge sharing session.',
            'Consistently delivers high-quality work that sets the standard for the team.',
            'Showed great respect and empathy during a challenging team transition.',
        ]

        for i in range(10):
            nominee = random.choice(employees)
            nominator = random.choice([e for e in employees if e != nominee])
            ValueNomination.all_objects.create(
                tenant=tenant,
                value=random.choice(values),
                nominee=nominee,
                nominated_by=nominator,
                reason=random.choice(nomination_reasons),
                status=random.choice(['pending', 'approved', 'approved', 'approved']),
                is_featured=random.choice([True, False, False]),
            )

        self.stdout.write('  Created 6 values, 2 assessments with responses, 10 nominations.')

    # =========================================================================
    # SUB-MODULE 6: SOCIAL CONNECT
    # =========================================================================

    def _seed_social_connect(self, tenant, employees):
        if TeamEvent.all_objects.filter(tenant=tenant).exists():
            self.stdout.write('  Social connect data already exists, skipping...')
            return

        # Team Events
        event_data = [
            ('Annual Company Picnic', 'team_building', 'City Park Pavilion', 0),
            ('Diwali Celebration 2026', 'celebration', 'Office Cafeteria', 0),
            ('Cricket Tournament', 'sports', 'Sports Complex', 40),
            ('Cultural Diversity Day', 'cultural', 'Conference Hall', 100),
            ('Lunch & Learn: AI in HR', 'learning', 'Meeting Room 3', 30),
            ('Friday Social Hour', 'social', 'Rooftop Terrace', 50),
            ('Hackathon 2026', 'team_building', 'Innovation Lab', 60),
            ('New Year Celebration', 'celebration', 'Grand Ballroom', 0),
        ]

        events = []
        for title, etype, location, max_p in event_data:
            event_date = timezone.now() + timedelta(days=random.randint(-60, 90))
            status = 'completed' if event_date < timezone.now() else random.choice(['planned', 'ongoing'])
            event = TeamEvent.all_objects.create(
                tenant=tenant,
                title=title,
                description=f'{title} - an exciting event for all employees.',
                event_type=etype,
                date=event_date,
                location=location,
                organizer=random.choice(employees),
                max_participants=max_p,
                status=status,
                is_active=True,
            )
            events.append(event)

        # Event Participants
        for event in events:
            attendees = random.sample(employees, min(random.randint(5, 12), len(employees)))
            for emp in attendees:
                EventParticipant.all_objects.create(
                    tenant=tenant,
                    event=event,
                    employee=emp,
                    rsvp_status=random.choice(['attending', 'attending', 'maybe', 'not_attending']),
                    attended=event.status == 'completed' and random.choice([True, True, False]),
                )

        # Interest Groups
        group_data = [
            ('Photography Club', 'arts', 'For photography enthusiasts to share tips and organize photo walks.'),
            ('Book Readers Circle', 'reading', 'Monthly book discussions and recommendations.'),
            ('Coding Club', 'technology', 'Learn new programming languages and collaborate on side projects.'),
            ('Running Group', 'sports', 'Regular running sessions for all fitness levels.'),
            ('Board Game Nights', 'gaming', 'Weekly board game sessions after work.'),
            ('Cooking Enthusiasts', 'cooking', 'Share recipes, cooking tips, and organize potlucks.'),
            ('Hiking Adventures', 'outdoor', 'Weekend hiking trips to nearby trails.'),
            ('Music Jam Sessions', 'music', 'Informal music sessions for musicians of all levels.'),
        ]

        groups = []
        for name, category, desc in group_data:
            group = InterestGroup.all_objects.create(
                tenant=tenant,
                name=name,
                description=desc,
                category=category,
                created_by=random.choice(employees),
                is_active=True,
            )
            groups.append(group)

        # Group Members
        for group in groups:
            # Creator is always admin
            InterestGroupMember.all_objects.create(
                tenant=tenant,
                group=group,
                employee=group.created_by,
                role='admin',
            )
            # Add random members
            other_employees = [e for e in employees if e != group.created_by]
            members = random.sample(other_employees, min(random.randint(3, 8), len(other_employees)))
            for emp in members:
                InterestGroupMember.all_objects.create(
                    tenant=tenant,
                    group=group,
                    employee=emp,
                    role='member',
                )

        # Volunteer Activities
        volunteer_data = [
            ('Beach Cleanup Drive', 'Organize and participate in local beach cleanup.', 'City Beach', Decimal('4.0')),
            ('Teach for a Day', 'Volunteer at local schools to teach underprivileged children.', 'Government School', Decimal('6.0')),
            ('Food Bank Volunteering', 'Help sort and distribute food at the local food bank.', 'Community Food Bank', Decimal('3.0')),
            ('Tree Plantation Drive', 'Plant trees in the community park.', 'Community Park', Decimal('4.0')),
            ('Blood Donation Camp', 'Organize a blood donation camp at the office.', 'Office Premises', Decimal('2.0')),
        ]

        activities = []
        for title, desc, location, hours in volunteer_data:
            activity_date = date.today() + timedelta(days=random.randint(-45, 60))
            status = 'completed' if activity_date < date.today() else 'planned'
            activity = VolunteerActivity.all_objects.create(
                tenant=tenant,
                title=title,
                description=desc,
                activity_date=activity_date,
                location=location,
                hours_required=hours,
                max_volunteers=random.choice([0, 15, 20, 25]),
                organizer=random.choice(employees),
                status=status,
                is_active=True,
            )
            activities.append(activity)

        # Volunteer Participants
        feedback_options = [
            'Great experience! Would love to do this again.',
            'Very rewarding and well organized.',
            'Felt good to give back to the community.',
            'Amazing team effort!',
            '',
        ]

        for activity in activities:
            volunteers = random.sample(employees, min(random.randint(4, 10), len(employees)))
            for emp in volunteers:
                contributed = activity.hours_required * Decimal(str(random.uniform(0.5, 1.0)))
                VolunteerParticipant.all_objects.create(
                    tenant=tenant,
                    activity=activity,
                    employee=emp,
                    hours_contributed=contributed.quantize(Decimal('0.1')) if activity.status == 'completed' else Decimal('0'),
                    feedback=random.choice(feedback_options) if activity.status == 'completed' else '',
                )

        self.stdout.write('  Created 8 events, 8 groups, 5 volunteer activities with participants.')
