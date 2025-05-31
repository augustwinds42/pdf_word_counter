import os
import sys
import site

site.addsitedir(os.path.dirname(os.path.abspath(__file__)))

from app import app as application
# Also export as 'app' for compatibility with standard WSGI servers and our tests
app = application
