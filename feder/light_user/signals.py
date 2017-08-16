from django.contrib.auth import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def associate_light_user_to_user(request, user, **kwargs):
    if getattr(request, 'light_user', None) and request.light_user.user is None:
        request.light_user.user = user
        request.light_user.save(update_fields=['user'])
