from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Celery with the correct project name ('core')
app = Celery('core')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Ensure this setting is included for Celery 6.0+
app.conf.broker_connection_retry_on_startup = True

# Auto-discover tasks from installed Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
