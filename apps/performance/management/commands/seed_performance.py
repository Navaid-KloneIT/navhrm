"""
Seed realistic performance management data for all tenants.

Seeds data for all 15 performance models: GoalPeriod, Goal, GoalUpdate,
ReviewCycle, PerformanceReview, ReviewGoalRating, PeerReviewer, PeerFeedback,
Feedback, OneOnOneMeeting, MeetingActionItem, PIP, PIPCheckpoint,
WarningLetter, CoachingNote.

Usage:
    python manage.py seed_performance
    python manage.py seed_performance --clear   # Clear & re-seed
"""
import random
from datetime import date, timedelta, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Tenant, set_current_tenant
from apps.employees.models import Employee
from apps.performance.models import (
    GoalPeriod, Goal, GoalUpdate,
    ReviewCycle, PerformanceReview, ReviewGoalRating,
    PeerReviewer, PeerFeedback,
    Feedback, OneOnOneMeeting, MeetingActionItem,
    PIP, PIPCheckpoint, WarningLetter, CoachingNote,
)

# ---------------------------------------------------------------------------
# Realistic seed data pools
# ---------------------------------------------------------------------------

GOAL_TITLES = [
    ("Increase quarterly revenue by 15%", "kpi", "15% revenue growth", "individual"),
    ("Complete AWS Solutions Architect certification", "kpi", "Certification obtained", "individual"),
    ("Launch mobile app v2.0", "okr", "App launched to production", "team"),
    ("Improve team NPS score to 8+", "kpi", "NPS >= 8.0", "team"),
    ("Reduce customer churn rate by 20%", "kpi", "Churn rate < 5%", "department"),
    ("Implement CI/CD pipeline for all services", "okr", "100% services on CI/CD", "team"),
    ("Deliver Q1 product roadmap on time", "okr", "All milestones met", "department"),
    ("Reduce average bug resolution time to 48 hours", "kpi", "Avg resolution < 48h", "team"),
    ("Onboard 10 enterprise clients", "kpi", "10 signed contracts", "organization"),
    ("Achieve 99.9% uptime SLA", "kpi", "Uptime >= 99.9%", "organization"),
    ("Complete leadership development program", "kpi", "Program completed", "individual"),
    ("Migrate legacy database to PostgreSQL", "okr", "Migration complete", "team"),
    ("Reduce infrastructure costs by 25%", "kpi", "Cost reduction achieved", "department"),
    ("Launch employee wellness program", "okr", "Program active with 50%+ participation", "organization"),
    ("Improve code review turnaround to under 24 hours", "kpi", "Avg review time < 24h", "team"),
    ("Build and deploy analytics dashboard", "okr", "Dashboard live in production", "team"),
    ("Achieve SOC 2 Type II compliance", "okr", "Audit passed", "organization"),
    ("Increase test coverage to 85%", "kpi", "Coverage >= 85%", "team"),
    ("Reduce customer support ticket backlog by 40%", "kpi", "Backlog reduced by 40%", "department"),
    ("Establish cross-functional design system", "okr", "Design system adopted by 3+ teams", "department"),
    ("Complete data privacy training for all staff", "kpi", "100% completion rate", "organization"),
    ("Implement automated regression testing suite", "okr", "Suite running in CI", "team"),
    ("Grow social media engagement by 30%", "kpi", "30% engagement growth", "department"),
    ("Deliver API v3 with backward compatibility", "okr", "API v3 released", "team"),
    ("Mentor 2 junior developers through promotion cycle", "kpi", "2 promotions achieved", "individual"),
    ("Reduce page load time to under 2 seconds", "kpi", "P95 load time < 2s", "team"),
    ("Launch internal knowledge base platform", "okr", "Platform live with 100+ articles", "organization"),
    ("Achieve employee satisfaction score of 4.5+", "kpi", "Score >= 4.5", "organization"),
    ("Automate monthly financial reporting", "okr", "Automated reports running", "department"),
    ("Conduct quarterly security penetration tests", "kpi", "4 pen tests completed", "department"),
]

GOAL_UPDATE_NOTES = [
    "Made solid progress this week. Completed the initial milestone ahead of schedule.",
    "Encountered some blockers with third-party dependencies. Working on workarounds.",
    "On track to meet the deadline. Team collaboration has been excellent.",
    "Revised the approach after stakeholder feedback. New direction looks promising.",
    "Completed the research phase. Moving into implementation next week.",
    "Hit 50% completion mark. Remaining work is well-scoped.",
    "Had a productive sprint. Delivered 3 out of 5 planned deliverables.",
    "Slight delay due to resource reallocation. Adjusted timeline accordingly.",
    "Exceeded the weekly target. Confidence is high for on-time delivery.",
    "Conducted a mid-point review with the team. All aligned on priorities.",
    "Integration testing revealed minor issues. Fixes are in progress.",
    "Stakeholder demo went well. Received positive feedback on direction.",
    "Bottleneck identified in approval process. Escalated to management.",
    "Training completed for the new tooling. Productivity expected to improve.",
    "Final stretch - polishing deliverables and preparing documentation.",
]

REVIEW_SELF_COMMENTS = [
    "I believe I have met or exceeded expectations across most of my goals this period.",
    "I delivered strong results on key projects while also supporting team initiatives.",
    "I focused on improving my technical skills and took on stretch assignments.",
    "I successfully led the cross-functional initiative and delivered on time.",
    "I could have improved my time management on lower-priority tasks.",
]

REVIEW_MANAGER_COMMENTS = [
    "Consistently delivers high-quality work and is a reliable team member.",
    "Shows strong initiative and ownership. Ready for increased responsibilities.",
    "Good progress this period. Could benefit from more proactive communication.",
    "Exceeded expectations on the key project. Technical skills are top-notch.",
    "Solid performer who collaborates well. Encourage more leadership visibility.",
]

