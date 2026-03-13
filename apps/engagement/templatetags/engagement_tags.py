from django import template

register = template.Library()


@register.filter
def survey_type_color(value):
    colors = {
        'pulse': 'info',
        'enps': 'primary',
        'engagement': 'success',
        'custom': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def survey_status_color(value):
    colors = {
        'draft': 'secondary',
        'active': 'success',
        'closed': 'warning',
        'archived': 'dark',
    }
    return colors.get(value, 'secondary')


@register.filter
def action_plan_priority_color(value):
    colors = {
        'low': 'secondary',
        'medium': 'info',
        'high': 'warning',
        'critical': 'danger',
    }
    return colors.get(value, 'secondary')


@register.filter
def action_plan_status_color(value):
    colors = {
        'pending': 'warning',
        'in_progress': 'info',
        'completed': 'success',
        'cancelled': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def wellbeing_category_color(value):
    colors = {
        'mental_health': 'primary',
        'physical_health': 'success',
        'nutrition': 'warning',
        'financial': 'info',
        'social': 'danger',
        'mindfulness': 'dark',
    }
    return colors.get(value, 'secondary')


@register.filter
def resource_type_color(value):
    colors = {
        'article': 'info',
        'video': 'primary',
        'podcast': 'warning',
        'webinar': 'success',
        'tool': 'secondary',
        'guide': 'dark',
    }
    return colors.get(value, 'secondary')


@register.filter
def challenge_type_color(value):
    colors = {
        'steps': 'success',
        'meditation': 'primary',
        'hydration': 'info',
        'exercise': 'warning',
        'sleep': 'dark',
        'custom': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def challenge_status_color(value):
    colors = {
        'draft': 'secondary',
        'active': 'success',
        'completed': 'primary',
        'cancelled': 'danger',
    }
    return colors.get(value, 'secondary')


@register.filter
def arrangement_type_color(value):
    colors = {
        'remote': 'primary',
        'hybrid': 'info',
        'flexible_hours': 'warning',
        'compressed_week': 'success',
        'job_sharing': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def arrangement_status_color(value):
    colors = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'expired': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def service_type_color(value):
    colors = {
        'counseling': 'primary',
        'legal': 'info',
        'financial': 'warning',
        'career': 'success',
        'family': 'secondary',
        'substance_abuse': 'danger',
    }
    return colors.get(value, 'secondary')


@register.filter
def session_type_color(value):
    colors = {
        'individual': 'primary',
        'group': 'info',
        'family': 'warning',
        'crisis': 'danger',
    }
    return colors.get(value, 'secondary')


@register.filter
def session_status_color(value):
    colors = {
        'scheduled': 'info',
        'completed': 'success',
        'cancelled': 'secondary',
        'no_show': 'danger',
    }
    return colors.get(value, 'secondary')


@register.filter
def culture_status_color(value):
    colors = {
        'draft': 'secondary',
        'active': 'success',
        'completed': 'primary',
    }
    return colors.get(value, 'secondary')


@register.filter
def nomination_status_color(value):
    colors = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
    }
    return colors.get(value, 'secondary')


@register.filter
def event_type_color(value):
    colors = {
        'team_building': 'primary',
        'celebration': 'success',
        'sports': 'warning',
        'cultural': 'info',
        'learning': 'dark',
        'social': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def event_status_color(value):
    colors = {
        'planned': 'info',
        'ongoing': 'warning',
        'completed': 'success',
        'cancelled': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def rsvp_color(value):
    colors = {
        'attending': 'success',
        'maybe': 'warning',
        'not_attending': 'danger',
    }
    return colors.get(value, 'secondary')


@register.filter
def interest_group_category_color(value):
    colors = {
        'sports': 'success',
        'arts': 'primary',
        'technology': 'info',
        'reading': 'warning',
        'music': 'dark',
        'gaming': 'secondary',
        'outdoor': 'success',
        'cooking': 'warning',
        'other': 'secondary',
    }
    return colors.get(value, 'secondary')


@register.filter
def volunteer_status_color(value):
    colors = {
        'planned': 'info',
        'ongoing': 'warning',
        'completed': 'success',
        'cancelled': 'secondary',
    }
    return colors.get(value, 'secondary')
