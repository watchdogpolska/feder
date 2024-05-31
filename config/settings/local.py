"""
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .common import *  # noqa

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]
# END SITE CONFIGURATION

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="CHANGEME!!!")

# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
if "test" not in sys.argv:
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    INSTALLED_APPS += ("debug_toolbar",)
    ROSETTA_EXCLUDED_APPLICATIONS += ("debug_toolbar",)
    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
        "SHOW_TEMPLATE_CONTEXT": True,
        "SHOW_TOOLBAR_CALLBACK": lambda x: "test" not in sys.argv,
    }
MY_INTERNAL_IP = env("MY_INTERNAL_IP", default="")
INTERNAL_IPS = ("127.0.0.1", "10.0.2.2", MY_INTERNAL_IP)

# django-extensions
# ------------------------------------------------------------------------------

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Your local stuff: Below this line define 3rd party library settings
# To get all sql queries sent by Django from py shell
EMAILLABS_APP_KEY = env("EMAILLABS_APP_KEY", default="Dummy")

EMAILLABS_SECRET_KEY = env("EMAILLABS_SECRET_KEY", default="Dummy")

LETTER_RECEIVE_SECRET = env("LETTER_RECEIVE_SECRET", default="my-strong-secret")

# Media folder defined in env to allow debugging with different data sets
MEDIA_ROOT_ENV = env("MEDIA_ROOT_ENV", default="media_dev")
MEDIA_ROOT = str(APPS_DIR(MEDIA_ROOT_ENV))
SENDFILE_ROOT = MEDIA_ROOT
