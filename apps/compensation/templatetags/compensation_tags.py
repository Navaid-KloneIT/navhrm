from django import template

register = template.Library()


@register.filter
def benefit_plan_type_color(plan_type):
    colors = {
        'health_insurance': 'success',
        'life_insurance': 'info',
        'dental': 'primary',
        'vision': 'warning',
        'retirement': 'secondary',
        'disability': 'danger',
        'wellness': 'success',
        'other': 'dark',
    }
    return colors.get(plan_type, 'secondary')


@register.filter
def benefit_status_color(status):
    colors = {
        'active': 'success',
        'pending': 'warning',
        'cancelled': 'danger',
        'expired': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def coverage_level_color(level):
    colors = {
        'employee_only': 'info',
        'employee_spouse': 'primary',
        'employee_children': 'warning',
        'family': 'success',
    }
    return colors.get(level, 'secondary')


@register.filter
def flex_allocation_type_color(alloc_type):
    colors = {
        'amount': 'success',
        'points': 'info',
    }
    return colors.get(alloc_type, 'secondary')


@register.filter
def flex_period_color(period):
    colors = {
        'monthly': 'info',
        'quarterly': 'primary',
        'annual': 'success',
    }
    return colors.get(period, 'secondary')


@register.filter
def flex_selection_status_color(status):
    colors = {
        'selected': 'success',
        'opted_out': 'secondary',
        'pending_approval': 'warning',
        'approved': 'primary',
    }
    return colors.get(status, 'secondary')


@register.filter
def grant_type_color(grant_type):
    colors = {
        'esop': 'success',
        'rsu': 'info',
        'stock_option': 'primary',
        'phantom_stock': 'warning',
    }
    return colors.get(grant_type, 'secondary')


@register.filter
def grant_status_color(status):
    colors = {
        'active': 'info',
        'partially_vested': 'warning',
        'fully_vested': 'success',
        'exercised': 'primary',
        'cancelled': 'danger',
        'expired': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def exercise_status_color(status):
    colors = {
        'pending': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def compensation_plan_status_color(status):
    colors = {
        'draft': 'secondary',
        'active': 'info',
        'under_review': 'warning',
        'approved': 'success',
        'completed': 'primary',
    }
    return colors.get(status, 'secondary')


@register.filter
def compensation_plan_type_color(plan_type):
    colors = {
        'merit_increase': 'success',
        'promotion': 'info',
        'market_adjustment': 'primary',
        'annual_review': 'warning',
        'special': 'danger',
    }
    return colors.get(plan_type, 'secondary')


@register.filter
def increase_type_color(increase_type):
    colors = {
        'merit': 'success',
        'promotion': 'info',
        'market_adjustment': 'primary',
        'retention': 'warning',
        'equity': 'danger',
    }
    return colors.get(increase_type, 'secondary')


@register.filter
def recommendation_status_color(status):
    colors = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'implemented': 'primary',
    }
    return colors.get(status, 'secondary')


@register.filter
def reward_program_type_color(program_type):
    colors = {
        'spot_award': 'success',
        'service_award': 'info',
        'peer_recognition': 'primary',
        'performance_bonus': 'warning',
        'team_award': 'danger',
    }
    return colors.get(program_type, 'secondary')


@register.filter
def recognition_type_color(recognition_type):
    colors = {
        'spot_award': 'success',
        'service_award': 'info',
        'peer_recognition': 'primary',
        'achievement': 'warning',
        'innovation': 'danger',
        'leadership': 'dark',
        'teamwork': 'secondary',
    }
    return colors.get(recognition_type, 'secondary')


@register.filter
def recognition_status_color(status):
    colors = {
        'nominated': 'info',
        'approved': 'success',
        'awarded': 'primary',
        'rejected': 'danger',
    }
    return colors.get(status, 'secondary')
