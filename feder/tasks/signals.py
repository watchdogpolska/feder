from django.db.models.signals import post_save
from django.dispatch import receiver

from feder.light_user.models import LightUser
from feder.tasks.models import Survey


@receiver(post_save, sender=LightUser, dispatch_uid='survey_update_when_light_user_changed')
def survey_update_when_light_user_changed(sender, instance, **kwargs):
    if instance.user:
        Survey.objects.filter(light_user=instance).update(user=instance.user)
