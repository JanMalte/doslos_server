from __future__ import absolute_import
from .settings import *

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.locmem'
# END EMAIL CONFIGURATION


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# END DEBUG CONFIGURATION


# IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}
# END IN-MEMORY TEST DATABASE


# Throw errors when using invalid args for G/N
DDF_VALIDATE_ARGS = True
DDF_FILL_NULLABLE_FIELDS = False


# Disable migrations when running tests
class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()
