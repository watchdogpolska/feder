from django.db.models.signals import post_init, post_save
from django.dispatch import receiver
from feder.letters.models import Attachment, Letter
from feder.es_search.tasks import index_letter


@receiver(post_init, sender=Attachment)
def backup_attachment_path(sender, instance, **kwargs):
    instance._current_attachment = instance.attachment


@receiver(post_save, sender=Attachment)
def delete_old_attachment(sender, instance, **kwargs):
    if hasattr(instance, "_current_attachment"):
        if instance._current_attachment != instance.attachment:
            instance._current_attachment.delete(save=False)


@receiver(post_init, sender=Letter)
def backup_eml_path(sender, instance, **kwargs):
    instance._current_eml = instance.eml


@receiver(post_save, sender=Letter)
def delete_old_eml(sender, instance, **kwargs):
    if hasattr(instance, "_current_eml"):
        if instance._current_eml != instance.eml:
            instance._current_eml.delete(save=False)


@receiver(post_save, sender=Letter)
def index_leltter(sender, instance, **kwargs):
    index_letter([instance.pk])
