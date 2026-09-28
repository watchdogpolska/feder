from django import template

register = template.Library()


@register.simple_tag
def elided_page_range(paginator, number, on_each_side=2, on_ends=1):
    """Wraps Paginator.get_elided_page_range so it can be called from a template
    (its arguments prevent a direct `paginator.get_elided_page_range` lookup)."""
    return paginator.get_elided_page_range(
        number, on_each_side=on_each_side, on_ends=on_ends
    )
