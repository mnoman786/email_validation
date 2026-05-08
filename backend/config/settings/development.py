from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ['debug_toolbar']

INTERNAL_IPS = ['127.0.0.1']

# Use console email in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
