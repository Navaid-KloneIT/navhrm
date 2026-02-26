from django import template

register = template.Library()


@register.simple_tag
def wish_sent(sent_wish_set, employee_id, occasion):
    """Check if a wish has been sent for a given employee and occasion.

    Usage: {% wish_sent sent_wish_set emp.pk 'birthday' as already_wished %}
    """
    return (employee_id, occasion) in sent_wish_set
