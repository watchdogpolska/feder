from django.core.paginator import Paginator, EmptyPage


class ExtraListMixin(object):
    paginate_by = 25
    extra_list_context = 'object_list'

    def paginator(self, object_list):
        paginator = Paginator(object_list, self.paginate_by)
        try:
            return paginator.page(self.kwargs.get('page', 1))
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            return paginator.page(paginator.num_pages)

    @staticmethod
    def get_object_list(obj):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        context = super(ExtraListMixin, self).get_context_data(**kwargs)
        case_list = self.get_object_list(self.object)
        context[self.extra_list_context] = self.paginator(case_list)
        return context