STRENGTHS = [
    "Strong technical problem-solving skills and attention to detail.",
    "Excellent communicator who bridges technical and business teams effectively.",
    "Demonstrates consistent ownership and accountability for deliverables.",
    "Proactive in identifying and resolving potential issues before they escalate.",
    "Great mentor to junior team members with a collaborative mindset.",
]

IMPROVEMENT_AREAS = [
    "Could improve on prioritizing tasks during high-pressure periods.",
    "Should work on delegating more to allow focus on strategic initiatives.",
    "Needs to improve documentation practices for better knowledge sharing.",
    "Could benefit from more structured approach to stakeholder management.",
    "Should focus on developing presentation and public speaking skills.",
]

PEER_FEEDBACK_COMMENTS = [
    "Great teammate who is always willing to help and share knowledge.",
    "Brings positive energy and creative solutions to team discussions.",
    "Reliable and consistent. I can always count on them to deliver.",
    "Would benefit from being more vocal in larger meetings.",
    "Strong collaborator who makes the team better overall.",
]

FEEDBACK_SUBJECTS_KUDOS = [
    ("Outstanding client presentation", "Your presentation to the enterprise client was exceptional. The preparation and delivery were top-notch."),
    ("Great mentoring effort", "Thank you for spending extra time mentoring the new hires. Your patience and guidance made a huge difference."),
    ("Excellent incident response", "Your quick thinking during the production incident saved us hours of downtime. Truly impressive."),
    ("Above and beyond on release", "Working through the weekend to ensure a smooth release shows incredible dedication. Thank you!"),
    ("Team player of the quarter", "Consistently helping others without being asked. Your collaborative spirit is what makes this team great."),
    ("Innovative solution delivery", "The caching solution you implemented reduced load times by 60%. Brilliant engineering work."),
    ("Customer success champion", "The way you handled the escalation turned an unhappy customer into an advocate. Well done!"),
]

FEEDBACK_SUBJECTS_CONSTRUCTIVE = [
    ("Communication in stand-ups", "It would help the team if you shared more detailed updates during daily stand-ups, especially on blockers."),
    ("Code review responsiveness", "Your code reviews are thorough, but the turnaround time could be improved. Aim for same-day reviews."),
    ("Meeting preparation", "Coming more prepared to planning meetings would help us make better use of everyone's time."),
    ("Documentation follow-through", "Great at building features, but the documentation often lags behind. Let's close that gap."),
    ("Deadline communication", "When deadlines are at risk, earlier communication would help us adjust plans proactively."),
]

FEEDBACK_SUBJECTS_GENERAL = [
    ("Quarterly retrospective thoughts", "Wanted to share some thoughts on how we can improve our sprint retrospectives for next quarter."),
    ("Process improvement idea", "I think we could streamline our deployment process by automating the staging environment setup."),
    ("Cross-team collaboration", "It would be great to set up regular sync meetings with the data team to align on shared priorities."),
    ("Team building suggestion", "How about organizing a monthly tech talk series? It would be great for knowledge sharing."),
    ("Tool recommendation", "I've been using this monitoring tool in my side project. Might be worth evaluating for our stack."),
]

MEETING_TITLES = [
    "Weekly 1:1 Sync",
    "Bi-weekly Check-in",
    "Career Development Discussion",
    "Project Milestone Review",
    "Performance Goals Alignment",
    "Mid-cycle Feedback Session",
    "Sprint Retrospective Debrief",
    "Quarterly Objectives Planning",
    "Return from PTO Catch-up",
    "Skills Development Planning",
    "End-of-quarter Review",
    "New Initiative Kick-off",
    "Team Dynamics Discussion",
    "Role Growth Conversation",
    "Technical Deep-dive Discussion",
]

MEETING_NOTES = [
    "Discussed progress on current goals. Employee is on track for most objectives.",
    "Covered career aspirations and identified two potential growth areas for next quarter.",
    "Reviewed project status. Discussed blocker with the API integration and agreed on a path forward.",
    "Talked about team dynamics. Employee raised concerns about workload distribution.",
    "Aligned on priorities for the upcoming sprint. Employee will take ownership of the auth module.",
    "Discussed feedback from the last review cycle. Employee appreciated the constructive input.",
]

MEETING_ACTION_DESCRIPTIONS = [
    "Schedule follow-up with the product team on requirements",
    "Draft proposal for the new testing framework",
    "Complete online course on system design by end of month",
    "Set up recurring sync with the data engineering team",
    "Prepare presentation for the team knowledge-sharing session",
    "Review and update personal development plan",
    "Document the architecture decision records for the new service",
    "Shadow senior engineer during next on-call rotation",
    "Submit expense report for the conference attendance",
    "Write unit tests for the payment module edge cases",
    "Organize a brownbag session on observability tools",
    "Create a runbook for the deployment pipeline",
]

