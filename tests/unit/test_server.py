"""Test server endpoints."""

from fastapi.testclient import TestClient

from drivel_server.server import app


def test_hello_world() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
