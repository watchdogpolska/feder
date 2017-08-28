from functools import partial

from django.core import signing
from django.core.signing import Signer
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from feder.light_user.models import LightUser

COOKIE_NAME = 'light_user_id'

signer = Signer("LightUserMiddleware")


def new_user(request):
    user = request.user if request.user.is_authenticated() else None
    lu = LightUser.objects.create(user=user,
                                  ip=request.META.get('REMOTE_ADDR'))
    request._light_user_set_id = lu.id
    request._cached_light_user = lu
    return lu


def get_light_user_or_none(request):
    """
    Get Light User (if exists already) for request

    :param request:
    :return: LightUser instance
    """
    if hasattr(request, '_cached_light_user'):
        return request._cached_light_user
    if 'light_user_id' not in request.COOKIES:
        return None

    try:
        lu_id = signer.unsign(request.COOKIES[COOKIE_NAME])
        request._cached_light_user = LightUser.objects.get(pk=lu_id)
        return request._cached_light_user
    except LightUser.DoesNotExist:
        request._light_user_reset = True
    except signing.BadSignature:
        request._light_user_reset = True
    return None


def get_light_user(request):
    """
    Get Light User (or create if not exists yet) for request

    :param request:
    :return: LightUser instance
    """
    if hasattr(request, '_cached_light_user'):
        return request._cached_light_user
    if COOKIE_NAME not in request.COOKIES:
        new_user(request)
        return request._cached_light_user
    try:
        lu_id = signer.unsign(request.COOKIES[COOKIE_NAME])
        request._cached_light_user = LightUser.objects.get(pk=lu_id)
    except LightUser.DoesNotExist:
        new_user(request)
    except signing.BadSignature:
        new_user(request)
    return request._cached_light_user


class LightUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.light_user = SimpleLazyObject(lambda: get_light_user_or_none(request))
        request.light_user_new = SimpleLazyObject(lambda: get_light_user(request))

    def process_response(self, request, response):
        if hasattr(request, '_light_user_reset'):
            response.delete_cookie(COOKIE_NAME)
        if hasattr(request, '_light_user_set_id'):
            response.set_cookie(COOKIE_NAME, signer.sign(request._light_user_set_id))
        return response
