"""
Django settings for django_courier demo
"""

from tests.settings import *  # noqa: F403,F401
from tests.settings import BASE_INSTALLED_APPS

INSTALLED_APPS = BASE_INSTALLED_APPS + [
    'tests.apps.CourierDemoConfig']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
