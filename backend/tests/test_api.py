import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_status_result_flow():
    fake_image = io.BytesIO(b"fake-image-bytes")
    response = client.post(
        "/api/images/upload",
        files={"file": ("test.jpg", fake_image, "image/jpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    image_id = body["image_id"]
    assert body["status"] == "done"

    status_response = client.get(f"/api/images/{image_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "done"

    result_response = client.get(f"/api/images/{image_id}/result")
    assert result_response.status_code == 200
    result = result_response.json()
    assert "label" in result
    assert 0.0 <= result["confidence"] <= 1.0


def test_upload_rejects_non_image():
    fake_file = io.BytesIO(b"not an image")
    response = client.post(
        "/api/images/upload",
        files={"file": ("test.txt", fake_file, "text/plain")},
    )
    assert response.status_code == 400


def test_status_and_result_404_for_unknown_id():
    assert client.get("/api/images/unknown-id/status").status_code == 404
    assert client.get("/api/images/unknown-id/result").status_code == 404
