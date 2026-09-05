from typing import TypedDict


class ImageRecord(TypedDict):
    status: str
    label: str
    confidence: float


_records: dict[str, ImageRecord] = {}


def save(image_id: str, record: ImageRecord) -> None:
    _records[image_id] = record


def get(image_id: str) -> ImageRecord | None:
    return _records.get(image_id)
