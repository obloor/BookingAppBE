import os
import sys
from pathlib import Path

current = Path(__file__).resolve()
project_root = current.parent.parent
monorepo_root = project_root.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(monorepo_root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

from django.core.asgi import get_asgi_application
application = get_asgi_application()
