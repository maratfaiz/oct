from pydantic import BaseModel


class UploadResponse(BaseModel):
    image_id: str
    status: str


class StatusResponse(BaseModel):
    image_id: str
    status: str


class ResultResponse(BaseModel):
    label: str
    confidence: float
    uncertain: bool
