"""
WSGI config for BMAD Forge project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmad_forge.settings')
application = get_wsgi_application()
