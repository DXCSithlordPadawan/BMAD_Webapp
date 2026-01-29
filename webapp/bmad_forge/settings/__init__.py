"""
Settings module with automatic environment detection.

Loads the appropriate settings based on DJANGO_ENV environment variable:
- production: Production settings with security hardening
- test: Test-optimized settings
- development: Development settings (default)
"""

import os

# Detect environment from DJANGO_ENV variable
# Default to 'development' if not specified
env = os.environ.get('DJANGO_ENV', 'development').lower()

# Import appropriate settings module
if env == 'production':
    from .production import *
elif env == 'test':
    from .test import *
else:
    from .development import *
