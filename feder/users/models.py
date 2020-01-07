from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from guardian.mixins import GuardianUserMixin


class User(GuardianUserMixin, AbstractUser):
    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
