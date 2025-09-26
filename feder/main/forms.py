from django.forms.models import BaseInlineFormSet
from crispy_forms.helper import FormHelper


class BaseTableFormSetB3(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        h = FormHelper()
        h.template_pack = "bootstrap3"
        h.template = "bootstrap3/table_inline_formset.html"
        h.form_tag = False  # outer <form> is in the page template
        self.helper = h
