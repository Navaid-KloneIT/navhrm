from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear


def get_headcount(tenant, target_date=None):
    """Return active employee count at a given date (defaults to today)."""
    from apps.employees.models import Employee
    if target_date is None:
        target_date = date.today()
    qs = Employee.all_objects.filter(
        tenant=tenant,
        date_of_joining__lte=target_date,
    ).exclude(
        date_of_leaving__isnull=False,
        date_of_leaving__lt=target_date,
    )
    return qs.count()


def get_attrition_rate(tenant, start_date, end_date):
    """Calculate attrition rate: exits / avg headcount * 100."""
    from apps.employees.models import Employee
    exits = Employee.all_objects.filter(
        tenant=tenant,
        status__in=['resigned', 'terminated'],
        date_of_leaving__gte=start_date,
        date_of_leaving__lte=end_date,
    ).count()
    hc_start = get_headcount(tenant, start_date)
    hc_end = get_headcount(tenant, end_date)
    avg_hc = (hc_start + hc_end) / 2
    if avg_hc == 0:
        return 0
    return round((exits / avg_hc) * 100, 1)


def get_monthly_headcount_trend(tenant, months=12):
    """Return list of {month, year, label, count} for last N months."""
    today = date.today()
    trend = []
    for i in range(months - 1, -1, -1):
        d = today - relativedelta(months=i)
        last_day = date(d.year, d.month, 1) + relativedelta(months=1) - timedelta(days=1)
        count = get_headcount(tenant, last_day)
        trend.append({
            'month': d.month,
            'year': d.year,
            'label': d.strftime('%b %Y'),
            'count': count,
        })
    return trend


def get_monthly_exits(tenant, months=12):
    """Return list of {label, count} of exits per month for last N months."""
    from apps.employees.models import Employee
    today = date.today()
    trend = []
    for i in range(months - 1, -1, -1):
        d = today - relativedelta(months=i)
        first_day = date(d.year, d.month, 1)
        last_day = first_day + relativedelta(months=1) - timedelta(days=1)
        count = Employee.all_objects.filter(
            tenant=tenant,
            status__in=['resigned', 'terminated'],
            date_of_leaving__gte=first_day,
            date_of_leaving__lte=last_day,
        ).count()
        trend.append({
            'label': d.strftime('%b %Y'),
            'count': count,
        })
    return trend


def get_department_breakdown(tenant, queryset=None, count_field=None):
    """Return department-wise counts. If queryset given, annotate it; else count active employees."""
    from apps.employees.models import Employee
    from apps.organization.models import Department
    departments = Department.all_objects.filter(
        tenant=tenant, is_active=True
    ).annotate(
        emp_count=Count(
            'employees',
            filter=Q(employees__status='active', employees__tenant=tenant)
        )
    ).values('name', 'emp_count').order_by('-emp_count')
    return list(departments)


def get_age_groups(employees):
    """Categorize employees into age bands based on date_of_birth."""
    today = date.today()
    groups = {'18-25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56+': 0}
    for emp in employees:
        if not emp.date_of_birth:
            continue
        age = (today - emp.date_of_birth).days // 365
        if age <= 25:
            groups['18-25'] += 1
        elif age <= 35:
            groups['26-35'] += 1
        elif age <= 45:
            groups['36-45'] += 1
        elif age <= 55:
            groups['46-55'] += 1
        else:
            groups['56+'] += 1
    return groups


def get_tenure_groups(employees):
    """Categorize employees by years of service."""
    today = date.today()
    groups = {'< 1 yr': 0, '1-3 yrs': 0, '3-5 yrs': 0, '5-10 yrs': 0, '10+ yrs': 0}
    for emp in employees:
        if not emp.date_of_joining:
            continue
        years = (today - emp.date_of_joining).days / 365.25
        if years < 1:
            groups['< 1 yr'] += 1
        elif years < 3:
            groups['1-3 yrs'] += 1
        elif years < 5:
            groups['3-5 yrs'] += 1
        elif years < 10:
            groups['5-10 yrs'] += 1
        else:
            groups['10+ yrs'] += 1
    return groups


def safe_division(numerator, denominator, default=0):
    """Safe division that returns default if denominator is 0."""
    if denominator == 0:
        return default
    return numerator / denominator
