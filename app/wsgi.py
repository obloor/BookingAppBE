"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Apply WSGI application
from django.core.wsgi import get_wsgi_application

# This application object is used by the development server and any WSGI server
application = get_wsgi_application()

# For Vercel serverless environment
def vercel_handler(event, context):
    """Handler for Vercel serverless environment"""
    from django.core.handlers.wsgi import WSGIHandler
    return WSGIHandler()(event, context)
