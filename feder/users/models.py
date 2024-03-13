from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from guardian.mixins import GuardianUserMixin


class User(GuardianUserMixin, AbstractUser):

    is_content_editor = models.BooleanField(
        default=False,
        verbose_name=_("Content Editor"),
        help_text=_("Whether or not to show user tinycontent editable fields"),
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def can_download_attachment(self):
        from feder.letters.models import Attachment

        content_type = ContentType.objects.get_for_model(Attachment)
        perm = Permission.objects.get(
            content_type=content_type, codename="view_attachment"
        )
        return self.user_permissions.filter(id=perm.id).exists()
