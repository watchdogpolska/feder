from django.conf import settings

from .attachmentscanner import AttachmentScannerEngine
from .metadefender import MetaDefenderEngine
from .virustotal import VirusTotalEngine


class NotFoundEngineException(Exception):
    pass


def is_available():
    try:
        get_engine()
        return True
    except NotFoundEngineException:
        return False


def get_engine():
    if settings.METADEFENDER_API_KEY:
        return MetaDefenderEngine()
    if settings.ATTACHMENTSCANNER_API_KEY:
        return AttachmentScannerEngine()
    if settings.VIRUSTOTAL_API_KEY:
        return VirusTotalEngine()
    raise NotFoundEngineException("Not found available virus_scan engine")
