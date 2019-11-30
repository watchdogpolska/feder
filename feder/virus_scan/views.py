from django.views.generic import View
from django.core.signing import TimestampSigner, BadSignature
from django.core.exceptions import SuspiciousOperation
from .engine import get_engine
from .models import Request
from django.http import JsonResponse

current_engine = get_engine()

signer = TimestampSigner()


class RequestWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            token = signer.unsign(
                value=self.request.GET.get("token", ""), max_age=60 * 24
            )
            if token != current_engine.name:
                raise SuspiciousOperation(
                    "The token does not match the current engine."
                )
        except BadSignature:
            raise SuspiciousOperation("The token signature is invalid.")
        # Ignore payload to process in generic way
        for request in (
            Request.objects.filter(status=Request.STATUS.queued)
            .filter(engine_name=current_engine.name)
            .all()
        ):
            print("Receive result: {}".format(request))
            request.receive_result()
            request.save()
        return JsonResponse({"status": "OK"})
