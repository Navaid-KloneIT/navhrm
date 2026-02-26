from django.db import models
from apps.core.models import TenantAwareModel, TimeStampedModel


# ===========================================================================
# Training Management Models
# ===========================================================================

class TrainingCategory(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Training Categories'

    def __str__(self):
        return self.name


class TrainingVendor(TenantAwareModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Training(TenantAwareModel, TimeStampedModel):
    TRAINING_TYPE_CHOICES = [
        ('classroom', 'Classroom Training'),
        ('virtual', 'Virtual Training'),
        ('external', 'External Training'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(TrainingCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='trainings')
    training_type = models.CharField(max_length=20, choices=TRAINING_TYPE_CHOICES, default='classroom')
    vendor = models.ForeignKey(TrainingVendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='trainings')
    instructor_name = models.CharField(max_length=255, blank=True)
    instructor_email = models.EmailField(blank=True)
    duration_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    max_participants = models.IntegerField(default=0)
    cost_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')
    prerequisites = models.TextField(blank=True)
    objectives = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TrainingSession(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    session_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    meeting_link = models.URLField(blank=True)
    instructor = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='training_sessions_as_instructor')
    max_participants = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-session_date', '-start_time']

    def __str__(self):
        return f"{self.title} - {self.session_date}"


# ===========================================================================
# Learning Management Models
# ===========================================================================

class Course(TenantAwareModel, TimeStampedModel):
    COURSE_TYPE_CHOICES = [
        ('video', 'Video'),
        ('document', 'Document'),
        ('scorm', 'SCORM Package'),
        ('blended', 'Blended'),
    ]
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(TrainingCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='video')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    is_mandatory = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='training/course_thumbnails/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CourseContent(TenantAwareModel, TimeStampedModel):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('document', 'Document'),
        ('scorm', 'SCORM Package'),
        ('link', 'External Link'),
        ('text', 'Text Content'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='document')
    content_url = models.URLField(blank=True)
    content_file = models.FileField(upload_to='training/course_content/', blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class LearningPath(TenantAwareModel, TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_role = models.CharField(max_length=255, blank=True)
    target_department = models.ForeignKey('organization.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='learning_paths')
    is_mandatory = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LearningPathCourse(TenantAwareModel, TimeStampedModel):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='path_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_paths')
    order = models.IntegerField(default=0)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ['learning_path', 'course']

    def __str__(self):
        return f"{self.learning_path.title} → {self.course.title}"


class CourseEnrollment(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='course_enrollments')
    enrolled_date = models.DateField(auto_now_add=True)
    started_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    progress = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-enrolled_date']
        unique_together = ['course', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.course.title}"


class Assessment(TenantAwareModel, TimeStampedModel):
    ASSESSMENT_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('test', 'Test'),
        ('certification', 'Certification Exam'),
    ]

    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES, default='quiz')
    passing_score = models.IntegerField(default=60)
    time_limit_minutes = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=1)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AssessmentQuestion(TenantAwareModel, TimeStampedModel):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_answer = models.CharField(max_length=500)
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class Badge(TenantAwareModel, TimeStampedModel):
    BADGE_TYPE_CHOICES = [
        ('course_completion', 'Course Completion'),
        ('path_completion', 'Learning Path Completion'),
        ('assessment', 'Assessment Achievement'),
        ('milestone', 'Milestone'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Remix icon class, e.g., ri-medal-line')
    criteria = models.TextField(blank=True)
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPE_CHOICES, default='course_completion')
    points_value = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ===========================================================================
# Training Administration Models
# ===========================================================================

class TrainingNomination(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    ]

    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='nominations')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='training_nominations')
    nominated_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='nominations_made')
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='nominations_approved')
    approved_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} → {self.training.title}"


class TrainingAttendance(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='attendance_records')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='training_attendance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-session__session_date']
        unique_together = ['session', 'employee']
        verbose_name_plural = 'Training Attendance'

    def __str__(self):
        return f"{self.employee} - {self.session.title} ({self.get_status_display()})"


class TrainingFeedback(TenantAwareModel, TimeStampedModel):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='feedbacks')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='training_feedbacks')
    overall_rating = models.IntegerField(default=3)
    content_rating = models.IntegerField(default=3)
    instructor_rating = models.IntegerField(default=3)
    relevance_rating = models.IntegerField(default=3)
    comments = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    would_recommend = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['training', 'employee']

    def __str__(self):
        return f"Feedback: {self.employee} on {self.training.title}"


class TrainingCertificate(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]

    training = models.ForeignKey(Training, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='training_certificates')
    certificate_number = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificate #{self.certificate_number} - {self.employee}"


class TrainingBudget(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    department = models.ForeignKey('organization.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='training_budgets')
    fiscal_year = models.CharField(max_length=20)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    utilized_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    class Meta:
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"Budget {self.fiscal_year} - {self.department or 'Company-wide'}"

    @property
    def remaining_amount(self):
        return self.allocated_amount - self.utilized_amount

    @property
    def utilization_percentage(self):
        if self.allocated_amount > 0:
            return round((self.utilized_amount / self.allocated_amount) * 100, 1)
        return 0


class EmployeeBadge(TenantAwareModel, TimeStampedModel):
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='earned_badges')
    earned_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='badges_awarded')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-earned_date']
        unique_together = ['badge', 'employee']

    def __str__(self):
        return f"{self.employee} earned {self.badge.name}"
