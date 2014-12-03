"""
WSGI config for Marine Planner CROP
"""

import os

activate_this = '/home/crop/env/cms-crop/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtaildemo.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
