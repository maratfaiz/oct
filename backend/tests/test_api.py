import io
import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import model, storage
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


@pytest.fixture(autouse=True)
def isolated_storage(monkeypatch, tmp_path):
    """Каждый тест работает со своей БД и папкой загрузок, а не с реальными
    данными проекта."""
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setattr(storage, "UPLOADS_DIR", str(tmp_path / "uploads"))


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
    assert result["uncertain"] is False

    assert os.path.exists(os.path.join(storage.UPLOADS_DIR, image_id))


def test_result_flags_low_confidence_as_uncertain(monkeypatch):
    def fake_classify(image_bytes: bytes):
        Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return "NORMAL", 0.5

    monkeypatch.setattr(model, "classify", fake_classify)

    upload_response = client.post(
        "/api/images/upload",
        files={"file": ("test.jpg", _fake_jpeg_bytes(), "image/jpeg")},
    )
    image_id = upload_response.json()["image_id"]

    result = client.get(f"/api/images/{image_id}/result").json()
    assert result["uncertain"] is True


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
