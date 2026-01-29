"""
Development settings for BMAD Forge.

These settings are optimized for local development:
- DEBUG enabled
- SQLite database
- Detailed logging
- Permissive security settings
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development logging - more verbose
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['forge']['level'] = 'DEBUG'

# Disable template caching for development
for template in TEMPLATES:
    template['OPTIONS']['debug'] = True

# Email backend - console for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache - dummy cache for development (no caching)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Development-specific settings
INTERNAL_IPS = ['127.0.0.1', 'localhost']
