from atom.ext.crispy_forms.forms import BaseTableFormSet
from extra_views import InlineFormSet

from feder.letters.models import Attachment


class AttachmentInline(InlineFormSet):
    model = Attachment
    formset_class = BaseTableFormSet
    fields = ['attachment', ]
