import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive_project.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# For Vercel serverless functions
def handler(request, context):
    return application(request, context) 