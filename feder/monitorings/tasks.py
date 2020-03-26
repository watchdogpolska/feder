from background_task import background
from ..cases.models import Case
from ..letters.models import Letter


@background
def handle_mass_assign(mass_assign):
    for case in Case.objects.filter(mass_assign=mass_assign).all():
        case.update_email()
        case.save()
    send_letter_for_mass_assign(mass_assign)

@background
def send_letter_for_mass_assign(mass_assign):
    for case in Case.objects.filter(mass_assign=mass_assign).all():
        Letter.send_new_case(case=case)