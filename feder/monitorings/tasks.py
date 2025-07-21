from background_task import background
from django.db import transaction

from feder.cases.models import Case
from feder.letters.logs.tasks import update_sent_letter_status
from feder.letters.models import Letter


@background
def handle_mass_assign(mass_assign):
    for case in Case.objects.filter(mass_assign=mass_assign).all():
        case.update_email()
    send_letter_for_mass_assign(mass_assign)
    update_sent_letter_status(schedule=(15 * 60))
    return f"Mass assign {mass_assign} handled."


@background
def send_letter_for_mass_assign(mass_assign):
    for case in Case.objects.filter(mass_assign=mass_assign).all():
        Letter.send_new_case(case=case)
    return f"Letters for mass assign {mass_assign} sent."


@background
def send_mass_draft(mass_draft_pk):
    """
    Generates letters from mass draft object, sends them and then deletes the draft.
    """
    if not Letter.objects.filter(pk=mass_draft_pk).exists():
        return f"Mass draft with pk={mass_draft_pk} not found."
    with transaction.atomic():
        mass_draft = Letter.objects.get(pk=mass_draft_pk)
        letters = mass_draft.generate_mass_letters()
        for letter in letters:
            letter.send()
        mass_draft.delete()
    update_sent_letter_status(schedule=(15 * 60))
    return f"Mass draft {mass_draft_pk} sent."
