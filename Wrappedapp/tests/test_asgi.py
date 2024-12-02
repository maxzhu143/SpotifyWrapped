import os
import unittest
from django.core.asgi import get_asgi_application
from django.core.exceptions import ImproperlyConfigured

class ASGIConfigTestCase(unittest.TestCase):
    def test_asgi_application_initialization(self):
        # Ensure DJANGO_SETTINGS_MODULE is set
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SpotifyWrapped.settings')

        # Ensure the ASGI application is initialized without errors
        try:
            application = get_asgi_application()
            self.assertIsNotNone(application)
        except ImproperlyConfigured as e:
            self.fail(f"ASGI application failed to initialize: {e}")
