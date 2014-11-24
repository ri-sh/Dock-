import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.

(head, path) = os.path.split(os.path.dirname(os.path.realpath(__file__)))
sys.path = [ head ] + sys.path

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
