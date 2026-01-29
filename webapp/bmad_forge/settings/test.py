"""
Test settings for BMAD Forge.

These settings are optimized for running tests:
- Fast in-memory SQLite database
- Minimal logging
- No external services
- Password hashing speedup
"""

from .base import *

# DEBUG can be True for tests to see detailed error pages
DEBUG = True

# Allowed hosts not critical for tests
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Database - In-memory SQLite for fast tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Password hashing - Use fast (insecure) hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Caching - Dummy cache (no caching) for predictable tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email - Store emails in memory for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Minimal logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'forge': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Disable migrations for faster tests (optional)
# Uncomment if you want to use --nomigrations flag behavior by default
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

# GitHub settings - use mock values for tests
GITHUB_TOKEN = 'test-token'
GITHUB_RAW_BASE_URL = 'https://raw.githubusercontent.com'
BMAD_METHOD_REPO = 'test/repo'
TEMPLATE_REPO = 'test/templates'
