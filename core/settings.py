"""
Django settings for the trademarks project.

Created with Django 5.1.4. Using django-tables2, 
django-celery-beat, django-crispy-forms, 
django-redis-server, and bootstrap5.
"""

# Imports of the required python modules and libraries
######################################################
from pathlib import Path
import os
import sys
import re

# Reconfigures the standard output (stdout) encoding to UTF-8 to support non-ASCII characters.
sys.stdout.reconfigure(encoding='utf-8')

# The BASE_DIR is the absolute path to the project directory, used to help generate file paths relative to the project.
BASE_DIR = Path(__file__).resolve().parent.parent

# Specifies the URL configuration module for the project.
# This is typically the file where all URL patterns for the project are defined.
ROOT_URLCONF = 'core.urls'

# Specifies the custom user model to be used in place of the default Django User model.
# Here, 'users.CustomUser' refers to a user model defined in the 'users' app with the name 'CustomUser'.
AUTH_USER_MODEL = 'users.CustomUser'

# Specifies the WSGI application used to serve the Django project.
# This is typically set to the path to your WSGI application file in the core app.
WSGI_APPLICATION = 'core.wsgi.application'

# Defines where the user should be redirected after successfully logging in.
LOGIN_REDIRECT_URL = '/'

# Specifies the URL to redirect to for the login page.
LOGIN_URL = '/login/'

# Defines the URL where the user will be redirected after logging out.
LOGOUT_REDIRECT_URL = 'index'

# Production settings
#########################################################################################################
# SECURITY WARNING: keep the secret key used in production secret!
# The SECRET_KEY is used for cryptographic signing and should be kept private in production.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-cdo1^@rz#s)d69d^0snm1(*!bfe#!eix%4z^%fsj!!hwskl107')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG should be set to False in production to prevent sensitive data exposure in errors.
DEBUG = True

# SECURITY WARNING: don't run with secure HTTPS connections False in production!
# Ensures that cookies for sessions and CSRF are only sent over secure (HTTPS) connections in production.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# SECURITY WARNING: don't allow all hosts in production!
# List of allowed host/domain names that the app can serve.
# In production, this should only include trusted domain names.
ALLOWED_HOSTS = ['*']

# Control whether the site can be embedded in an <iframe> externally.
# Prevents the site from being embedded in an iframe on other websites for security reasons.
X_FRAME_OPTIONS = "SAMEORIGIN"

# Silences specific system checks during Django startup.
# This is often used to suppress warnings you consider non-critical or specific to your environment.
SILENCED_SYSTEM_CHECKS = ["security.W019"]
#########################################################################################################

# List of installed applications in the Django project.
# This includes Django apps and third-party apps that contribute functionality to the project.
INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'documents',
    'users',
    'crispy_forms',
    "crispy_bootstrap5",
    'django_tables2',
]

# List of middleware classes that process requests before and after the view function is called.
# Middleware are hooks into Django’s request/response processing.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Configuration for Django templates. This includes settings for template engines.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'documents', 'templates'), os.path.join(BASE_DIR, 'users', 'templates')],
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

# Allows crispy-forms to use the 'bootstrap5' template pack for rendering form fields.
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# Specifies the template pack used by crispy-forms for rendering forms.
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# PostgreSQL database settings.
# Defines the database settings, including the database engine and connection parameters.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),  # This should match your .env variable
        'USER': os.getenv('POSTGRES_USER'),  # This should match your .env variable
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),  # This should match your .env variable
        'HOST': 'postgres_db',  # This should match the service name in Docker Compose
        'PORT': '5432',
    }
}

# Redis Cache configuration for the Django app, usually for storing temporary data for better performance.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',  # Adjust the port and database number as needed
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery configuration for task queue management.
# This includes settings for the broker, which in this case is Redis.
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER', 'redis://redis:6379/0')  # Adjust if Redis is running on a different host or port
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Password validation settings to enhance security for user passwords.
# These settings control the password complexity and validation checks.
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


# Language and timezone settings.
# Defines the language code for the application and the timezone used for date and time.
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Etc/GMT-2'
USE_I18N = True
USE_TZ = True

# Default charset for the application. It's set to UTF-8 for international character support.
DEFAULT_CHARSET = 'utf-8'

# Specifies the paths for translation files. 
# This is where the application will look for language files.
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files settings define how static assets like CSS, JavaScript, and images are served.
STATIC_URL = '/static/'

# The root directory where static files will be collected for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Additional directories where static files are stored.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "documents/static"),
]

# For Compression and Manifest Storage
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Defines the default primary key field type to be used for models when no explicit primary key is set.
# The 'BigAutoField' allows for larger integers (up to 9223372036854775807) as primary keys, which is useful for applications with a large number of records.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MEDIA_URL is the URL where files will be accessed from the browser
MEDIA_URL = '/media/'

# MEDIA_ROOT is the actual filesystem path where the files are stored
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# low-level logging settings for the entire Django project.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/logs.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5MB max size per log file
            'backupCount': 2,  # Keep only 3 log files
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'documents': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Link error messages to Bootstrap danger class
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

def get_last_version_from_readme():
    if not os.path.exists("README.MD"):
        return "Unknown"  # Return a default version if the file is missing

    try:
        with open("README.MD", "r", encoding="utf-8") as f:
            content = f.read()
            # Use regex to find all version numbers prefixed by 'v'
            versions = re.findall(r'v(\d+\.\d+\.\d+)', content)
            return versions[-1] if versions else "Unknown"
    except Exception as e:
        return f"Error: {str(e)}"  # Handle unexpected errors gracefully

VERSION = get_last_version_from_readme()