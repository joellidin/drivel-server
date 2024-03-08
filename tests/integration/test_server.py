"""Test server endpoints."""

from fastapi.testclient import TestClient

from drivel_server.core.config import settings
from drivel_server.main import app


def test_root() -> None:
    with TestClient(app) as client:
        response = client.get(settings.API_V1_STR)
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
