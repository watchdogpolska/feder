from django.conf import settings
from .virustotal import VirusTotalEngine
from .attachmentscanner import AttachmentScannerEngine
from .metadefender import MetaDefenderEngine


def is_available():
    try:
        get_engine()
        return True
    except:
        return False


def get_engine():
    if settings.METADEFENDER_API_KEY:
        return MetaDefenderEngine()
    if settings.ATTACHMENTSCANNER_API_KEY:
        return AttachmentScannerEngine()
    if settings.VIRUSTOTAL_API_KEY:
        return VirusTotalEngine()
    raise Exception("Not found available virus_scan engine")
