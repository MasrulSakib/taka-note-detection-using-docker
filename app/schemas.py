from typing import List
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float = Field(..., description="Left edge in pixels")
    y1: float = Field(..., description="Top edge in pixels")
    x2: float = Field(..., description="Right edge in pixels")
    y2: float = Field(..., description="Bottom edge in pixels")


class Detection(BaseModel):
    class_name: str = Field(..., description="Detected note denomination")
    confidence: float = Field(..., description="Detection confidence score (0.0 - 1.0)", ge=0.0, le=1.0)
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")


class PredictionResponse(BaseModel):
    filename: str
    num_detections: int
    detections: List[Detection]
    inference_time_ms: float


class ErrorResponse(BaseModel):
    detail: str
