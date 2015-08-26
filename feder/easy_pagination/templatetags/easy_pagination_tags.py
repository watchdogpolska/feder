from django import template

register = template.Library()


@register.inclusion_tag('easy_pagination/pager.html', takes_context=True)
def paginator(context, request=None, page=None):
    return {
        'request': request or context['request'],
        'page': page or context['page_obj']
    }
