from django import template

register = template.Library()


@register.filter
def payroll_status_color(status):
    """Return Bootstrap color class for payroll statuses."""
    colors = {
        'draft': 'secondary',
        'processing': 'info',
        'processed': 'primary',
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'cancelled': 'dark',
        'paid': 'success',
        'held': 'warning',
        'calculated': 'info',
        'active': 'success',
        'inactive': 'secondary',
        'revised': 'info',
        'released': 'primary',
        'applied': 'success',
    }
    return colors.get(status, 'secondary')


@register.filter
def component_type_color(component_type):
    """Return Bootstrap color for earning/deduction."""
    colors = {
        'earning': 'success',
        'deduction': 'danger',
    }
    return colors.get(component_type, 'secondary')


@register.filter
def payment_status_color(status):
    """Return Bootstrap color for payment register status."""
    colors = {
        'pending': 'warning',
        'processed': 'success',
        'failed': 'danger',
        'reconciled': 'primary',
    }
    return colors.get(status, 'secondary')


@register.filter
def reimbursement_status_color(status):
    """Return Bootstrap color for reimbursement status."""
    colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'paid': 'primary',
    }
    return colors.get(status, 'secondary')


@register.filter
def declaration_status_color(status):
    """Return Bootstrap color for investment declaration status."""
    colors = {
        'draft': 'secondary',
        'submitted': 'info',
        'verified': 'success',
        'rejected': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def proof_status_color(status):
    """Return Bootstrap color for investment proof status."""
    colors = {
        'pending': 'warning',
        'verified': 'success',
        'rejected': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def bank_file_status_color(status):
    """Return Bootstrap color for bank file status."""
    colors = {
        'draft': 'secondary',
        'generated': 'info',
        'sent': 'primary',
        'processed': 'success',
        'failed': 'danger',
    }
    return colors.get(status, 'secondary')


@register.filter
def indian_currency(amount):
    """Format amount in Indian numbering system (e.g. 12,34,567.89)."""
    if amount is None:
        return '0.00'
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return '0.00'
    is_negative = amount < 0
    amount = abs(amount)
    parts = f'{amount:.2f}'.split('.')
    integer_part = parts[0]
    if len(integer_part) <= 3:
        result = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        result = ','.join(groups) + ',' + last_three
    formatted = result + '.' + parts[1]
    return f'-{formatted}' if is_negative else formatted
