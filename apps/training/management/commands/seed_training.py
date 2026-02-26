import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.organization.models import Department
from apps.training.models import (
    TrainingCategory, TrainingVendor, Training, TrainingSession,
    Course, CourseContent, LearningPath, LearningPathCourse, CourseEnrollment,
    Assessment, AssessmentQuestion, Badge, EmployeeBadge,
    TrainingNomination, TrainingAttendance, TrainingFeedback,
    TrainingCertificate, TrainingBudget,
)


class Command(BaseCommand):
    help = 'Seed training & development module with sample data'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found. Run seed_data first.'))
            return

        for tenant in tenants:
            self.stdout.write(f'Seeding training data for {tenant.name}...')
            employees = list(Employee.objects.filter(tenant=tenant, status='active'))
            departments = list(Department.objects.filter(tenant=tenant))

            if len(employees) < 2:
                self.stdout.write(self.style.WARNING(f'  Skipping {tenant.name} - not enough employees.'))
                continue

            # Categories
            categories = self._seed_categories(tenant)

            # Vendors
            vendors = self._seed_vendors(tenant)

            # Trainings
            trainings = self._seed_trainings(tenant, categories, vendors)

            # Sessions
            sessions = self._seed_sessions(tenant, trainings, employees)

            # Courses
            courses = self._seed_courses(tenant, categories)

            # Course Content
            self._seed_course_content(tenant, courses)

            # Learning Paths
            paths = self._seed_learning_paths(tenant, courses, departments)

            # Assessments & Questions
            assessments = self._seed_assessments(tenant, courses)

            # Badges
            badges = self._seed_badges(tenant)

            # Enrollments
            self._seed_enrollments(tenant, courses, employees)

            # Nominations
            self._seed_nominations(tenant, trainings, employees)

            # Attendance
            self._seed_attendance(tenant, sessions, employees)

            # Feedback
            self._seed_feedback(tenant, trainings, employees)

            # Certificates
            self._seed_certificates(tenant, trainings, courses, employees)

            # Budgets
            self._seed_budgets(tenant, departments)

            # Employee Badges
            self._seed_employee_badges(tenant, badges, courses, employees)

            self.stdout.write(self.style.SUCCESS(f'  Done seeding training data for {tenant.name}.'))

        self.stdout.write(self.style.SUCCESS('Training data seeding complete!'))

    def _seed_categories(self, tenant):
        category_data = [
            ('Technical Skills', 'Programming, databases, cloud computing, DevOps'),
            ('Soft Skills', 'Communication, leadership, teamwork, time management'),
            ('Compliance', 'Regulatory compliance, safety, data privacy'),
            ('Management', 'Project management, people management, strategic planning'),
            ('Product Training', 'Company products, features, updates'),
            ('Onboarding', 'New hire orientation, company culture, policies'),
        ]
        categories = []
        for name, desc in category_data:
            cat, _ = TrainingCategory.objects.get_or_create(
                tenant=tenant, name=name,
                defaults={'description': desc, 'is_active': True}
            )
            categories.append(cat)
        return categories

    def _seed_vendors(self, tenant):
        vendor_data = [
            ('SkillUp Academy', 'John Smith', 'john@skillup.com', '+91-9876543210', 'https://skillup.com'),
            ('TechLearn Pro', 'Sarah Johnson', 'sarah@techlearn.com', '+91-9876543211', 'https://techlearn.com'),
            ('LeadershipEdge', 'Mike Wilson', 'mike@leadedge.com', '+91-9876543212', 'https://leadedge.com'),
            ('CompliancePlus', 'Lisa Brown', 'lisa@complianceplus.com', '+91-9876543213', 'https://complianceplus.com'),
        ]
        vendors = []
        for name, contact, email, phone, website in vendor_data:
            vendor, _ = TrainingVendor.objects.get_or_create(
                tenant=tenant, name=name,
                defaults={
                    'contact_person': contact, 'email': email,
                    'phone': phone, 'website': website, 'is_active': True,
                }
            )
            vendors.append(vendor)
        return vendors

    def _seed_trainings(self, tenant, categories, vendors):
        training_data = [
            ('Python Advanced Programming', 'classroom', 'published', 16, 5000, False),
            ('AWS Cloud Practitioner', 'virtual', 'published', 24, 8000, True),
            ('Effective Communication', 'classroom', 'published', 8, 3000, False),
            ('Data Privacy & GDPR Compliance', 'virtual', 'published', 4, 2000, True),
            ('Agile Project Management', 'classroom', 'published', 16, 6000, False),
            ('React.js Fundamentals', 'virtual', 'published', 20, 4500, False),
            ('Leadership for New Managers', 'external', 'published', 24, 15000, True),
            ('Docker & Kubernetes', 'virtual', 'draft', 16, 7000, False),
            ('Time Management Mastery', 'classroom', 'published', 4, 1500, False),
            ('SQL & Database Design', 'virtual', 'published', 12, 3500, False),
        ]
        trainings = []
        for i, (title, ttype, status, hours, cost, featured) in enumerate(training_data):
            cat = categories[i % len(categories)]
            vendor = vendors[i % len(vendors)] if ttype == 'external' else None
            training, _ = Training.objects.get_or_create(
                tenant=tenant, title=title,
                defaults={
                    'description': f'Comprehensive {title.lower()} training program for employees.',
                    'category': cat, 'training_type': ttype, 'vendor': vendor,
                    'instructor_name': f'Instructor {i+1}',
                    'instructor_email': f'instructor{i+1}@example.com',
                    'duration_hours': hours, 'max_participants': random.randint(10, 50),
                    'cost_per_person': cost, 'currency': 'INR',
                    'prerequisites': 'Basic knowledge required' if i % 2 == 0 else '',
                    'objectives': f'Master key concepts in {title.lower()}.',
                    'status': status, 'is_featured': featured,
                }
            )
            trainings.append(training)
        return trainings

    def _seed_sessions(self, tenant, trainings, employees):
        sessions = []
        today = date.today()
        for i, training in enumerate(trainings[:6]):
            for j in range(random.randint(1, 3)):
                session_date = today + timedelta(days=random.randint(-30, 60))
                status = 'completed' if session_date < today else 'scheduled'
                instructor = random.choice(employees) if employees else None
                session, _ = TrainingSession.objects.get_or_create(
                    tenant=tenant, training=training,
                    title=f'{training.title} - Session {j+1}',
                    defaults={
                        'session_date': session_date,
                        'start_time': '09:00:00', 'end_time': '17:00:00',
                        'venue': f'Conference Room {chr(65+j)}' if training.training_type == 'classroom' else '',
                        'meeting_link': 'https://meet.example.com/session' if training.training_type == 'virtual' else '',
                        'instructor': instructor,
                        'max_participants': training.max_participants,
                        'status': status,
                    }
                )
                sessions.append(session)
        return sessions

    def _seed_courses(self, tenant, categories):
        course_data = [
            ('Introduction to Python', 'video', 'beginner', 8, True),
            ('Advanced JavaScript', 'blended', 'advanced', 16, False),
            ('Data Analysis with Excel', 'document', 'beginner', 6, True),
            ('Cloud Architecture Patterns', 'video', 'advanced', 20, False),
            ('Workplace Safety Training', 'scorm', 'beginner', 2, True),
            ('Git Version Control', 'video', 'intermediate', 4, False),
            ('REST API Design', 'blended', 'intermediate', 10, False),
            ('Business Communication', 'document', 'beginner', 5, False),
        ]
        courses = []
        for i, (title, ctype, diff, hours, mandatory) in enumerate(course_data):
            cat = categories[i % len(categories)]
            course, _ = Course.objects.get_or_create(
                tenant=tenant, title=title,
                defaults={
                    'description': f'Learn {title.lower()} through comprehensive materials.',
                    'category': cat, 'course_type': ctype,
                    'difficulty_level': diff, 'duration_hours': hours,
                    'is_mandatory': mandatory, 'is_published': True,
                }
            )
            courses.append(course)
        return courses

    def _seed_course_content(self, tenant, courses):
        content_types = ['video', 'document', 'link', 'text']
        for course in courses:
            if course.contents.exists():
                continue
            for j in range(random.randint(3, 6)):
                CourseContent.objects.create(
                    tenant=tenant, course=course,
                    title=f'Module {j+1}: {course.title} Part {j+1}',
                    content_type=random.choice(content_types),
                    content_url=f'https://example.com/content/{course.pk}/{j+1}' if j % 2 == 0 else '',
                    description=f'Module {j+1} covering key concepts.',
                    order=j+1,
                    duration_minutes=random.randint(15, 60),
                )

    def _seed_learning_paths(self, tenant, courses, departments):
        path_data = [
            ('Junior Developer Onboarding', 'Junior Developer', 40),
            ('Data Analyst Track', 'Data Analyst', 30),
            ('Engineering Lead Path', 'Engineering Lead', 50),
        ]
        paths = []
        for i, (title, role, hours) in enumerate(path_data):
            dept = departments[i % len(departments)] if departments else None
            path, created = LearningPath.objects.get_or_create(
                tenant=tenant, title=title,
                defaults={
                    'description': f'Learning path for {role} role development.',
                    'target_role': role, 'target_department': dept,
                    'is_mandatory': i == 0, 'is_published': True,
                    'estimated_hours': hours,
                }
            )
            paths.append(path)
            if created and len(courses) >= 3:
                selected = random.sample(courses, min(3, len(courses)))
                for j, course in enumerate(selected):
                    LearningPathCourse.objects.get_or_create(
                        tenant=tenant, learning_path=path, course=course,
                        defaults={'order': j+1, 'is_mandatory': True}
                    )
        return paths

    def _seed_assessments(self, tenant, courses):
        assessments = []
        for i, course in enumerate(courses[:4]):
            assessment, created = Assessment.objects.get_or_create(
                tenant=tenant, title=f'{course.title} - Final Quiz',
                defaults={
                    'course': course,
                    'description': f'Assessment for {course.title}.',
                    'assessment_type': 'quiz',
                    'passing_score': 60, 'time_limit_minutes': 30,
                    'max_attempts': 3, 'is_published': True,
                }
            )
            assessments.append(assessment)
            if created:
                for q in range(5):
                    AssessmentQuestion.objects.create(
                        tenant=tenant, assessment=assessment,
                        question_text=f'Sample question {q+1} for {course.title}?',
                        question_type='multiple_choice',
                        option_a='Option A', option_b='Option B',
                        option_c='Option C', option_d='Option D',
                        correct_answer='Option A',
                        points=random.choice([1, 2, 5]),
                        order=q+1,
                    )
        return assessments

    def _seed_badges(self, tenant):
        badge_data = [
            ('Quick Learner', 'Complete your first course', 'ri-flashlight-line', 'course_completion', 10),
            ('Knowledge Seeker', 'Complete 5 courses', 'ri-search-eye-line', 'course_completion', 50),
            ('Path Finder', 'Complete a learning path', 'ri-route-line', 'path_completion', 100),
            ('Quiz Master', 'Score 100% on any assessment', 'ri-trophy-line', 'assessment', 75),
            ('Training Champion', 'Attend 10 training sessions', 'ri-medal-2-line', 'milestone', 150),
        ]
        badges = []
        for name, desc, icon, btype, points in badge_data:
            badge, _ = Badge.objects.get_or_create(
                tenant=tenant, name=name,
                defaults={
                    'description': desc, 'icon': icon,
                    'criteria': desc, 'badge_type': btype,
                    'points_value': points,
                }
            )
            badges.append(badge)
        return badges

    def _seed_enrollments(self, tenant, courses, employees):
        statuses = ['enrolled', 'in_progress', 'completed', 'in_progress']
        for course in courses[:5]:
            selected_emps = random.sample(employees, min(5, len(employees)))
            for emp in selected_emps:
                status = random.choice(statuses)
                progress = 100 if status == 'completed' else random.randint(0, 80)
                score = random.uniform(60, 100) if status == 'completed' else None
                CourseEnrollment.objects.get_or_create(
                    tenant=tenant, course=course, employee=emp,
                    defaults={
                        'progress': progress,
                        'time_spent_minutes': random.randint(30, 500),
                        'status': status,
                        'score': round(score, 2) if score else None,
                        'started_date': date.today() - timedelta(days=random.randint(1, 30)) if status != 'enrolled' else None,
                        'completed_date': date.today() - timedelta(days=random.randint(0, 10)) if status == 'completed' else None,
                    }
                )

    def _seed_nominations(self, tenant, trainings, employees):
        statuses = ['pending', 'approved', 'approved', 'rejected', 'waitlisted']
        for training in trainings[:5]:
            selected_emps = random.sample(employees, min(3, len(employees)))
            for emp in selected_emps:
                nominator = random.choice(employees)
                status = random.choice(statuses)
                TrainingNomination.objects.get_or_create(
                    tenant=tenant, training=training, employee=emp,
                    defaults={
                        'nominated_by': nominator,
                        'reason': f'Employee would benefit from {training.title}.',
                        'status': status,
                        'approved_date': date.today() if status == 'approved' else None,
                        'approved_by': random.choice(employees) if status == 'approved' else None,
                        'rejection_reason': 'Budget constraints' if status == 'rejected' else '',
                    }
                )

    def _seed_attendance(self, tenant, sessions, employees):
        att_statuses = ['present', 'present', 'present', 'late', 'absent']
        for session in sessions:
            selected_emps = random.sample(employees, min(5, len(employees)))
            for emp in selected_emps:
                status = random.choice(att_statuses)
                TrainingAttendance.objects.get_or_create(
                    tenant=tenant, session=session, employee=emp,
                    defaults={
                        'status': status,
                        'check_in_time': '09:05:00' if status != 'absent' else None,
                        'check_out_time': '17:00:00' if status == 'present' else None,
                    }
                )

    def _seed_feedback(self, tenant, trainings, employees):
        for training in trainings[:5]:
            selected_emps = random.sample(employees, min(3, len(employees)))
            for emp in selected_emps:
                TrainingFeedback.objects.get_or_create(
                    tenant=tenant, training=training, employee=emp,
                    defaults={
                        'overall_rating': random.randint(3, 5),
                        'content_rating': random.randint(3, 5),
                        'instructor_rating': random.randint(2, 5),
                        'relevance_rating': random.randint(3, 5),
                        'comments': 'Great training session, learned a lot.',
                        'suggestions': 'More hands-on exercises would be helpful.',
                        'would_recommend': random.choice([True, True, True, False]),
                    }
                )

    def _seed_certificates(self, tenant, trainings, courses, employees):
        cert_num = 1000
        for i, emp in enumerate(employees[:8]):
            source = random.choice(trainings[:3]) if trainings else None
            course = random.choice(courses[:3]) if courses else None
            cert_number = f'CERT-{tenant.pk}-{cert_num + i}'
            TrainingCertificate.objects.get_or_create(
                tenant=tenant, certificate_number=cert_number,
                defaults={
                    'training': source if i % 2 == 0 else None,
                    'course': course if i % 2 != 0 else None,
                    'employee': emp,
                    'issue_date': date.today() - timedelta(days=random.randint(0, 180)),
                    'expiry_date': date.today() + timedelta(days=random.randint(180, 730)),
                    'status': 'active',
                }
            )

    def _seed_budgets(self, tenant, departments):
        years = ['2025-2026', '2024-2025']
        for year in years:
            for dept in departments[:3]:
                allocated = random.randint(100000, 500000)
                utilized = random.randint(0, allocated)
                TrainingBudget.objects.get_or_create(
                    tenant=tenant, fiscal_year=year, department=dept,
                    defaults={
                        'allocated_amount': allocated,
                        'utilized_amount': utilized,
                        'currency': 'INR',
                        'description': f'Training budget for {dept.name} - {year}',
                        'status': 'active' if year == '2025-2026' else 'closed',
                    }
                )

    def _seed_employee_badges(self, tenant, badges, courses, employees):
        for emp in employees[:5]:
            badge = random.choice(badges)
            course = random.choice(courses) if courses else None
            EmployeeBadge.objects.get_or_create(
                tenant=tenant, badge=badge, employee=emp,
                defaults={
                    'earned_date': date.today() - timedelta(days=random.randint(0, 90)),
                    'course': course,
                    'notes': f'Awarded for excellent performance.',
                }
            )
