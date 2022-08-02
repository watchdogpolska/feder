from background_task import background
from django.db import transaction

from feder.cases.models import Case
from feder.letters.models import Letter


@background
def handle_mass_assign(mass_assign):
    for case in Case.objects.filter(mass_assign=mass_assign).all():
        case.update_email()
        case.update_is_quarantined()
        case.save()
    send_letter_for_mass_assign(mass_assign)


@background
def send_letter_for_mass_assign(mass_assign):
    for case in Case.objects.filter(mass_assign=mass_assign).all():
        Letter.send_new_case(case=case)


@background
def send_mass_draft(mass_draft_pk):
    """
    Generates letters from mass draft object, sends them and then deletes the draft.
    """
    with transaction.atomic():
        mass_draft = Letter.objects.get(pk=mass_draft_pk)
        letters = mass_draft.generate_mass_letters()
        for letter in letters:
            letter.send()
        mass_draft.delete()
