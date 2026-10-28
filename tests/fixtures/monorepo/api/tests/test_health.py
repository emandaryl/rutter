from fastapi.testclient import TestClient

from app.main import app

# API contract tests. Run with the full pytest suite (`make test`); these raise
# 503 if Postgres is not up, which CI treats as a skip.
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
