from background_task import background

from .serializers import letter_serialize


@background
def index_letter(letter_pks):
    from ..letters.models import Letter

    for letter in Letter.objects.filter(pk__in=letter_pks).all():
        doc = letter_serialize(letter)
        doc.save()
