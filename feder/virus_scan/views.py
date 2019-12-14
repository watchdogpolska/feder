from django.views.generic import View
from django.core.exceptions import SuspiciousOperation
from .models import Request
from django.http import JsonResponse
from .signer import TokenSigner


class RequestWebhookView(View):
    signer = TokenSigner()

    def post(self, request, *args, **kwargs):
        from .engine import get_engine

        current_engine = get_engine()
        token = self.signer.sign(self.request.GET.get("token", ""))
        if token != current_engine.name:
            raise SuspiciousOperation("The token does not match the current engine.")
        for request in (
            Request.objects.filter(status=Request.STATUS.queued)
            .filter(engine_name=current_engine.name)
            .all()
        ):
            print("Receive result: {}".format(request))
            request.receive_result()
            request.save()
        return JsonResponse({"status": "OK"})
