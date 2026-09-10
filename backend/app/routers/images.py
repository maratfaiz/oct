import uuid

from fastapi import APIRouter, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app import model, storage
from app.schemas import ResultResponse, StatusResponse, UploadResponse

router = APIRouter(prefix="/api/images", tags=["images"])


@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile) -> UploadResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    image_bytes = await file.read()
    try:
        label, confidence = await run_in_threadpool(model.classify, image_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Не удалось прочитать изображение") from exc

    image_id = str(uuid.uuid4())
    storage.save(
        image_id,
        {
            "status": "done",
            "label": label,
            "confidence": confidence,
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
