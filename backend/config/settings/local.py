"""
Local development settings for Windows — no Docker, no Redis, no PostgreSQL required.
Uses SQLite + in-memory cache + synchronous task execution.
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite instead of PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use in-memory cache instead of Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'emailguard-local',
    }
}

# Use DB sessions (not cache-based) since we have no Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Run Celery tasks synchronously (no worker needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Override Celery result backend to avoid DB tables issue in eager mode
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'default'

# Relaxed security for local dev
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Faster passwords in dev
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Longer JWT lifetime for local dev convenience
from datetime import timedelta
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(days=7)
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=30)

# Use local filesystem for media
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# No Sentry in local dev
SENTRY_DSN = ''

# Stripe test keys (set your own in .env.local)
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='pk_test_placeholder')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_placeholder')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

FRONTEND_URL = 'http://localhost:3000'

# Simple console-only logging for local dev (no file handler needed)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'apps': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}

print("[OK] Running with LOCAL settings (SQLite, no Redis, sync Celery)")
