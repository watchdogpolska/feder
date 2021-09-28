import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from feder.letters.models import Letter
from feder.es_search.tasks import index_letter
from feder.es_search.settings import ELASTICSEARCH_URL

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Letter)
def index_letter_signal(sender, instance, **kwargs):
    if ELASTICSEARCH_URL:
        logger.info("Skipping indexing due Elasticsearch integration disabled")
        return
    index_letter([instance.pk])


@receiver(post_save, sender=Letter)
def update_case_statuses(sender, instance, created, raw, **kwargs):
    if not raw and created and instance.record.case_id:
        case = instance.record.case
        prev_cr = case.confirmation_received
        prev_rr = case.response_received
        case.confirmation_received = case.get_confirmation_received()
        case.response_received = case.get_response_received()
        if prev_cr != case.confirmation_received or prev_rr != case.response_received:
            case.save()
