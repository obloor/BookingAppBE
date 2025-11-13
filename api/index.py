# api/index.py

import os
import sys
from pathlib import Path

current = Path(__file__).resolve()
project_root = current.parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
