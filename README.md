# NavHRM - Human Resource Management System

A multi-tenant HRM application built with Django and Bootstrap 5.

## Tech Stack

- **Backend:** Django 4.2 LTS, Python 3.10+
- **Database:** MySQL (MariaDB via XAMPP)
- **Frontend:** Bootstrap 5.3, jQuery, Remix Icons, Chart.js
- **Multi-tenancy:** Shared database with login-based tenant isolation
- **Config:** python-decouple for environment variables

## Features

### Core HR Module
- **Employee Management** - Directory, profiles, documents, lifecycle tracking
- **Organizational Structure** - Departments, designations, org chart, cost centers
- **Employee Onboarding** - Templates, task checklists, asset allocation, orientation, welcome kits
- **Employee Offboarding** - Resignations, exit interviews, clearance process, F&F settlements, experience letters

### Attendance & Leave Module
- **Attendance Management** - Web check-in/out, attendance records, monthly calendar view, attendance regularization, shift management & assignment
- **Leave Management** - Leave types (sick, casual, earned, unpaid, comp-off), leave policies (accrual, carry-forward, encashment), leave balances, leave applications with approval workflow, team leave calendar
- **Time Tracking** - Projects & tasks, weekly timesheets with approval workflow, time entries against projects, overtime requests & approval, billable hours tracking
- **Holiday Management** - National/regional/company holidays, holiday calendar, floating/optional holidays, location-based holiday policies

### Payroll Module
- **Salary Structure** - Pay components (earnings/deductions), salary structure templates, grade-wise CTC breakdown, employee salary assignments
- **Payroll Processing** - Monthly payroll periods, calculation engine, payroll approval workflow, salary holds, salary revisions with arrears
- **Statutory Compliance** - PF management (12%/12%, EPS, EDLI), ESI management (0.75%/3.25%), professional tax (state-wise slabs), LWF management, contribution tracking
- **Tax & Investment** - Old vs New tax regime selection, investment declarations (80C, 80D, HRA, LTA, etc.), proof uploads with verification, annual tax computation, monthly TDS projection
- **Payout & Reports** - Bank file generation (HDFC/ICICI/SBI/Axis/NEFT/CSV), digital payslips, payment register with reconciliation, reimbursement claims (LTA, medical, fuel, mobile)

### Performance Management Module
- **Goal Setting** - OKR/KPI management, goal alignment with cascading parent-child goals, weight assignment (validated to 100% per employee per period), configurable goal periods (monthly/quarterly/half-yearly/annual/custom), progress tracking with milestone updates, goal visibility (individual/team/department/organization), goal status workflow (draft → active → on_track/at_risk/behind → completed/cancelled)
- **Performance Review** - Configurable review cycles (annual/half-yearly/quarterly), multi-phase status workflow (draft → active → self_assessment → manager_review → peer_review → calibration → completed), self-assessment forms with per-goal ratings, manager review with per-goal ratings and comments, 360° peer feedback with reviewer assignment and acceptance workflow, rating calibration with final scores, 1.0-5.0 decimal rating scale
- **Continuous Feedback** - Real-time feedback (kudos/constructive/general), anonymous feedback option (sender hidden in UI, stored for audit), public/private/anonymous visibility controls, 1:1 meeting scheduling with date/time/location/duration, meeting notes (shared + separate manager/employee notes), meeting action items with assignment and due date tracking, given/received feedback tabs
- **Performance Improvement** - PIP management with defined goals and support plans, PIP checkpoints with status tracking (pending/on_track/needs_improvement/met/not_met), PIP outcome tracking (success/failure/extended/cancelled), warning letters (verbal/written/final) with acknowledgement and appeal workflow, coaching notes with session tracking, action items, and follow-up scheduling

### Training & Development Module
- **Training Management** - Training categories, training catalog (classroom/virtual/external), training sessions with scheduling, venue and instructor management, external vendor management with cost tracking, training calendar view
- **Learning Management (LMS)** - Course management with content types (video/document/SCORM/blended), course content ordering, role-based learning paths with ordered course sequences, assessments (quizzes/tests/certification exams) with multiple question types, gamification with badges and points, course enrollment with progress tracking (completion status, time spent, scores)
- **Training Administration** - Employee nomination with approval/rejection workflow, session attendance tracking (present/absent/late/excused), post-training feedback with multi-criteria ratings (overall/content/instructor/relevance), auto-generated completion certificates with expiry tracking, department-wise training budget allocation and utilization tracking

