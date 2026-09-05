import random
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app import storage
from app.schemas import ResultResponse, StatusResponse, UploadResponse

router = APIRouter(prefix="/api/images", tags=["images"])

# Заглушка вместо реальной модели: реальный инференс появится на этапе
# "Дообучение и интеграция модели" (docs/PLAN.md), после выбора базовой модели.
_STUB_LABELS = ["normal", "abnormal"]


@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile) -> UploadResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    image_id = str(uuid.uuid4())
    storage.save(
        image_id,
        {
            "status": "done",
            "label": random.choice(_STUB_LABELS),
            "confidence": round(random.uniform(0.5, 0.99), 2),
        },
    )
    return UploadResponse(image_id=image_id, status="done")


@router.get("/{image_id}/status", response_model=StatusResponse)
async def get_status(image_id: str) -> StatusResponse:
    record = storage.get(image_id)
    if record is None:
        raise HTTPException(status_code=404, detail="image_id не найден")
    return StatusResponse(image_id=image_id, status=record["status"])


@router.get("/{image_id}/result", response_model=ResultResponse)
async def get_result(image_id: str) -> ResultResponse:
    record = storage.get(image_id)
    if record is None:
        raise HTTPException(status_code=404, detail="image_id не найден")
    return ResultResponse(label=record["label"], confidence=record["confidence"])
