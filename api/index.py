import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

import django
django.setup()

from django.core.asgi import get_asgi_application
application = get_asgi_application()

async def handler(request, context):
    return await application(request, context)
