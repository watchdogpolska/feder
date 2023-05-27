from django.conf import settings
from django.utils.timezone import now
from django_filters import DateRangeFilter, FilterSet


class InitialFilterSet(FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        initial = kwargs.pop("initial", {})
        if data is None:
            data = {}
        data = dict(list(initial.items()) + list(data.copy().items()))
        super().__init__(data, *args, **kwargs)


class MinYearRangeFilter(DateRangeFilter):
    def __init__(self, choices=None, filters=None, *args, **kwargs):
        years = range(now().year, settings.MIN_FILTER_YEAR - 1, -1)
        if choices is None:
            choices = DateRangeFilter.choices + [(str(year), year) for year in years]
        if filters is None:
            filters = dict(DateRangeFilter.filters)
            for year in years:
                filters[str(year)] = lambda qs, name: qs.filter(
                    **{
                        "%s__year" % name: now().year,
                    }
                )
        super().__init__(choices=choices, filters=filters, *args, **kwargs)
