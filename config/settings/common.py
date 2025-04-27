"""
Django settings for feder project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os
import sys

import environ
from django.utils.translation import gettext_lazy as _

ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path("feder")

env = environ.Env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    # Default Django apps:
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Useful template tags:
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    # Admin
    "django.contrib.admin",
)
THIRD_PARTY_APPS = (
    "crispy_forms",  # Form layouts
    "allauth",  # registration
    "allauth.account",  # registration
    "allauth.socialaccount",  # registration
    "dal",
    "dal_select2",
    "tinycontent",
    "django_extensions",
    "tinymce",
    "ajax_datatable",
    "formtools",
    "mptt",
    "atom",
    "guardian",
    "teryt_tree",
    "bootstrap_pagination",
    "rest_framework",
    "reversion",
    "django_filters",
    "background_task",
    "corsheaders",
    "rosetta",
)

# Local apps which should be put before any other apps
# allowing for example to override third party app's templates.
PRIORITY_LOCAL_APPS = ("feder.main",)

# Apps specific for this project go here.
LOCAL_APPS = (
    "feder.teryt",
    "feder.users",
    "feder.institutions",
    "feder.monitorings",
    "feder.cases",
    "feder.cases_tags",
    "feder.letters",
    "feder.alerts",
    "feder.letters.logs",
    "feder.domains",
    "feder.records.apps.RecordsConfig",
    "feder.parcels.apps.ParcelsConfig",
    "feder.virus_scan",
    "feder.organisations",
    "feder.llm_evaluation",
    # Your stuff: custom apps go here
)

ALLAUTH_PROVIDERS_APPS = ("allauth.socialaccount.providers.google",)
# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = (
    PRIORITY_LOCAL_APPS
    + DJANGO_APPS
    + THIRD_PARTY_APPS
    + ALLAUTH_PROVIDERS_APPS
    + LOCAL_APPS
    + ("django_cleanup.apps.CleanupConfig",)  # should be placed after all other apps
)

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    # Make sure djangosecure.middleware.SecurityMiddleware is listed first
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "reversion.middleware.RevisionMiddleware",
    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {"sites": "feder.contrib.sites.migrations"}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env.str(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = env.str("DJANGO_EMAIL_HOST", default="")
EMAIL_HOST_PASSWORD = env.str("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_HOST_USER = env.str("DJANGO_EMAIL_HOST_USER", "")
EMAIL_PORT = env.str("DJANGO_EMAIL_PORT", default=25)

DEFAULT_FROM_EMAIL = env.str(
    "DJANGO_DEFAULT_FROM_EMAIL", default="feder <noreply@dane.siecobywatelska.pl>"
)
EMAIL_SUBJECT_PREFIX = env.str("DJANGO_EMAIL_SUBJECT_PREFIX", default="[feder] ")
EMAIL_USE_TLS = env.bool("DJANGO_EMAIL_USE_TLS", True)
SERVER_EMAIL = env.str(
    "DJANGO_SERVER_EMAIL", default="feder <<noreply@dane.siecobywatelska.pl>"
)
# END EMAIL CONFIGURATION
# ------------------------------------------------------------------------------

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins

from ast import literal_eval as make_tuple

ADMINS = make_tuple(env("DJANGO_ADMINS", default="()"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    "default": env.db("DATABASE_URL", default="mysql:///feder"),
    "OPTIONS": {
        "charset": "utf8mb4",
        "init_command": "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_polish_ci'",
    },
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "Europe/Warsaw"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "pl"
LANGUAGES = (("pl", _("Polish")), ("en", _("English")))
LOCALE_PATHS = (str(APPS_DIR.path("main/locale")),)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# Default format for datetime.strftime.method
STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"
STRFTIME_DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "Y-m-d H:i:s"
DATE_FORMAT = "Y-m-d"

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "OPTIONS": {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # Your stuff: custom template context processors go here
            ],
        },
    }
]

# See: http://django-crispy-forms.readthedocs.org/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap3"

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (str(APPS_DIR.path("static")),)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = "feder.main.urls"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# NoSignupAdapter disables the signup functionality - new users to be
# manually added by admins
ACCOUNT_ADAPTER = "feder.main.adapters.NoSignupAdapter"
SOCIALACCOUNT_EMAIL_VERIFICATION = "optional"
SOCIALACCOUNT_PROVIDERS = {
    "github": {"SCOPE": ["user"]},
    "gilab": {"SCOPE": ["read_user", "openid"]},
}
# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "users:redirect"
LOGIN_URL = "account_login"
MIN_FILTER_YEAR = 2016

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = "feder.main.slugifier.ascii_slugify"

# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
#
# TODO add proper file logging configuration when loggers added to code
#   as for now all stdout and stderr captured by gunicorn logs
LOG_FILE_ENV = env("LOG_FILE_ENV", default="logs/feder.log")
LOG_FILE = str(ROOT_DIR(LOG_FILE_ENV))
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "app",
        },
        "file": {
            # "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "app",
        },
    },
    "loggers": {
        # "django.request": {"handlers": [], "level": "ERROR", "propagate": True},
        "": {"handlers": ["file", "console"], "level": "INFO", "propagate": True},
        "feder.letters.models": {
            "handlers": ["console"] if "test" not in environ.sys.argv else [],
            "level": "INFO",
        },
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)-7s] "
                # "(%(module)s.%(funcName)s) %(message)s"
                "(%(pathname)s:%(lineno)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

# Your common stuff: Below this line define 3rd party library settings
ANONYMOUS_USER_ID = -1
GUARDIAN_RAISE_403 = True

CASE_EMAIL_TEMPLATE = env("CASE_EMAIL_TEMPLATE", default="sprawa-{pk}@{domain}")

DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE = True
DJANGO_MAILBOX_COMPRESS_ORIGINAL_MESSAGE = True

FILTERS_HELP_TEXT_FILTER = False

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "feder.main.paginator.DefaultPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

EMAIL_NOTIFICATION = env(
    "DJANGO_EMAIL_NOTIFICATION", default="no-reply@siecobywatelska.pl"
)

EMAILLABS_APP_KEY = env("EMAILLABS_APP_KEY", default="Dummy")

EMAILLABS_SECRET_KEY = env("EMAILLABS_SECRET_KEY", default="Dummy")

INSTALLED_APPS += ("github_revision",)
GITHUB_REVISION_REPO_URL = "https://github.com/watchdogpolska/feder"
SENDFILE_BACKEND = "django_sendfile.backends.development"
SENDFILE_ROOT = MEDIA_ROOT

DATA_UPLOAD_MAX_MEMORY_SIZE = 200000000  # 200MB

NECESSARY_FILES = {
    "letters.Letter": {"path": "record__case__monitoring", "fields": ["eml"]},
    "letters.Attachment": {
        "path": "letter__record__case__monitoring",
        "fields": ["attachment"],
    },
    "parcels.IncomingParcelPost": {
        "path": "record__case__monitoring",
        "fields": ["content"],
    },
    "parcels.OutgoingParcelPost": {
        "path": "record__case__monitoring",
        "fields": ["content"],
    },
}

VIRUSTOTAL_API_KEY = env("VIRUSTOTAL_API_KEY", default=None)
ATTACHMENTSCANNER_API_KEY = env("ATTACHMENTSCANNER_API_KEY", default=None)
ATTACHMENTSCANNER_API_URL = env(
    "ATTACHMENTSCANNER_API_URL", default="https://beta-eu.attachmentscanner.com"
)
METADEFENDER_API_KEY = env("METADEFENDER_API_KEY", default=None)
METADEFENDER_API_URL = env(
    "METADEFENDER_API_URL", default="https://api.metadefender.com"
)

CORS_ALLOWED_ORIGINS = [
    "https://sprawdzamyjakjest.pl",
    "https://demo.sprawdzamyjakjest.pl",
    "https://sjj.127.0.0.1.nip.io",
]
CORS_URLS_REGEX = r"^/api/.*$"

FILE_TO_TEXT_URL = env("FILE_TO_TEXT_URL", default="http://localhost:9980/")
FILE_TO_TEXT_TOKEN = env("FILE_TO_TEXT_TOKEN", default="")

# To avoid unwanted migrations when upgrading to Django 3.2
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# APP_MODE used to differentiate dev, demo and production environments
# use DEV, DEMO and PROD values in env variable APP_MODE
APP_MODE = env.str("APP_MODE", "DEMO")

ROSETTA_SHOW_AT_ADMIN_PANEL = True

# Rosetta translation settings
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True
ROSETTA_EXCLUDED_APPLICATIONS = (
    "django.contrib.admin",  # for some reason does not exclue admin app
    "django.contrib.auth",
    "crispy_forms",  # Form layouts
    "allauth",  # registration
    "allauth.account",  # registration
    "allauth.socialaccount",  # registration
    "dal",
    "dal_select2",
    "tinymce",
    "ajax_datatable",
    "formtools",
    "mptt",
    "atom",
    "guardian",
    "teryt_tree",
    "bootstrap_pagination",
    "rest_framework",
    "reversion",
    "django_filters",
    "background_task",
    "corsheaders",
    "rosetta",
)
AZURE_CLIENT_SECRET = env.str("ROSETTA_AZURE_CLIENT_SECRET", "")

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    # "height": 500,
    "menubar": True,
    "lineheight": 1,
    "plugins": "autolink,lists,link,image,charmap,print,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,"
    "code,help,wordcount",
    "toolbar": "undo redo | formatselect | lineheight | fontsizeselect |"
    "bold italic backcolor | alignleft aligncenter "
    "alignright alignjustify | bullist numlist outdent indent | "
    "charmap | removeformat | help",
}

BLEACH_ALLOWED_TAGS = {
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "strong",
    "em",
    "p",
    "ul",
    "ol",
    "i",
    "li",
    "br",
    "sub",
    "sup",
    "hr",
    "pre",
    "img",
}

BLEACH_ALLOWED_ATTRIBUTES = ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "abbr": ["title"],
    "acronym": ["title"],
    "img": ["alt", "src", "title"],
}

OPENAI_API_KEY = env.str("OPENAI_API_KEY", "")
OPENAI_API_VERSION = env.str("OPENAI_API_VERSION", "")
OPENAI_API_TYPE = env.str("OPENAI_API_TYPE", "")
AZURE_ENDPOINT = env.str("AZURE_ENDPOINT", "")
OPENAI_API_ENGINE_35 = env.str("OPENAI_API_ENGINE_35", "")
OPENAI_API_ENGINE_35_MAX_TOKENS = env.int("OPENAI_API_ENGINE_35_MAX_TOKENS", 4096)
OPENAI_API_ENGINE_35_MAX_COMPLETION_TOKENS = env.int(
    "OPENAI_API_ENGINE_35_MAX_COMPLETION_TOKENS", 1024
)
OPENAI_API_ENGINE_4 = env.str("OPENAI_API_ENGINE_4", "")
OPENAI_API_ENGINE_4_MAX_TOKENS = env.int("OPENAI_API_ENGINE_4_MAX_TOKENS", 8000)
OPENAI_API_ENGINE_4_MAX_COMPLETION_TOKENS = env.int(
    "OPENAI_API_ENGINE_4_MAX_COMPLETION_TOKENS", 1024
)
LETTER_CATEGORIZATION_MAX_TOKENS = env.int("LETTER_CATEGORIZATION_MAX_TOKENS", 6000)
LETTER_NORMALIZATION_MAX_TOKENS = env.int("LETTER_NORMALIZATION_MAX_TOKENS", 100000)
ANSWERS_CATEGORIZATION_MAX_TOKENS = env.int("ANSWERS_CATEGORIZATION_MAX_TOKENS", 100000)
MONITORING_NORMALIZATION_MAX_TOKENS = env.int(
    "MONITORING_NORMALIZATION_MAX_TOKENS", 100000
)
OPENAI_API_TEMPERATURE = env.float("OPENAI_API_TEMPERATURE", 0.0)
