from dal import autocomplete
from django.utils.translation import gettext_lazy as _
from teryt_tree.dal_ext.filters import CommunityFilter, CountyFilter, VoivodeshipFilter

from feder.main.mixins import DisabledWhenFilterMixin


class DisabledWhenVoivodeshipFilter(DisabledWhenFilterMixin, VoivodeshipFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget", autocomplete.ModelSelect2(url="teryt:voivodeship-autocomplete")
        )
        kwargs.setdefault("disabled_when", ["county", "community"])
        super().__init__(*args, **kwargs)


class DisabledWhenCountyFilter(DisabledWhenFilterMixin, CountyFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget",
            autocomplete.ModelSelect2(
                url="teryt:county-autocomplete", forward=["voivodeship"]
            ),
        )
        kwargs.setdefault("disabled_when", ["community"])
        kwargs.setdefault("label", _("County"))
        super().__init__(*args, **kwargs)


class DisabledWhenCommunityFilter(DisabledWhenFilterMixin, CommunityFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget",
            autocomplete.ModelSelect2(
                url="teryt:community-autocomplete", forward=["county"]
            ),
        )
        kwargs.setdefault("disabled_when", [])
        kwargs.setdefault("label", _("Community"))
        super().__init__(*args, **kwargs)
