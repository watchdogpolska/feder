from django.core.management.base import BaseCommand

from feder.letters.models import Letter


class Command(BaseCommand):
    help = "Update letters attachments text content."

    def handle(self, *args, **options):
        letters_count = Letter.objects.all().count()
        counter = 0
        print("Command options", options)
        print(f"Number of letters to process: {letters_count}")
        for letter in Letter.objects.order_by("pk").iterator(chunk_size=1000):
            counter += 1
            print(f"Processing letter: {letter.pk} - {counter} of {letters_count} ")
            if letter.attachment_set.all().count() == 0:
                print(f"Skipping letter {letter.pk} due to no attachments")
                continue
            for att in letter.attachment_set.all():
                print(
                    f"Updating text content of att.: {att.pk},",
                    f" {att.attachment.name}",
                )
                att.update_text_content()
            print(f"Letter {letter.pk} attachments text updated")
        print(f"Completed attachments text update of {letters_count} letters")
