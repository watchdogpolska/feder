from extra_views import InlineFormSetFactory

from feder.letters.models import Attachment
from feder.main.forms import BaseTableFormSetB3


class AttachmentInline(InlineFormSetFactory):
    model = Attachment
    formset_class = BaseTableFormSetB3
    fields = ["attachment"]
