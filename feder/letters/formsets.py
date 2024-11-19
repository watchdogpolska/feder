from atom.ext.crispy_forms.forms import BaseTableFormSet
from extra_views import InlineFormSetFactory

from feder.letters.models import Attachment


class AttachmentInline(InlineFormSetFactory):
    model = Attachment
    formset_class = BaseTableFormSet
    fields = ["attachment"]
