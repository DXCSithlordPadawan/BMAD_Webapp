"""
Base Django settings for BMAD Forge project.

Contains common settings shared across all environments.
Environment-specific settings should be in development.py, production.py, or test.py.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import config loader
from bmad_forge.config import (
    ConfigLoader,
    get_app_name,
    get_app_version,
    get_template_github_repo,
    get_template_github_branch,
    get_template_github_path,
    get_template_local_path,
    get_sync_overwrite_existing,
    get_sync_match_by,
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'forge',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bmad_forge.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bmad_forge.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'forge' / 'static',
]

# Static files root for production (collectstatic destination)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Application settings (loaded from config.yaml)
APP_NAME = get_app_name()
APP_VERSION = get_app_version()

# Template location settings (loaded from config.yaml)
TEMPLATE_LOCAL_PATH = get_template_local_path()
TEMPLATE_GITHUB_REPO = get_template_github_repo()
TEMPLATE_GITHUB_BRANCH = get_template_github_branch()
TEMPLATE_GITHUB_PATH = get_template_github_path()
TEMPLATE_SYNC_OVERWRITE = get_sync_overwrite_existing()
TEMPLATE_SYNC_MATCH_BY = get_sync_match_by()

# Legacy settings for backwards compatibility
TEMPLATE_REPO = TEMPLATE_GITHUB_REPO

# GitHub settings
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_RAW_BASE_URL = os.environ.get('GITHUB_RAW_BASE_URL', 'https://raw.githubusercontent.com')
BMAD_METHOD_REPO = os.environ.get('BMAD_METHOD_REPO', 'bmadcode/BMAD-METHOD-v5')

# BMAD Framework settings
BMAD_AGENT_ROLES = [
    ('orchestrator', 'Orchestrator'),
    ('analyst', 'Analyst'),
    ('pm', 'Project Manager'),
    ('architect', 'Architect'),
    ('scrum_master', 'Scrum Master'),
    ('developer', 'Developer'),
    ('qa', 'QA Engineer'),
]

BMAD_WORKFLOW_PHASES = [
    ('planning', 'Planning Phase'),
    ('development', 'Development Phase'),
]

BMAD_REQUIRED_SECTIONS = [
    '## Your Role',
    '## Input',
    '## Output Requirements',
]

# Logging configuration (base configuration, environments can extend)
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
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'forge': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