PIP_DATA = [
    {
        "title": "Performance Improvement Plan - Delivery Consistency",
        "reason": "Consistently missed deadlines on assigned tasks over the last two quarters. Three out of five sprints had incomplete commitments without prior communication.",
        "goals": "1. Complete all assigned sprint items on time for 3 consecutive sprints\n2. Proactively communicate blockers within 24 hours\n3. Improve estimation accuracy to within 20% of actual effort",
        "support": "Weekly check-ins with manager, pairing with senior engineer on estimation, reduced scope for first sprint",
    },
    {
        "title": "Performance Improvement Plan - Code Quality",
        "reason": "Multiple production incidents traced back to insufficient testing and code review feedback not being addressed. Code coverage on authored modules is below 40%.",
        "goals": "1. Achieve 80%+ test coverage on all new code\n2. Zero critical bugs in production from authored code\n3. Address all code review feedback before merging",
        "support": "Testing workshop enrollment, dedicated refactoring time in sprint planning, mentorship from tech lead",
    },
    {
        "title": "Performance Improvement Plan - Collaboration & Communication",
        "reason": "Repeated feedback from multiple team members about lack of collaboration and unresponsive communication. Team satisfaction survey scores significantly below average.",
        "goals": "1. Respond to all messages within 4 business hours\n2. Actively participate in team ceremonies (stand-ups, retros, planning)\n3. Achieve team feedback score of 3.5+ in next pulse survey",
        "support": "Communication skills coaching, weekly feedback sessions with manager, conflict resolution workshop",
    },
    {
        "title": "Performance Improvement Plan - Technical Skills Gap",
        "reason": "Unable to independently complete tasks requiring core technology stack knowledge. Requires significant hand-holding on routine assignments that peers handle independently.",
        "goals": "1. Complete assigned learning path for core technologies within 30 days\n2. Independently deliver 3 medium-complexity features\n3. Pass internal technical assessment with 80%+ score",
        "support": "Access to learning platforms, dedicated study time (4 hrs/week), assigned technical mentor, reduced on-call rotation",
    },
]

PIP_CHECKPOINT_DATA = [
    ("Week 2 Review", "Initial progress assessment. Review first two weeks of improvement efforts."),
    ("Week 4 Mid-point Check", "Mid-point evaluation. Assess whether trajectory indicates success."),
    ("Week 6 Final Review", "Final assessment checkpoint before PIP conclusion decision."),
    ("Week 3 Progress Review", "Early progress check. Identify any adjustments needed to the plan."),
    ("Week 5 Near-completion Assessment", "Penultimate review. Determine if extension or conclusion is appropriate."),
]

WARNING_DATA = [
    {
        "type": "verbal",
        "subject": "Repeated tardiness and attendance issues",
        "description": "Employee has been late to work on 8 occasions in the past month, exceeding the acceptable threshold of 3 per quarter. This was discussed verbally on two prior occasions without improvement.",
    },
    {
        "type": "verbal",
        "subject": "Failure to follow code review process",
        "description": "Employee has bypassed the mandatory code review process on three separate occasions, merging code directly to the main branch without approval. This poses a risk to code quality and production stability.",
    },
    {
        "type": "written",
        "subject": "Inappropriate workplace communication",
        "description": "Employee used unprofessional language in a team Slack channel that made colleagues uncomfortable. This violates our workplace communication policy and code of conduct.",
    },
    {
        "type": "written",
        "subject": "Unauthorized access to restricted systems",
        "description": "Employee accessed production database without following the established change management process. This is a serious security policy violation that could result in data integrity issues.",
    },
    {
        "type": "final",
        "subject": "Continued policy violations after written warning",
        "description": "Despite previous verbal and written warnings, employee continues to violate the established processes. This serves as a final warning that any further violations will result in termination proceedings.",
    },
]

COACHING_TOPICS = [
    ("Leadership Development", "Discussed leadership frameworks and how to influence without authority. Practiced situational leadership scenarios.", "1. Read 'The Manager's Path' chapters 3-5\n2. Lead next sprint retrospective\n3. Identify one cross-team initiative to champion"),
    ("Technical Architecture Skills", "Deep dive into system design principles. Reviewed current architecture and identified areas for improvement.", "1. Complete system design case study\n2. Present architecture proposal for new service\n3. Review Martin Fowler's refactoring patterns"),
    ("Communication & Presentation Skills", "Worked on structuring presentations for executive audience. Practiced elevator pitch for the current project.", "1. Prepare 5-minute lightning talk for team meeting\n2. Record and review own presentation style\n3. Attend Toastmasters session"),
    ("Conflict Resolution", "Discussed recent team friction and strategies for constructive disagreement. Role-played difficult conversations.", "1. Practice active listening in next 3 meetings\n2. Journal reflections on difficult conversations\n3. Read 'Crucial Conversations' chapters 1-3"),
    ("Time Management & Prioritization", "Reviewed current workload and identified time sinks. Introduced Eisenhower matrix for task prioritization.", "1. Track time for one week using toggl\n2. Implement weekly planning ritual every Monday\n3. Identify and delegate 2 low-priority recurring tasks"),
    ("Career Growth Planning", "Mapped out career aspirations and identified gaps. Created a 12-month development roadmap.", "1. Schedule informational interviews with 2 people in target role\n2. Identify one stretch project for next quarter\n3. Update personal development plan document"),
    ("Stakeholder Management", "Discussed strategies for managing expectations with multiple stakeholders. Reviewed communication frequency and channels.", "1. Create a stakeholder map for current project\n2. Set up bi-weekly update cadence with key stakeholders\n3. Practice saying 'no' constructively using DACI framework"),
    ("Emotional Intelligence", "Explored self-awareness and empathy in workplace interactions. Discussed impact of emotional responses on team dynamics.", "1. Complete EQ self-assessment questionnaire\n2. Practice 'pause before responding' technique\n3. Seek feedback from 2 peers on interpersonal style"),
]

COACHING_SESSION_NOTES = [
    "Productive session. Employee showed genuine interest and self-awareness. Clear progress from last session.",
    "Employee came well-prepared with specific examples. We worked through real scenarios together.",
    "Good discussion but employee seems hesitant to step outside comfort zone. Encouraged small experiments.",
    "Breakthrough session. Employee connected coaching concepts to a real work challenge and found a solution.",
    "Follow-up from last session showed solid execution on action items. Raised the bar for next steps.",
]


