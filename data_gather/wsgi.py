"""
WSGI config for data_gather project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/usr/local/apps/data_gather')
sys.path.append('/usr/local/apps/data_gather/data_gather')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_gather.settings")

application = get_wsgi_application()
