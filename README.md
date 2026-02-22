# NavHRM - Human Resource Management System

A multi-tenant HRM application built with Django and Bootstrap 5.

## Tech Stack

- **Backend:** Django 4.2 LTS, Python 3.10+
- **Database:** MySQL (MariaDB via XAMPP)
- **Frontend:** Bootstrap 5.3, jQuery, Remix Icons, Chart.js
- **Multi-tenancy:** Shared database with login-based tenant isolation

## Features

### Core HR Module
- **Employee Management** - Directory, profiles, documents, lifecycle tracking
- **Organizational Structure** - Departments, designations, org chart, cost centers
- **Employee Onboarding** - Templates, task checklists, asset allocation, orientation, welcome kits
- **Employee Offboarding** - Resignations, exit interviews, clearance process, F&F settlements, experience letters

### Dashboard & Theme System
- Multiple layout modes (vertical, horizontal, detached sidebar)
- Light/Dark theme toggle
- Sidebar variants (light, dark, colored)
- Sidebar sizes (default, compact, small icon, hover)
- Topbar color options
- Boxed/fluid width, fixed/scrollable position
- RTL/LTR support
- Preloader toggle
- Theme preferences saved to localStorage

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

4. **Create MySQL database**
   ```sql
   CREATE DATABASE navhrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Seed sample data**
   ```bash
   python manage.py seed_data
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Open in browser**
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
├── apps/
│   ├── core/           # Tenant model, middleware, base models
│   ├── accounts/       # Auth, users, profiles, invites
│   ├── organization/   # Company, departments, designations, org chart
│   ├── employees/      # Employee directory, profiles, documents
│   ├── onboarding/     # Onboarding tasks, assets, orientation
│   └── offboarding/    # Resignations, exit interviews, clearance, F&F
├── config/             # Django settings, URLs, WSGI
├── static/
│   ├── css/style.css   # Custom theme CSS
│   └── js/app.js       # Theme engine & UI JavaScript
├── templates/
│   ├── base.html       # Master layout
│   ├── partials/       # Sidebar, topbar, footer, theme settings
│   ├── auth/           # Login, register, forgot password
│   ├── dashboard/      # Dashboard index
│   ├── accounts/       # User management templates
│   ├── organization/   # Organization templates
│   ├── employees/      # Employee templates
│   ├── onboarding/     # Onboarding templates
│   └── offboarding/    # Offboarding templates
├── media/              # User uploads
├── manage.py
└── requirements.txt
```

## Configuration

Database settings are in `config/settings.py`. Update the `DATABASES` section if your MySQL credentials differ from defaults:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'navhrm',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
