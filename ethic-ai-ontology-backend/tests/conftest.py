import pytest
from fastapi.testclient import TestClient

from main import app

@pytest.fixture(scope="module")
def client():
    """Returns a FastAPI TestClient instance."""
    with TestClient(app) as client:
        yield client
