import json
import logging

from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.views.generic import View

from .models import Request
from .signer import TokenSigner

logger = logging.getLogger(__name__)


class RequestWebhookView(View):
    signer = TokenSigner()

    def post(self, request, *args, **kwargs):
        from .engine import get_engine

        current_engine = get_engine()
        token_engine = self.signer.unsign(self.request.GET.get("token", ""))
        if token_engine != current_engine.name:
            raise SuspiciousOperation("Token does not match the current engine.")
        headers = dict(request.headers)
        logger.info(f"Received webhook from {current_engine.name}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Body: {request.body.decode('utf-8')}")
        try:
            result = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            logger.error("Invalid JSON body")
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        if not result.get("data_id"):
            logger.error("Missing data_id in the request")
            return JsonResponse({"error": "Missing data_id"}, status=400)
        request = Request.objects.filter(
            engine_id=result["data_id"], engine_name=current_engine.name
        ).first()
        if not request:
            logger.error(f"Request not found: {result["data_id"]}")
            return JsonResponse({"error": "Request not found"}, status=404)
        result["response_headers"] = headers
        request_update = {
            "engine_id": result["data_id"],
            "status": current_engine.map_status(result),
            "engine_report": result,
            "engine_link": current_engine.get_result_url(
                result["data_id"] if result["data_id"] is not None else None,
            ),
        }
        for key in request_update:
            setattr(request, key, request_update[key])
        request.save()
        logger.info(f"Request updated: {request}")
        return JsonResponse({"status": "OK"})
