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
   git clone <repository-url>
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
│   └── attendance/        # Attendance, leave, time tracking, holidays
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
│   └── attendance/        # Attendance & leave module templates
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