class Command(BaseCommand):
    help = 'Seed realistic performance management data for all tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete existing performance data before seeding',
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

        self.stdout.write('Seeding Performance Management data...\n')

        for tenant in tenants:
            set_current_tenant(tenant)
            self.stdout.write(f'  Tenant: {tenant.name}')
            self._seed_tenant(tenant)

        self.stdout.write(self.style.SUCCESS(
            '\nPerformance Management seeding complete!'
        ))

    def _clear_data(self):
        self.stdout.write('  Clearing existing performance data...')
        # Delete in reverse dependency order
        CoachingNote.all_objects.all().delete()
        WarningLetter.all_objects.all().delete()
        PIPCheckpoint.all_objects.all().delete()
        PIP.all_objects.all().delete()
        MeetingActionItem.all_objects.all().delete()
        OneOnOneMeeting.all_objects.all().delete()
        Feedback.all_objects.all().delete()
        PeerFeedback.all_objects.all().delete()
        PeerReviewer.all_objects.all().delete()
        ReviewGoalRating.all_objects.all().delete()
        PerformanceReview.all_objects.all().delete()
        ReviewCycle.all_objects.all().delete()
        GoalUpdate.all_objects.all().delete()
        Goal.all_objects.all().delete()
        GoalPeriod.all_objects.all().delete()
        self.stdout.write(self.style.WARNING('  Cleared.'))

    def _seed_tenant(self, tenant):
        employees = list(
            Employee.all_objects.filter(tenant=tenant, status='active')
        )
        if not employees:
            self.stdout.write(self.style.WARNING(
                '    No active employees found. Skipping.'
            ))
            return

        # --- 1. Goal Periods ---
        periods = self._seed_goal_periods(tenant)

        # --- 2. Goals ---
        goals = self._seed_goals(tenant, employees, periods)

        # --- 3. Goal Updates ---
        goal_update_count = self._seed_goal_updates(tenant, employees, goals)

        # --- 4. Review Cycles ---
        cycles = self._seed_review_cycles(tenant, periods)

        # --- 5. Performance Reviews ---
        reviews = self._seed_performance_reviews(tenant, employees, cycles)

        # --- 6. Review Goal Ratings ---
        rating_count = self._seed_review_goal_ratings(tenant, reviews, goals)

        # --- 7 & 8. Peer Reviewers & Peer Feedback ---
        peer_reviewer_count, peer_feedback_count = self._seed_peer_reviews(
            tenant, employees, reviews
        )

        # --- 9. Feedback ---
        feedback_count = self._seed_feedback(tenant, employees)

        # --- 10 & 11. One-on-One Meetings & Action Items ---
        meeting_count, action_count = self._seed_meetings(tenant, employees)

        # --- 12 & 13. PIPs & PIP Checkpoints ---
        pip_count, checkpoint_count = self._seed_pips(tenant, employees)

        # --- 14. Warning Letters ---
        warning_count = self._seed_warning_letters(tenant, employees)

        # --- 15. Coaching Notes ---
        coaching_count = self._seed_coaching_notes(tenant, employees)

        self.stdout.write(
            f'    GoalPeriods: {len(periods)}, Goals: {len(goals)}, '
            f'GoalUpdates: {goal_update_count}'
        )
        self.stdout.write(
            f'    ReviewCycles: {len(cycles)}, Reviews: {len(reviews)}, '
            f'GoalRatings: {rating_count}'
        )
        self.stdout.write(
            f'    PeerReviewers: {peer_reviewer_count}, '
            f'PeerFeedback: {peer_feedback_count}'
        )
        self.stdout.write(
            f'    Feedback: {feedback_count}, Meetings: {meeting_count}, '
            f'ActionItems: {action_count}'
        )
        self.stdout.write(
            f'    PIPs: {pip_count}, Checkpoints: {checkpoint_count}, '
            f'Warnings: {warning_count}, CoachingNotes: {coaching_count}'
        )

    # -----------------------------------------------------------------------
    # 1. Goal Periods
    # -----------------------------------------------------------------------
    def _seed_goal_periods(self, tenant):
        period_definitions = [
            {
                "name": "Q1 2026",
                "period_type": "quarterly",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 3, 31),
                "status": "active",
                "description": "First quarter 2026 goal period",
            },
            {
                "name": "Q2 2026",
                "period_type": "quarterly",
                "start_date": date(2026, 4, 1),
                "end_date": date(2026, 6, 30),
                "status": "upcoming",
                "description": "Second quarter 2026 goal period",
            },
            {
                "name": "H1 2026",
                "period_type": "half_yearly",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 6, 30),
                "status": "active",
                "description": "First half of 2026 goal period",
            },
            {
                "name": "Annual 2025",
                "period_type": "annual",
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 12, 31),
                "status": "closed",
                "description": "Annual 2025 goal period - completed",
            },
            {
                "name": "Annual 2026",
                "period_type": "annual",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 12, 31),
                "status": "active",
                "description": "Annual 2026 goal period",
            },
        ]

        periods = []
        for defn in period_definitions:
            period, _ = GoalPeriod.all_objects.get_or_create(
                tenant=tenant,
                name=defn["name"],
                defaults=defn,
            )
            periods.append(period)
        return periods

    # -----------------------------------------------------------------------
    # 2. Goals
    # -----------------------------------------------------------------------
    def _seed_goals(self, tenant, employees, periods):
        goals = []
        num_goals = min(len(GOAL_TITLES), random.randint(20, 30))
        selected_goals = random.sample(GOAL_TITLES, num_goals)

        statuses = ['draft', 'active', 'on_track', 'at_risk', 'behind', 'completed', 'cancelled']
        status_weights = [5, 20, 25, 15, 10, 20, 5]

        for title, goal_type, target_value, visibility in selected_goals:
            employee = random.choice(employees)
            period = random.choice(periods)
            status = random.choices(statuses, weights=status_weights, k=1)[0]
            weight = Decimal(str(random.randint(10, 40)))

            # Progress based on status
            if status == 'draft':
                progress = 0
            elif status == 'completed':
                progress = 100
            elif status == 'cancelled':
                progress = random.randint(0, 30)
            elif status == 'behind':
                progress = random.randint(5, 30)
            elif status == 'at_risk':
                progress = random.randint(20, 50)
            elif status == 'on_track':
                progress = random.randint(40, 85)
            else:  # active
                progress = random.randint(10, 60)

            current_value = f"{progress}% towards target" if progress > 0 else ""

            start_date = period.start_date + timedelta(days=random.randint(0, 14))
            due_date = period.end_date - timedelta(days=random.randint(0, 14))

            goal, created = Goal.all_objects.get_or_create(
                tenant=tenant,
                title=title,
                employee=employee,
                period=period,
                defaults={
                    "description": f"Goal to {title.lower()}. Aligned with {period.name} objectives.",
                    "goal_type": goal_type,
                    "weight": weight,
                    "target_value": target_value,
                    "current_value": current_value,
                    "progress": progress,
                    "status": status,
                    "visibility": visibility,
                    "start_date": start_date,
                    "due_date": due_date,
                },
            )
            goals.append(goal)

        # Set parent_goal on some goals for cascading (about 20%)
        cascading_count = max(1, len(goals) // 5)
        org_or_dept_goals = [
            g for g in goals
            if g.visibility in ('organization', 'department')
        ]
        individual_goals = [
            g for g in goals
            if g.visibility == 'individual' and g.parent_goal is None
        ]

        if org_or_dept_goals and individual_goals:
            for child_goal in random.sample(
                individual_goals,
                min(cascading_count, len(individual_goals)),
            ):
                parent = random.choice(org_or_dept_goals)
                if parent.pk != child_goal.pk:
                    child_goal.parent_goal = parent
                    child_goal.save()

        return goals

    # -----------------------------------------------------------------------
    # 3. Goal Updates
    # -----------------------------------------------------------------------
    def _seed_goal_updates(self, tenant, employees, goals):
        count = 0
        active_goals = [
            g for g in goals if g.status not in ('draft', 'cancelled')
        ]

        for goal in active_goals:
            num_updates = random.randint(2, 4)
            current_progress = 0
            progress_step = goal.progress // max(num_updates, 1)

            for i in range(num_updates):
                current_progress = min(
                    goal.progress,
                    current_progress + progress_step + random.randint(0, 10),
                )
                note = random.choice(GOAL_UPDATE_NOTES)

                GoalUpdate.all_objects.create(
                    tenant=tenant,
                    goal=goal,
                    updated_by=goal.employee,
                    progress=current_progress,
                    current_value=f"{current_progress}% complete",
                    note=note,
                )
                count += 1
        return count

    # -----------------------------------------------------------------------
    # 4. Review Cycles
    # -----------------------------------------------------------------------
    def _seed_review_cycles(self, tenant, periods):
        cycle_definitions = [
            {
                "name": "Annual Review 2025",
                "cycle_type": "annual",
                "status": "completed",
                "start_date": date(2025, 11, 1),
                "end_date": date(2025, 12, 31),
                "self_assessment_deadline": date(2025, 11, 15),
                "manager_review_deadline": date(2025, 11, 30),
                "peer_review_deadline": date(2025, 12, 10),
                "calibration_deadline": date(2025, 12, 20),
                "description": "Annual performance review cycle for 2025",
                "period_name": "Annual 2025",
            },
            {
                "name": "H1 2026 Review",
                "cycle_type": "half_yearly",
                "status": "active",
                "start_date": date(2026, 1, 15),
                "end_date": date(2026, 3, 31),
                "self_assessment_deadline": date(2026, 2, 15),
                "manager_review_deadline": date(2026, 2, 28),
                "peer_review_deadline": date(2026, 3, 10),
                "calibration_deadline": date(2026, 3, 25),
                "description": "Mid-year performance review for H1 2026",
                "period_name": "H1 2026",
            },
            {
                "name": "Q1 2026 Review",
                "cycle_type": "quarterly",
                "status": "self_assessment",
                "start_date": date(2026, 2, 15),
                "end_date": date(2026, 3, 31),
                "self_assessment_deadline": date(2026, 3, 5),
                "manager_review_deadline": date(2026, 3, 15),
                "peer_review_deadline": date(2026, 3, 22),
                "calibration_deadline": date(2026, 3, 28),
                "description": "Quarterly check-in review for Q1 2026",
                "period_name": "Q1 2026",
            },
        ]

        cycles = []
        period_map = {p.name: p for p in GoalPeriod.all_objects.filter(tenant=tenant)}

        for defn in cycle_definitions:
            period_name = defn.pop("period_name")
            period = period_map.get(period_name)
            cycle, _ = ReviewCycle.all_objects.get_or_create(
                tenant=tenant,
                name=defn["name"],
                defaults={
                    **defn,
                    "period": period,
                },
            )
            cycles.append(cycle)
        return cycles

    # -----------------------------------------------------------------------
    # 5. Performance Reviews
    # -----------------------------------------------------------------------
    def _seed_performance_reviews(self, tenant, employees, cycles):
        reviews = []
        review_statuses_by_cycle = {
            'completed': ['completed', 'completed', 'completed', 'calibration'],
            'active': ['pending', 'self_assessment', 'manager_review', 'peer_review'],
            'self_assessment': ['pending', 'self_assessment', 'self_assessment'],
            'draft': ['pending'],
        }

        for cycle in cycles:
            possible_statuses = review_statuses_by_cycle.get(
                cycle.status, ['pending', 'self_assessment']
            )
            num_reviews = min(len(employees), random.randint(8, 12))
            selected_employees = random.sample(employees, num_reviews)

            for emp in selected_employees:
                # Pick a different employee as reviewer (manager)
                other_employees = [e for e in employees if e.pk != emp.pk]
                reviewer = random.choice(other_employees) if other_employees else None

                status = random.choice(possible_statuses)

                self_rating = None
                self_comments = ""
                manager_rating = None
                manager_comments = ""
                final_rating = None
                final_comments = ""
                strengths = ""
                areas_of_improvement = ""
                submitted_at = None
                reviewed_at = None
                calibrated_by = None
                calibrated_at = None

                if status in ('self_assessment', 'manager_review', 'peer_review', 'calibration', 'completed'):
                    self_rating = Decimal(str(round(random.uniform(3.0, 5.0), 1)))
                    self_comments = random.choice(REVIEW_SELF_COMMENTS)
                    submitted_at = timezone.now() - timedelta(days=random.randint(5, 30))

                if status in ('manager_review', 'peer_review', 'calibration', 'completed'):
                    manager_rating = Decimal(str(round(random.uniform(2.5, 5.0), 1)))
                    manager_comments = random.choice(REVIEW_MANAGER_COMMENTS)
                    strengths = random.choice(STRENGTHS)
                    areas_of_improvement = random.choice(IMPROVEMENT_AREAS)
                    reviewed_at = timezone.now() - timedelta(days=random.randint(1, 20))

                if status in ('calibration', 'completed'):
                    final_rating = Decimal(str(round(random.uniform(2.5, 5.0), 1)))
                    final_comments = f"Final calibrated rating after review of self-assessment and manager evaluation."
                    if other_employees:
                        calibrated_by = random.choice(other_employees)
                    calibrated_at = timezone.now() - timedelta(days=random.randint(1, 10))

                review, created = PerformanceReview.all_objects.get_or_create(
                    tenant=tenant,
                    cycle=cycle,
                    employee=emp,
                    defaults={
                        "reviewer": reviewer,
                        "status": status,
                        "self_rating": self_rating,
                        "self_comments": self_comments,
                        "manager_rating": manager_rating,
                        "manager_comments": manager_comments,
                        "final_rating": final_rating,
                        "final_comments": final_comments,
                        "calibrated_by": calibrated_by,
                        "calibrated_at": calibrated_at,
                        "strengths": strengths,
                        "areas_of_improvement": areas_of_improvement,
                        "submitted_at": submitted_at,
                        "reviewed_at": reviewed_at,
                    },
                )
                reviews.append(review)
        return reviews

    # -----------------------------------------------------------------------
    # 6. Review Goal Ratings
    # -----------------------------------------------------------------------
    def _seed_review_goal_ratings(self, tenant, reviews, goals):
        count = 0
        for review in reviews:
            # Get goals belonging to the same employee
            employee_goals = [g for g in goals if g.employee_id == review.employee_id]
            if not employee_goals:
                continue

            num_ratings = min(len(employee_goals), random.randint(1, 3))
            selected_goals = random.sample(employee_goals, num_ratings)

            for goal in selected_goals:
                self_rating = None
                manager_rating = None

                if review.status in ('self_assessment', 'manager_review', 'peer_review', 'calibration', 'completed'):
                    self_rating = Decimal(str(round(random.uniform(3.0, 5.0), 1)))

                if review.status in ('manager_review', 'peer_review', 'calibration', 'completed'):
                    manager_rating = Decimal(str(round(random.uniform(2.5, 5.0), 1)))

                _, created = ReviewGoalRating.all_objects.get_or_create(
                    tenant=tenant,
                    review=review,
                    goal=goal,
                    defaults={
                        "self_rating": self_rating,
                        "self_comments": f"Self-assessment for: {goal.title}",
                        "manager_rating": manager_rating,
                        "manager_comments": f"Manager evaluation for: {goal.title}" if manager_rating else "",
                    },
                )
                if created:
                    count += 1
        return count

    # -----------------------------------------------------------------------
    # 7 & 8. Peer Reviewers & Peer Feedback
    # -----------------------------------------------------------------------
    def _seed_peer_reviews(self, tenant, employees, reviews):
        peer_reviewer_count = 0
        peer_feedback_count = 0

        # Only assign peers to reviews that are in peer_review, calibration, or completed
        eligible_reviews = [
            r for r in reviews
            if r.status in ('peer_review', 'calibration', 'completed')
        ]

        for review in eligible_reviews:
            other_employees = [
                e for e in employees
                if e.pk != review.employee_id
                and (review.reviewer_id is None or e.pk != review.reviewer_id)
            ]
            if not other_employees:
                continue

            num_peers = min(len(other_employees), random.randint(2, 3))
            selected_peers = random.sample(other_employees, num_peers)
            assigner = review.reviewer or random.choice(employees)

            for peer_emp in selected_peers:
                if review.status == 'completed':
                    peer_status = 'completed'
                elif review.status == 'calibration':
                    peer_status = random.choice(['completed', 'completed', 'accepted'])
                else:
                    peer_status = random.choice(['pending', 'accepted', 'completed', 'declined'])

                peer_reviewer, created = PeerReviewer.all_objects.get_or_create(
                    tenant=tenant,
                    review=review,
                    reviewer=peer_emp,
                    defaults={
                        "status": peer_status,
                        "assigned_by": assigner,
                    },
                )
                if created:
                    peer_reviewer_count += 1

                # Create feedback for completed peer reviewers
                if peer_reviewer.status == 'completed':
                    _, fb_created = PeerFeedback.all_objects.get_or_create(
                        tenant=tenant,
                        peer_reviewer=peer_reviewer,
                        defaults={
                            "rating": Decimal(str(round(random.uniform(3.0, 5.0), 1))),
                            "strengths": random.choice(STRENGTHS),
                            "areas_of_improvement": random.choice(IMPROVEMENT_AREAS),
                            "comments": random.choice(PEER_FEEDBACK_COMMENTS),
                        },
                    )
                    if fb_created:
                        peer_feedback_count += 1

        return peer_reviewer_count, peer_feedback_count

    # -----------------------------------------------------------------------
    # 9. Feedback
    # -----------------------------------------------------------------------
    def _seed_feedback(self, tenant, employees):
        count = 0
        num_feedback = random.randint(15, 25)

        for _ in range(num_feedback):
            from_emp = random.choice(employees)
            to_emp = random.choice([e for e in employees if e.pk != from_emp.pk])

            feedback_type = random.choices(
                ['kudos', 'constructive', 'general'],
                weights=[50, 25, 25],
                k=1,
            )[0]

            if feedback_type == 'kudos':
                subject, message = random.choice(FEEDBACK_SUBJECTS_KUDOS)
            elif feedback_type == 'constructive':
                subject, message = random.choice(FEEDBACK_SUBJECTS_CONSTRUCTIVE)
            else:
                subject, message = random.choice(FEEDBACK_SUBJECTS_GENERAL)

            is_anonymous = random.random() < 0.15
            if is_anonymous:
                visibility = 'anonymous'
            else:
                visibility = random.choice(['public', 'private'])

            Feedback.all_objects.create(
                tenant=tenant,
                from_employee=from_emp,
                to_employee=to_emp,
                feedback_type=feedback_type,
                visibility=visibility,
                subject=subject,
                message=message,
                is_anonymous=is_anonymous,
            )
            count += 1
        return count

    # -----------------------------------------------------------------------
    # 10 & 11. One-on-One Meetings & Action Items
    # -----------------------------------------------------------------------
    def _seed_meetings(self, tenant, employees):
        meeting_count = 0
        action_count = 0
        num_meetings = random.randint(10, 15)

        for i in range(num_meetings):
            manager = random.choice(employees)
            emp = random.choice([e for e in employees if e.pk != manager.pk])
            title = random.choice(MEETING_TITLES)

            # Spread meetings across the past 2 months and upcoming 2 weeks
            days_offset = random.randint(-60, 14)
            scheduled_date = date.today() + timedelta(days=days_offset)

            hour = random.choice([9, 10, 11, 13, 14, 15, 16])
            minute = random.choice([0, 30])
            scheduled_time = time(hour, minute)

            duration = random.choice([30, 45, 60])
            location = random.choice([
                "Conference Room A", "Conference Room B",
                "Google Meet", "Zoom", "Microsoft Teams",
                "Manager's Office", "Cafeteria",
            ])

            if days_offset < -7:
                status = random.choices(
                    ['completed', 'cancelled', 'rescheduled'],
                    weights=[75, 15, 10],
                    k=1,
                )[0]
            elif days_offset < 0:
                status = random.choices(
                    ['completed', 'scheduled'],
                    weights=[80, 20],
                    k=1,
                )[0]
            else:
                status = 'scheduled'

            notes = random.choice(MEETING_NOTES) if status == 'completed' else ""
            manager_notes = (
                "Follow up on the action items from today's discussion."
                if status == 'completed' else ""
            )
            employee_notes = (
                "Prepared topics to discuss and questions about upcoming projects."
                if status == 'completed' and random.random() < 0.6 else ""
            )

            meeting = OneOnOneMeeting.all_objects.create(
                tenant=tenant,
                manager=manager,
                employee=emp,
                title=title,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                duration_minutes=duration,
                location=location,
                status=status,
                notes=notes,
                manager_notes=manager_notes,
                employee_notes=employee_notes,
            )
            meeting_count += 1

            # Action items for completed meetings
            if status == 'completed':
                num_actions = random.randint(1, 3)
                action_descriptions = random.sample(
                    MEETING_ACTION_DESCRIPTIONS,
                    min(num_actions, len(MEETING_ACTION_DESCRIPTIONS)),
                )

                for desc in action_descriptions:
                    assigned = random.choice([manager, emp])
                    action_due = scheduled_date + timedelta(
                        days=random.randint(3, 14)
                    )
                    action_status = random.choices(
                        ['pending', 'in_progress', 'completed', 'cancelled'],
                        weights=[30, 30, 35, 5],
                        k=1,
                    )[0]

                    MeetingActionItem.all_objects.create(
                        tenant=tenant,
                        meeting=meeting,
                        description=desc,
                        assigned_to=assigned,
                        due_date=action_due,
                        status=action_status,
                    )
                    action_count += 1

        return meeting_count, action_count

    # -----------------------------------------------------------------------
    # 12 & 13. PIPs & PIP Checkpoints
    # -----------------------------------------------------------------------
    def _seed_pips(self, tenant, employees):
        pip_count = 0
        checkpoint_count = 0
        num_pips = random.randint(2, 4)

        pip_statuses = ['draft', 'active', 'extended', 'completed_success', 'completed_failure', 'cancelled']
        pip_status_weights = [10, 30, 15, 20, 15, 10]

        selected_pip_data = random.sample(
            PIP_DATA, min(num_pips, len(PIP_DATA))
        )

        for pip_data in selected_pip_data:
            emp = random.choice(employees)
            initiator = random.choice([e for e in employees if e.pk != emp.pk])
            status = random.choices(pip_statuses, weights=pip_status_weights, k=1)[0]

            start_date = date.today() - timedelta(days=random.randint(14, 90))
            end_date = start_date + timedelta(days=random.randint(30, 90))

            outcome_notes = ""
            if status == 'completed_success':
                outcome_notes = "Employee successfully met all improvement goals. Performance has returned to acceptable levels. Recommending return to normal performance tracking."
            elif status == 'completed_failure':
                outcome_notes = "Employee was unable to meet the required improvement targets within the PIP period. Escalating to HR for further action."
            elif status == 'cancelled':
                outcome_notes = "PIP cancelled due to organizational restructuring. Employee reassigned to new team."

            pip, created = PIP.all_objects.get_or_create(
                tenant=tenant,
                employee=emp,
                title=pip_data["title"],
                defaults={
                    "initiated_by": initiator,
                    "reason": pip_data["reason"],
                    "goals": pip_data["goals"],
                    "support_provided": pip_data["support"],
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": status,
                    "outcome_notes": outcome_notes,
                },
            )
            if created:
                pip_count += 1

            # PIP Checkpoints
            num_checkpoints = random.randint(2, 3)
            selected_checkpoints = random.sample(
                PIP_CHECKPOINT_DATA,
                min(num_checkpoints, len(PIP_CHECKPOINT_DATA)),
            )

            checkpoint_statuses = {
                'draft': ['pending'],
                'active': ['pending', 'on_track', 'needs_improvement'],
                'extended': ['pending', 'on_track', 'needs_improvement'],
                'completed_success': ['met', 'met', 'on_track'],
                'completed_failure': ['not_met', 'needs_improvement', 'not_met'],
                'cancelled': ['pending'],
            }
            possible_cp_statuses = checkpoint_statuses.get(status, ['pending'])

            for j, (cp_title, cp_desc) in enumerate(selected_checkpoints):
                cp_due = start_date + timedelta(
                    days=(j + 1) * ((end_date - start_date).days // (num_checkpoints + 1))
                )
                cp_status = random.choice(possible_cp_statuses)

                review_date = None
                manager_notes_text = ""
                employee_notes_text = ""

                if cp_status not in ('pending',):
                    review_date = cp_due + timedelta(days=random.randint(0, 3))
                    manager_notes_text = random.choice([
                        "Employee is showing improvement in the identified areas.",
                        "Progress is slower than expected. Additional support may be needed.",
                        "Good trajectory. Continue with current approach.",
                        "Discussed specific examples of improvement and areas still needing work.",
                        "Employee has met this checkpoint's requirements satisfactorily.",
                    ])
                    employee_notes_text = random.choice([
                        "I feel I am making progress. The mentoring sessions have been helpful.",
                        "Working on the feedback areas. Would appreciate more specific guidance.",
                        "Completed the training modules. Applying learnings to daily work.",
                        "",
                    ])

                _, cp_created = PIPCheckpoint.all_objects.get_or_create(
                    tenant=tenant,
                    pip=pip,
                    title=cp_title,
                    defaults={
                        "description": cp_desc,
                        "due_date": cp_due,
                        "review_date": review_date,
                        "status": cp_status,
                        "manager_notes": manager_notes_text,
                        "employee_notes": employee_notes_text,
                    },
                )
                if cp_created:
                    checkpoint_count += 1

        return pip_count, checkpoint_count

    # -----------------------------------------------------------------------
    # 14. Warning Letters
    # -----------------------------------------------------------------------
    def _seed_warning_letters(self, tenant, employees):
        count = 0
        num_warnings = random.randint(3, 5)
        selected_warnings = random.sample(
            WARNING_DATA, min(num_warnings, len(WARNING_DATA))
        )

        for warning_data in selected_warnings:
            emp = random.choice(employees)
            issuer = random.choice([e for e in employees if e.pk != emp.pk])

            status = random.choices(
                ['draft', 'issued', 'acknowledged', 'appealed', 'resolved'],
                weights=[10, 25, 35, 15, 15],
                k=1,
            )[0]

            issue_date = date.today() - timedelta(days=random.randint(7, 120))

            acknowledged_date = None
            employee_response = ""

            if status in ('acknowledged', 'appealed', 'resolved'):
                acknowledged_date = issue_date + timedelta(
                    days=random.randint(1, 7)
                )
                employee_response = random.choice([
                    "I acknowledge receipt of this warning and understand the concerns raised. I will work to address these issues.",
                    "I accept the feedback and commit to improving in the areas identified.",
                    "While I understand the concern, I would like to discuss the circumstances that contributed to this situation.",
                    "I acknowledge this warning and have already begun taking corrective action.",
                    "",
                ])

            warning, created = WarningLetter.all_objects.get_or_create(
                tenant=tenant,
                employee=emp,
                subject=warning_data["subject"],
                defaults={
                    "issued_by": issuer,
                    "warning_type": warning_data["type"],
                    "description": warning_data["description"],
                    "issue_date": issue_date,
                    "status": status,
                    "acknowledged_date": acknowledged_date,
                    "employee_response": employee_response,
                },
            )
            if created:
                count += 1
        return count

    # -----------------------------------------------------------------------
    # 15. Coaching Notes
    # -----------------------------------------------------------------------
    def _seed_coaching_notes(self, tenant, employees):
        count = 0
        num_notes = random.randint(5, 8)
        selected_topics = random.sample(
            COACHING_TOPICS, min(num_notes, len(COACHING_TOPICS))
        )

        for topic, base_notes, action_items in selected_topics:
            emp = random.choice(employees)
            coach = random.choice([e for e in employees if e.pk != emp.pk])

            session_date = date.today() - timedelta(days=random.randint(3, 60))
            follow_up_date = session_date + timedelta(days=random.randint(7, 21))

            session_notes = (
                f"{random.choice(COACHING_SESSION_NOTES)}\n\n{base_notes}"
            )

            coaching_note, created = CoachingNote.all_objects.get_or_create(
                tenant=tenant,
                employee=emp,
                topic=topic,
                session_date=session_date,
                defaults={
                    "coach": coach,
                    "notes": session_notes,
                    "action_items": action_items,
                    "follow_up_date": follow_up_date,
                },
            )
            if created:
                count += 1
        return count
