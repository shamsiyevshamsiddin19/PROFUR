"""Use Django's in-process HTTP client without production HTTPS redirects."""

import pytest


@pytest.fixture(autouse=True)
def in_process_http_client(settings):
    """HTTPS termination is handled outside Django in deployed environments."""
    settings.SECURE_SSL_REDIRECT = False
