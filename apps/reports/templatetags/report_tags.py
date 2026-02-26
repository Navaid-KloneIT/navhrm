from django import template

register = template.Library()


@register.filter
def percentage(value, decimals=1):
    """Format a number as a percentage string."""
    if value is None:
        return '0.0%'
    try:
        value = float(value)
    except (ValueError, TypeError):
        return '0.0%'
    return f'{value:.{int(decimals)}f}%'


@register.filter
def indian_number(amount):
    """Format number in Indian numbering system (e.g. 12,34,567)."""
    if amount is None:
        return '0'
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return '0'
    is_negative = amount < 0
    amount = abs(amount)
    if amount == int(amount):
        integer_part = str(int(amount))
        decimal_part = None
    else:
        parts = f'{amount:.2f}'.split('.')
        integer_part = parts[0]
        decimal_part = parts[1]
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
    if decimal_part:
        result = result + '.' + decimal_part
    return f'-{result}' if is_negative else result


@register.filter
def trend_icon(value):
    """Return an up/down/neutral trend arrow icon class based on value."""
    if value is None:
        return 'ri-subtract-line text-muted'
    try:
        value = float(value)
    except (ValueError, TypeError):
        return 'ri-subtract-line text-muted'
    if value > 0:
        return 'ri-arrow-up-line text-success'
    elif value < 0:
        return 'ri-arrow-down-line text-danger'
    return 'ri-subtract-line text-muted'


@register.filter
def abs_value(value):
    """Return absolute value."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0
