from django import template

register = template.Library()


@register.filter
def forecast_status_color(status):
    colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'approved': 'success',
        'rejected': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def priority_color(priority):
    colors = {
        'low': 'secondary',
        'medium': 'info',
        'high': 'warning',
        'critical': 'danger',
    }
    return colors.get(priority, 'secondary')


@register.filter
def proficiency_color(level):
    colors = {
        'beginner': 'secondary',
        'intermediate': 'info',
        'advanced': 'warning',
        'expert': 'success',
    }
    return colors.get(level, 'secondary')


@register.filter
def gap_type_color(gap_type):
    colors = {
        'surplus': 'info',
        'deficit': 'danger',
        'balanced': 'success',
    }
    return colors.get(gap_type, 'secondary')


@register.filter
def gap_status_color(status):
    colors = {
        'identified': 'info',
        'in_progress': 'warning',
        'resolved': 'success',
        'deferred': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def budget_status_color(status):
    colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'approved': 'success',
        'rejected': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def scenario_type_color(scenario_type):
    colors = {
        'growth': 'success',
        'restructuring': 'warning',
        'downsizing': 'danger',
        'merger': 'info',
        'expansion': 'primary',
    }
    return colors.get(scenario_type, 'secondary')


@register.filter
def scenario_status_color(status):
    colors = {
        'draft': 'secondary',
        'active': 'success',
        'archived': 'dark',
    }
    return colors.get(status, 'secondary')
