from django import template

register = template.Library()


@register.filter
def labor_law_status_color(status):
    colors = {
        'active': 'success',
        'amended': 'warning',
        'repealed': 'danger',
        'draft': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def labor_law_category_color(category):
    colors = {
        'wages': 'primary',
        'working_hours': 'info',
        'leave': 'success',
        'safety': 'danger',
        'discrimination': 'warning',
        'termination': 'dark',
        'child_labor': 'danger',
        'social_security': 'primary',
        'industrial_relations': 'info',
        'other': 'secondary',
    }
    return colors.get(category, 'secondary')


@register.filter
def compliance_status_color(status):
    colors = {
        'compliant': 'success',
        'non_compliant': 'danger',
        'partial': 'warning',
        'under_review': 'info',
    }
    return colors.get(status, 'secondary')


@register.filter
def contract_type_color(contract_type):
    colors = {
        'permanent': 'success',
        'fixed_term': 'info',
        'probation': 'warning',
        'internship': 'primary',
        'consultant': 'dark',
        'part_time': 'secondary',
    }
    return colors.get(contract_type, 'secondary')


@register.filter
def contract_status_color(status):
    colors = {
        'draft': 'secondary',
        'active': 'success',
        'expired': 'dark',
        'terminated': 'danger',
        'renewed': 'info',
    }
    return colors.get(status, 'secondary')


@register.filter
def amendment_status_color(status):
    colors = {
        'draft': 'secondary',
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def policy_status_color(status):
    colors = {
        'draft': 'secondary',
        'active': 'success',
        'under_review': 'warning',
        'archived': 'dark',
    }
    return colors.get(status, 'secondary')


@register.filter
def incident_severity_color(severity):
    colors = {
        'minor': 'info',
        'moderate': 'warning',
        'major': 'danger',
        'critical': 'dark',
    }
    return colors.get(severity, 'secondary')


@register.filter
def incident_status_color(status):
    colors = {
        'reported': 'info',
        'under_investigation': 'warning',
        'action_taken': 'primary',
        'closed': 'success',
        'dismissed': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def warning_type_color(warning_type):
    colors = {
        'verbal': 'info',
        'written': 'warning',
        'final': 'danger',
        'suspension': 'dark',
        'termination': 'danger',
    }
    return colors.get(warning_type, 'secondary')


@register.filter
def warning_status_color(status):
    colors = {
        'issued': 'info',
        'acknowledged': 'primary',
        'appealed': 'warning',
        'resolved': 'success',
        'expired': 'secondary',
    }
    return colors.get(status, 'secondary')


@register.filter
def appeal_decision_color(decision):
    colors = {
        'pending': 'warning',
        'upheld': 'danger',
        'modified': 'info',
        'overturned': 'success',
    }
    return colors.get(decision, 'secondary')


@register.filter
def grievance_priority_color(priority):
    colors = {
        'low': 'success',
        'medium': 'info',
        'high': 'warning',
        'critical': 'danger',
    }
    return colors.get(priority, 'secondary')


@register.filter
def grievance_status_color(status):
    colors = {
        'registered': 'info',
        'under_investigation': 'warning',
        'hearing': 'primary',
        'resolved': 'success',
        'closed': 'secondary',
        'withdrawn': 'dark',
    }
    return colors.get(status, 'secondary')


@register.filter
def investigation_status_color(status):
    colors = {
        'pending': 'secondary',
        'in_progress': 'warning',
        'completed': 'success',
    }
    return colors.get(status, 'secondary')


@register.filter
def register_status_color(status):
    colors = {
        'draft': 'secondary',
        'final': 'success',
    }
    return colors.get(status, 'secondary')


@register.filter
def inspection_type_color(inspection_type):
    colors = {
        'routine': 'info',
        'surprise': 'warning',
        'complaint_based': 'danger',
        'follow_up': 'primary',
    }
    return colors.get(inspection_type, 'secondary')


@register.filter
def inspection_status_color(status):
    colors = {
        'scheduled': 'info',
        'completed': 'success',
        'follow_up_required': 'warning',
        'closed': 'secondary',
    }
    return colors.get(status, 'secondary')
