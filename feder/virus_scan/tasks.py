from background_task import background
from .models import Request


@background
def scan_request(pk):
    request = Request.objects.get(pk=pk)
    request.receive_result()
    request.save()
