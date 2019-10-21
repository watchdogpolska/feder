from feder.letters.models import Letter
from feder.records.registry import record_type_registry
from feder.records.types import BaseRecordType
from django.utils.translation import ugettext_lazy as _


class LetterRecordType(BaseRecordType):
    def get_verbose_name(self, obj):
        if obj.is_draft:
            return _("Draft letter")
        if obj.is_spam:
            return _("Letter-spam")
        if obj.is_incoming:
            return _("Incoming letter")
        return _("Outgoing letter")

    def get_verbose_name_plural(self, obj):
        if obj.is_draft:
            return _("Draft letters")
        if obj.is_spam:
            return _("Letters-spam")
        if obj.is_incoming:
            return _("Incoming letters")
        return _("Outgoing letters")

    def get_template_milestone_item(self, obj=None):
        return "letters/letter_milestone_item.html"

    def get_template_content_item(self, obj=None):
        return "letters/_letter_content_item.html"


record_type_registry.registry(Letter, LetterRecordType())
