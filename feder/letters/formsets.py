from feder.main.forms import BaseTableFormSetB3
from extra_views import InlineFormSetFactory

from feder.letters.models import Attachment


class AttachmentInline(InlineFormSetFactory):
    model = Attachment
    formset_class = BaseTableFormSetB3
    fields = ["attachment"]