### Employee Self-Service Module
- **Personal Information** - Profile management (personal/contact/bank details), avatar upload, emergency contacts CRUD, family members with dependent/nominee tracking, insurance coverage, personal document viewer
- **Request Management** - Leave application (wraps attendance module), attendance regularization requests, document requests (experience letter/salary certificate/employment certificate/bonafide/address proof), ID card requests (new/replacement/renewal/update), asset requests (laptop/monitor/headset/furniture/etc.) with priority levels and approval workflow
- **Communication Hub** - Company/department announcements with pinning and priority, birthday & work anniversary celebrations with wish sending, employee engagement surveys with multiple question types (text/single choice/multiple choice/rating/yes-no), anonymous suggestion box with upvotes and admin response, HR help desk ticketing system with comment threads and status tracking

### Reports & Analytics Module
- **HR Reports** - Headcount report (active employees, new joins, exits by department), attrition report (turnover analysis, trends), diversity report (gender, age, tenure demographics), cost reports (salary cost, department-wise), hiring reports (time-to-hire, source analysis)
- **Attendance Reports** - Attendance summary (daily/monthly rates), late/early departure patterns, absenteeism analysis (frequent absentees, department-wise), overtime tracking (hours, cost), utilization report (productivity metrics)
- **Leave Reports** - Leave register (availed, balances), leave liability (accrued leave liability calculation), comp-off report (earned vs availed), leave trend (monthly/seasonal patterns)
- **Payroll Reports** - Salary register (monthly details), tax reports (TDS, investment summary), statutory reports (PF, ESI, PT contributions), cost analysis (CTC breakdown, cost center reports)
- **Analytics Dashboard** - Executive dashboard with key HR metrics, headcount trends, attrition analysis, workforce composition, department cost distribution, gender distribution charts

### Admin & Settings Module
- **User Management** - User accounts with CRUD, custom roles & permissions matrix (module-level access control), role assignment to users, login history with IP tracking and session audit
- **Workflow Configuration** - Multi-level approval workflows (leave, expense, timesheet, etc.), customizable email templates with variable placeholders, notification settings per event (email/in-app/both), escalation rules with auto-reminders and auto-approval
- **System Configuration** - Company settings (logo, timezone, date format, currency), financial year setup with auto-generated monthly periods, working hours policies (grace time, overtime threshold, working days), location/office management, third-party integration settings (SMTP, Slack, Teams, biometric, APIs)
- **Audit & Compliance** - Full audit trail logging all CRUD operations with old/new value diffs, data privacy & GDPR compliance dashboard, data retention policies (archive/anonymize/delete), access logs (login/logout tracking), backup configuration and recovery with manual/scheduled options

### Additional Modules

#### Asset Management
- **Asset Categories** - Categorize assets (laptops, phones, furniture, vehicles, etc.)
- **Asset Register** - Track all assets with asset ID, serial number, purchase details, warranty, condition and status
- **Asset Allocation** - Assign assets to employees with allocation tracking, expected return dates
- **Asset Return** - Process asset returns with condition assessment during offboarding or transfers
- **Asset Maintenance** - Schedule and track preventive, corrective, and AMC maintenance with vendor and cost tracking

#### Expense Management
- **Expense Categories** - Define expense types (travel, food, office supplies, etc.) with maximum limits
- **Expense Policies** - Configure policies per employee group (all/department/designation) with amount limits and receipt requirements
- **Expense Claims** - Submit claims with receipts, multi-level approval workflow (draft → submitted → approved → reimbursed), rejection with reason tracking

#### Travel Management
- **Travel Policies** - Define travel class (economy/business/first), daily allowance, and hotel limits
- **Travel Requests** - Request domestic/international travel with itinerary, cost estimation, advance requests, and approval workflow
- **Travel Expenses** - Record itemized travel expenses (flight, hotel, cab, food) with receipt uploads
- **Travel Settlement** - Post-travel expense settlement with advance reconciliation

#### Helpdesk Module
- **Ticket Categories** - Define categories (IT Support, HR Query, Facilities, Finance, Admin) with SLA response and resolution hours
- **Ticket Management** - Raise, assign, track, and resolve tickets with priority levels (low/medium/high/critical), status workflow (open → assigned → in_progress → resolved → closed), satisfaction rating
- **Ticket Comments** - Comment threads with internal notes (visible only to staff) and file attachments
- **Knowledge Base** - Self-help articles organized by category with view tracking and publish controls

