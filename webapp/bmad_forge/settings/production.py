"""
Production settings for BMAD Forge.

These settings are optimized for production deployment:
- DEBUG disabled
- PostgreSQL database with connection pooling
- Security headers (HSTS, CSP, XSS protection)
- WhiteNoise for static file serving
- Sentry error tracking
- Production logging
- Redis caching (optional)
"""

import os
from .base import *

# SECURITY WARNING: DEBUG must be False in production!
DEBUG = False

# ALLOWED_HOSTS must be explicitly configured in production
_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]

# Database - PostgreSQL for production
# Supports DATABASE_URL format or individual components
if 'DATABASE_URL' in os.environ:
    # Parse DATABASE_URL (postgres://user:pass@host:port/dbname)
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=os.environ['DATABASE_URL'],
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ImportError:
        # Fallback if dj_database_url not installed
        # Parse DATABASE_URL manually
        import re
        db_url = os.environ['DATABASE_URL']
        # Simple regex parse: postgresql://user:pass@host:port/dbname
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
        if match:
            user, password, host, port, dbname = match.groups()
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': dbname,
                    'USER': user,
                    'PASSWORD': password,
                    'HOST': host,
                    'PORT': port,
                    'CONN_MAX_AGE': 600,
                    'OPTIONS': {'connect_timeout': 10}
                }
            }
        else:
            raise ValueError("Invalid DATABASE_URL format")
else:
    # Use individual environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'bmad_forge_prod'),
            'USER': os.environ.get('DB_USER', 'bmad_admin'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,  # Connection pooling (10 minutes)
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }

# Security settings

# SSL/TLS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# HSTS (HTTP Strict Transport Security)
# Start with a short duration (e.g., 300) and increase gradually
# Use 31536000 (1 year) once confident
SECURE_HSTS_SECONDS = int(os.environ.get('HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Browser security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files - WhiteNoise configuration
MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Content Security Policy
# Install: pip install django-csp
try:
    import csp
    MIDDLEWARE.append('csp.middleware.CSPMiddleware')

    CSP_DEFAULT_SRC = ("'self'",)
    # WARNING: 'unsafe-inline' weakens CSP protection against XSS attacks
    # TODO: Remove 'unsafe-inline' and use nonces or hashes for inline scripts/styles
    # For now, unsafe-inline is enabled for compatibility with existing templates
    # Before removing, audit all inline scripts/styles in templates
    CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
    CSP_IMG_SRC = ("'self'", "data:", "https:")
    CSP_FONT_SRC = ("'self'",)
    CSP_CONNECT_SRC = ("'self'",)
    CSP_FRAME_ANCESTORS = ("'none'",)
    CSP_BASE_URI = ("'self'",)
    CSP_FORM_ACTION = ("'self'",)
except ImportError:
    pass

# Permissions Policy
# Install: pip install django-permissions-policy
try:
    import django_permissions_policy
    MIDDLEWARE.append('django_permissions_policy.PermissionsPolicyMiddleware')

    PERMISSIONS_POLICY = {
        'geolocation': [],
        'microphone': [],
        'camera': [],
        'payment': [],
        'usb': [],
        'magnetometer': [],
        'gyroscope': [],
        'accelerometer': [],
    }
except ImportError:
    pass

# Caching - Redis (optional, falls back to database cache)
if 'REDIS_URL' in os.environ:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ['REDIS_URL'],
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                }
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # Fallback to database cache if Redis not available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }

# Sentry error tracking
# Install: pip install sentry-sdk
if 'SENTRY_DSN' in os.environ:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        send_default_pii=False,
        environment='production',
        release=os.environ.get('APP_VERSION', '1.0.0'),
    )

# Production logging
# Check if log directory exists, otherwise use console only
log_file_path = os.environ.get('LOG_FILE', '/var/log/bmad_forge/django.log')
log_dir = os.path.dirname(log_file_path)
use_file_logging = os.path.exists(log_dir) or log_file_path == '/tmp/bmad_forge.log'

# Build handlers list based on available logging targets
_handlers = {
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'simple',
    },
}

if use_file_logging:
    _handlers['file'] = {
        'level': 'WARNING',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': log_file_path,
        'maxBytes': 1024 * 1024 * 10,  # 10MB
        'backupCount': 5,
        'formatter': 'verbose',
    }

_default_handlers = ['console'] if not use_file_logging else ['file', 'console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': _handlers,
    'root': {
        'handlers': _default_handlers,
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': _default_handlers,
            'level': 'INFO',
            'propagate': False,
        },
        'forge': {
            'handlers': _default_handlers,
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file'] if use_file_logging else ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Add Sentry handler if configured
if 'SENTRY_DSN' in os.environ:
    try:
        LOGGING['handlers']['sentry'] = {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        }
        LOGGING['loggers']['django']['handlers'].append('sentry')
        LOGGING['loggers']['forge']['handlers'].append('sentry')
    except Exception:
        pass

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'admin@example.com')

# Admin notifications
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@example.com')),
]
MANAGERS = ADMINS
