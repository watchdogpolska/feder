from .models import Letter


class LetterObjectFeedMixin:
    """A mixins to view (feed) to provide easy way to generate
    feed of letters related to selected object

    Attributes:
        filter_field (str): path to related object to Letter
        kwargs_name (str): name used in urlpatterns
        model (model): model used to select object related to Letter
    """

    model = None
    filter_field = None
    kwargs_name = None

    def get_object(self, request, **kwargs):
        return self.model.objects.get(pk=kwargs.get(self.kwargs_name))

    def link(self, obj):
        return obj.get_absolute_url()

    def get_items(self, obj):
        return (
            Letter.objects.with_feed_items()
            .filter(**{self.filter_field: obj})
            .order_by("-created")[:30]
        )
