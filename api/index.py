import sys
import os

# プロジェクトのルートパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "archive_project.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application() 