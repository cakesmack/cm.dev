import sys
import os

# Add project directory to path
project_home = '/home/cmack6189/cm.dev/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add venv site-packages to path
venv_site_packages = '/home/cmack6189/cm.dev/backend/venv/lib/python3.13/site-packages'
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Change to project directory
os.chdir(project_home)

# Import FastAPI app and wrap with ASGI-to-WSGI adapter
from app.main import app
from a2wsgi import ASGIMiddleware

application = ASGIMiddleware(app)
