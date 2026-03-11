from django import template

register = template.Library()


@register.filter
def talent_category_color(category):
    colors = {
        'high_potential': 'success',
        'key_talent': 'primary',
        'solid_performer': 'info',
        'emerging_talent': 'warning',
        'inconsistent_performer': 'secondary',
        'underperformer': 'danger',
        'new_to_role': 'dark',
        'risk_of_stagnation': 'warning',
        'misplaced_talent': 'danger',
    }
    return colors.get(category, 'secondary')


@register.filter
def criticality_color(criticality):
    colors = {
        'critical': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'secondary',
    }
    return colors.get(criticality, 'secondary')


@register.filter
def readiness_color(readiness):
    colors = {
        'ready_now': 'success',
        'ready_1_2_years': 'warning',
        'ready_3_5_years': 'info',
    }
    return colors.get(readiness, 'secondary')


@register.filter
def successor_status_color(status):
    colors = {
        'identified': 'info',
        'in_development': 'warning',
        'ready': 'success',
        'placed': 'primary',
        'withdrawn': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def career_path_status_color(status):
    colors = {
        'active': 'success',
        'draft': 'secondary',
        'archived': 'dark',
    }
    return colors.get(status, 'secondary')


@register.filter
def career_plan_status_color(status):
    colors = {
        'active': 'success',
        'completed': 'primary',
        'on_hold': 'warning',
        'cancelled': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def posting_status_color(status):
    colors = {
        'open': 'success',
        'closed': 'secondary',
        'on_hold': 'warning',
    }
    return colors.get(status, 'secondary')


@register.filter
def transfer_status_color(status):
    colors = {
        'applied': 'info',
        'shortlisted': 'warning',
        'selected': 'success',
        'rejected': 'danger',
        'withdrawn': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def review_session_status_color(status):
    colors = {
        'scheduled': 'info',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def flight_risk_color(risk_level):
    colors = {
        'critical': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'success',
    }
    return colors.get(risk_level, 'secondary')


@register.filter
def retention_plan_status_color(status):
    colors = {
        'planned': 'info',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def retention_action_status_color(status):
    colors = {
        'pending': 'secondary',
        'in_progress': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
    }
    return colors.get(status, 'secondary')