#### Compensation & Benefits
- **Salary Benchmarking** - Market salary data by designation, industry and location with min/median/max salary, percentile tracking
- **Benefits Administration** - Benefit plans (health/life/dental/vision/retirement/disability/wellness) with employee/employer premiums, employee enrollment with coverage levels (employee only/spouse/children/family)
- **Flexible Benefits** - Cafeteria-style benefit plans with amount/points allocation, benefit options by category, employee opt-in/opt-out selections
- **Stock/ESOP Management** - Equity grants (ESOP/RSU/stock option/phantom stock) with auto-generated grant numbers, vesting schedules (monthly/quarterly/annual/cliff), vesting event tracking, exercise records with profit calculation
- **Compensation Planning** - Compensation plans (merit/promotion/market adjustment/annual review) with budget tracking and utilization, employee recommendations with current/recommended salary and increase percentage, approval workflow
- **Rewards & Recognition** - Reward programs (spot award/service award/peer recognition/performance bonus/team award) with budget tracking, employee recognitions with nominee/nominator, approval workflow (nominated → approved → awarded)

### Talent Management & Succession Planning Module
- **Talent Pool** - High-potential employee identification, talent assessments with performance/potential ratings (1-5), auto-calculated 9-box grid categories, interactive 9-box grid visualization
- **Succession Planning** - Critical role mapping with criticality levels (critical/high/medium/low), successor identification with readiness timelines (ready now/1-2 years/3-5 years), development needs tracking
- **Career Pathing** - Role progression maps with sequenced designation steps, skill and competency requirements per step, employee career plans linking to paths with current/target step tracking
- **Internal Mobility** - Internal job postings with status workflow (open/closed/on_hold), transfer applications with review process (applied → shortlisted → selected/rejected)
- **Talent Reviews** - Calibration sessions with review periods, participant management with initial and calibrated performance/potential ratings, development recommendations
- **Retention Strategies** - Flight risk analysis with risk levels (critical/high/medium/low), retention action plans with responsible person tracking, action items with assignment and status tracking

### Workforce Planning Module
- **Demand Forecasting** - Headcount planning based on business growth, department/designation-level projections, fiscal year tracking, growth rate calculation, status workflow (draft/submitted/approved/rejected), priority levels (low/medium/high/critical)
- **Supply Analysis** - Skills inventory with employee skill tracking, proficiency levels (beginner/intermediate/advanced/expert), certification tracking with expiry dates; talent availability analysis with department-level counts (available/on-notice/retiring/transfer-ready)
- **Gap Analysis** - Current vs. future workforce needs comparison, auto-computed gap type (surplus/deficit/balanced), skills gap descriptions, action plans, priority-based tracking
- **Budget Planning** - Hiring budget management with allocated/utilized tracking, position budgeting, utilization percentage; salary forecasting with current vs. projected salary analysis, increment percentages, cost impact calculations
- **Scenario Planning** - What-if analysis with scenario types (growth/restructuring/downsizing/merger/expansion), base/projection year tracking, assumptions documentation, per-department scenario details with headcount and cost impact projections
- **Workforce Analytics** - Productivity metrics with target vs. actual tracking, achievement percentages, variance analysis; utilization rates with total/productive/billable/non-billable hours tracking

### Recruitment Module
- **Job Requisitions** - Create job posts, status workflow (draft → approved → published → closed), priority levels, budget tracking
- **Job Templates** - Pre-defined job description templates for quick requisition creation
- **Candidate Management** - Talent pool, candidate profiles, resume uploads, skills tracking, source tracking
- **Applications** - Link candidates to jobs, status pipeline (applied → screening → shortlisted → interview → offered → hired)
- **Interview Process** - Schedule interviews (in-person/phone/video), assign interviewers, multi-criteria feedback with star ratings
- **Offer Management** - Create offers with salary, joining date, probation, benefits, approval workflow, status tracking
- **Public Career Page** - Standalone public-facing career page for external candidates to browse jobs and submit applications without login

### Authentication & User Management
- Login, registration, forgot password
- Role-based access (super admin, tenant admin, HR manager, HR staff, manager, employee)
- User invite system with token-based acceptance
- User profiles with theme preferences

### Multi-Tenancy
- Shared database with `tenant_id` on all models
- Middleware-based tenant resolution from logged-in user
- Auto-filtered querysets ensure data isolation between tenants

## Setup

