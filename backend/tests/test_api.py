import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import model
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def stub_model(monkeypatch):
    """Подменяем тяжёлую модель на фиктивный результат, но сохраняем проверку
    декодируемости изображения, как это делает реальный model.classify."""

    def fake_classify(image_bytes: bytes):
        Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return "NORMAL", 0.87

    monkeypatch.setattr(model, "classify", fake_classify)


def _fake_jpeg_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), color="white").save(buffer, format="JPEG")
    return buffer.getvalue()


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_status_result_flow():
    response = client.post(
        "/api/images/upload",
        files={"file": ("test.jpg", _fake_jpeg_bytes(), "image/jpeg")},
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
    assert result["label"] == "NORMAL"
    assert 0.0 <= result["confidence"] <= 1.0


def test_upload_rejects_non_image_content_type():
    response = client.post(
        "/api/images/upload",
        files={"file": ("test.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_rejects_corrupt_image_bytes():
    response = client.post(
        "/api/images/upload",
        files={"file": ("test.jpg", b"not actually a jpeg", "image/jpeg")},
    )
    assert response.status_code == 400


def test_status_and_result_404_for_unknown_id():
    assert client.get("/api/images/unknown-id/status").status_code == 404
    assert client.get("/api/images/unknown-id/result").status_code == 404
