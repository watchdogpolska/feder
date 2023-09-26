from django.core.management.base import BaseCommand

from feder.letters.models import Letter


class Command(BaseCommand):
    help = "Mark duplicated letters as spam based on 'Message-ID'."

    def add_arguments(self, parser):
        parser.add_argument(
            "--monitoring-pk", help="PK of monitoring to evaluate", required=True
        )

    def handle(self, *args, **options):
        monitoring_resp_letters = (
            Letter.objects.filter(record__case__monitoring__id=options["monitoring_pk"])
            .is_incoming()
            .exclude_spam()
            .exclude_automatic()
            .order_by("pk")
        )
        print("Command options", options)
        print("Number of letters to evaluate", monitoring_resp_letters.count())
        for letter in monitoring_resp_letters:
            print(f"Processing letter: {letter.pk}, ")
            if letter.ai_evaluation is None:
                for att in letter.attachment_set.all():
                    print(
                        f"Updating text content of att.: {att.pk},",
                        f" {att.attachment.name}",
                    )
                    att.update_text_content()
                print(f"Evaluating letter: {letter.pk}")
                letter.evaluate_letter_content_with_ai()
                print(f"Letter {letter.pk} evaluated with AI: {letter.ai_evaluation}")
            else:
                print(
                    f"Skipping letter {letter.pk} due to existing evaluation: "
                    + f"{letter.ai_evaluation}"
                )
        print(
            f"Completed evaluation of {monitoring_resp_letters.count()} letters for "
            + f"monitoring {options['monitoring_pk']}"
        )
