from fastapi.testclient import TestClient
from reqtools.mock_server.server import app

client = TestClient(app)


def test_echo_returns_payload():
    payload = {"message": "hello"}
    response = client.post("/echo", json=payload)
    assert response.status_code == 200
    assert response.json() == {"echo": payload}
