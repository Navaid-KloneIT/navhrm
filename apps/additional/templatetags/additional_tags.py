from django import template

register = template.Library()


@register.filter
def asset_status_color(status):
    colors = {
        'available': 'success',
        'allocated': 'info',
        'maintenance': 'warning',
        'retired': 'secondary',
        'disposed': 'dark',
    }
    return colors.get(status, 'secondary')


@register.filter
def asset_condition_color(condition):
    colors = {
        'new': 'success',
        'good': 'info',
        'fair': 'warning',
        'poor': 'danger',
        'damaged': 'dark',
    }
    return colors.get(condition, 'secondary')


@register.filter
def allocation_status_color(status):
    colors = {
        'active': 'success',
        'returned': 'info',
        'overdue': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def maintenance_status_color(status):
    colors = {
        'scheduled': 'info',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def expense_status_color(status):
    colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'reimbursed': 'primary',
    }
    return colors.get(status, 'secondary')


@register.filter
def travel_status_color(status):
    colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'completed': 'primary',
        'cancelled': 'dark',
    }
    return colors.get(status, 'secondary')


@register.filter
def settlement_status_color(status):
    colors = {
        'pending': 'warning',
        'submitted': 'info',
        'approved': 'success',
        'settled': 'primary',
    }
    return colors.get(status, 'secondary')


@register.filter
def ticket_priority_color(priority):
    colors = {
        'low': 'info',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'dark',
    }
    return colors.get(priority, 'secondary')


@register.filter
def ticket_status_color(status):
    colors = {
        'open': 'info',
        'assigned': 'primary',
        'in_progress': 'warning',
        'resolved': 'success',
        'closed': 'secondary',
        'reopened': 'danger',
    }
    return colors.get(status, 'secondary')
