from django.core.management.base import BaseCommand
from feder.virus_scan.models import Request

from feder.virus_scan.engine import get_engine

current_engine = get_engine()


class Command(BaseCommand):
    help = "Commands to send request to scan files & receive results"

    def add_arguments(self, parser):
        parser.add_argument("--skip-send", action="store_true")
        parser.add_argument("--skip-receive", action="store_true")

    def send_scan(self):
        for request in Request.objects.filter(status=Request.STATUS.created).all():
            self.stdout.write("Send to scan: {}".format(request))
            request.send_scan()
            request.save()

    def receive_result(self):
        for request in (
            Request.objects.filter(status=Request.STATUS.queued)
            .filter(engine_name=current_engine.name)
            .all()
        ):
            self.stdout.write("Receive result: {}".format(request))
            request.receive_result()
            request.save()

    def handle(self, *args, **options):
        if not options["skip_send"]:
            self.stdout.write("Sending requests to scan")
            self.send_scan()
        if not options["skip_receive"]:
            self.stdout.write("Fetching results of requests of scan")
            self.receive_result()
