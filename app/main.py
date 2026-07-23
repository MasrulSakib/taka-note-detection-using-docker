"""
Bangladeshi Taka Note Detection API

1. How to build the Docker image:
   docker build -t taka-note-detector .

2. How to run the container:
   docker run -d -p 8000:8000 --name taka-api taka-note-detector

3. How to use the API endpoint:
   - Interactive docs: http://localhost:8000/docs
   - Predict endpoint: POST http://localhost:8000/predict
     Send a multipart form-data request with the image file in the 'file' field.
     
     Example command (curl):
       curl -X POST "http://localhost:8000/predict" -F "file=@path/to/image.jpg"
"""

import io
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from app.config import ALLOWED_CONTENT_TYPES, CONFIDENCE_THRESHOLD
from app.inference import load_model, run_inference
from app.schemas import ErrorResponse, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load YOLO model once at server startup."""
    load_model()
    yield


app = FastAPI(
    title="Bangladeshi Taka Note Detection API",
    description="REST API to detect Bangladeshi Taka banknotes using YOLOv11.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "Bangladeshi Taka Note Detection API is running.",
        "docs": "/docs",
        "predict_endpoint": "/predict (POST)",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def predict(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    filename_lower = file.filename.lower() if file.filename else ""
    is_valid_ext = filename_lower.endswith((".jpg", ".jpeg", ".png"))
    is_valid_mime = file.content_type in ALLOWED_CONTENT_TYPES

    if not (is_valid_mime or is_valid_ext):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Please upload a JPEG or PNG image.",
        )

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file format.",
        )

    try:
        start_time = time.perf_counter()
        detections = run_inference(image, confidence_threshold=CONFIDENCE_THRESHOLD)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")

    return JSONResponse(
        status_code=200,
        content={
            "filename": file.filename,
            "num_detections": len(detections),
            "detections": detections,
            "inference_time_ms": round(elapsed_ms, 2),
        },
    )
