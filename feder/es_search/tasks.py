from background_task import background
from .queries import delete_document
from .serializers import letter_serialize


@background
def index_letter(letter_pks):
    from ..letters.models import Letter

    for letter in Letter.objects.filter(pk__in=letter_pks).all():
        delete_document(letter.pk)
        doc = letter_serialize(letter)
        assert doc.save() == "created"
