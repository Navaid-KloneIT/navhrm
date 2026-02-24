from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Access dict by key in templates: {{ my_dict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def attendance_badge_color(status):
    """Return Bootstrap color class for attendance status."""
    colors = {
        'present': 'success',
        'absent': 'danger',
        'half_day': 'warning',
        'on_leave': 'info',
        'holiday': 'primary',
        'weekend': 'secondary',
        'not_marked': 'light',
    }
    return colors.get(status, 'secondary')


@register.filter
def leave_status_color(status):
    """Return Bootstrap color class for leave/approval status."""
    colors = {
        'draft': 'secondary',
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'cancelled': 'dark',
    }
    return colors.get(status, 'secondary')


@register.filter
def timesheet_status_color(status):
    """Return Bootstrap color class for timesheet status."""
    colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'approved': 'success',
        'rejected': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def project_status_color(status):
    """Return Bootstrap color class for project status."""
    colors = {
        'active': 'success',
        'on_hold': 'warning',
        'completed': 'info',
        'archived': 'secondary',
    }
    return colors.get(status, 'secondary')