### Prerequisites
- Python 3.10+
- MySQL (XAMPP recommended)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Navaid-KloneIT/navhrm.git
   cd navhrm
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update the values for your environment:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=navhrm
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Create MySQL database**
   ```sql
   CREATE DATABASE navhrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Seed sample data**
   ```bash
   python manage.py seed_data
   python manage.py seed_recruitment
   python manage.py seed_attendance
   python manage.py seed_payroll
   python manage.py seed_payout
   python manage.py seed_performance
   python manage.py seed_training
   python manage.py seed_ess
   python manage.py seed_administration
   python manage.py seed_additional
   python manage.py seed_compensation
   python manage.py seed_talent
   python manage.py seed_workforce
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Open in browser**
   ```
   http://localhost:8000
   ```

### Default Login Credentials

After running `seed_data`, three tenant accounts are available:

| Username | Password     | Company           |
|----------|-------------|-------------------|
| admin1   | password123 | Tenant 1          |
| admin2   | password123 | Tenant 2          |
| admin3   | password123 | Tenant 3          |

## Project Structure

```
navhrm/
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment template for new setups
├── apps/
│   ├── core/              # Tenant model, middleware, base models
│   ├── accounts/          # Auth, users, profiles, invites
│   ├── organization/      # Company, departments, designations, org chart
│   ├── employees/         # Employee directory, profiles, documents
│   ├── onboarding/        # Onboarding tasks, assets, orientation
│   ├── offboarding/       # Resignations, exit interviews, clearance, F&F
│   ├── recruitment/       # Job requisitions, candidates, interviews, offers
│   ├── attendance/        # Attendance, leave, time tracking, holidays
│   ├── payroll/           # Salary structure, payroll, statutory, tax, payout
│   ├── performance/       # Goals, reviews, feedback, PIP, warnings, coaching
│   ├── training/          # Training management, LMS, administration
│   ├── ess/               # Employee self-service, requests, communication
│   ├── reports/           # Reports & analytics (no models, read-only views)
│   ├── administration/    # Admin & settings, roles, workflows, audit
│   ├── additional/        # Asset, expense, travel management & helpdesk
│   ├── compensation/      # Compensation & benefits, salary benchmarking, ESOP
│   ├── talent/            # Talent management, succession planning, career pathing
│   └── workforce/         # Workforce planning, demand forecasting, gap analysis
├── config/                # Django settings, URLs, WSGI
├── static/
│   ├── css/style.css      # Custom theme CSS
│   └── js/app.js          # Theme engine & UI JavaScript
├── templates/
│   ├── base.html          # Master layout
│   ├── partials/          # Sidebar, topbar, footer, theme settings
│   ├── auth/              # Login, register, forgot password
│   ├── dashboard/         # Dashboard index
│   ├── accounts/          # User management templates
│   ├── organization/      # Organization templates
│   ├── employees/         # Employee templates
│   ├── onboarding/        # Onboarding templates
│   ├── offboarding/       # Offboarding templates
│   ├── recruitment/       # Recruitment templates + public career page
│   ├── attendance/        # Attendance & leave module templates
│   ├── payroll/           # Payroll module templates (44 files)
│   ├── performance/       # Performance management templates (33 files)
│   ├── training/          # Training & development templates (35 files)
│   ├── ess/               # Employee self-service templates (39 files)
│   ├── reports/           # Reports & analytics templates (20 files)
│   ├── administration/    # Admin & settings templates (33 files)
│   ├── additional/        # Additional modules templates (31 files)
│   ├── compensation/      # Compensation & benefits templates (31 files)
│   ├── talent/            # Talent management templates (32 files)
│   └── workforce/         # Workforce planning templates (28 files)
├── media/                 # User uploads
├── manage.py
└── requirements.txt
```

## Environment Variables

All configuration is managed via the `.env` file using `python-decouple`. See `.env.example` for all available variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | - | Django secret key (required) |
| `DEBUG` | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts |
| `DB_ENGINE` | `django.db.backends.mysql` | Database engine |
| `DB_NAME` | `navhrm` | Database name |
| `DB_USER` | `root` | Database username |
| `DB_PASSWORD` | *(empty)* | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `3306` | Database port |
| `APP_NAME` | `NavHRM` | Application display name |
| `TIME_ZONE` | `UTC` | Server timezone |
| `LANGUAGE_CODE` | `en-us` | Default language |
| `LOGIN_URL` | `/accounts/login/` | Login page URL |
| `LOGIN_REDIRECT_URL` | `/` | Redirect after login |
| `LOGOUT_REDIRECT_URL` | `/accounts/login/` | Redirect after logout |
