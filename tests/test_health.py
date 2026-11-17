"""
Sog'liq (Health check) va loyiha sozlamalarini tekshirish uchun testlar.
"""

import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_check_endpoint():
    """/api/health/ manzili 200 qaytarishi va status ok bo'lishi kerak."""
    client = Client()
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "profur-backend"}
