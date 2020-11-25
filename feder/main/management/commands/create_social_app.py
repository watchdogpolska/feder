from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management import CommandError, BaseCommand

from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = "Create an initial Facebook SocialApp to fix an ImproperlyConfigured error"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                """
                This command can only be used in DEBUG mode.
                For production setup, use django admin.
                """
            )
        else:
            site = Site.objects.get(id=settings.SITE_ID)
            sa = SocialApp.objects.create(
                provider="Facebook",
                name="FB",
                client_id="FAKE",
                secret="FAKE",
                key="FAKE",
            )
            sa.sites.add(site)
