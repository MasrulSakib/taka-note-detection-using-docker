import os
from typing import Dict, List, Union
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

from app.config import CONFIDENCE_THRESHOLD, IMAGE_SIZE, MODEL_PATH

_model = None


def load_model() -> YOLO:
    """Loads the trained YOLOv11 model weights into memory."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model weights not found at '{MODEL_PATH}'. "
                "Please place 'best.pt' in the models/weights/ directory."
            )
        _model = YOLO(MODEL_PATH)
    return _model


def run_inference(
    image: Union[str, Image.Image],
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> List[Dict]:
    """Runs object detection on an image and returns formatted detections."""
    model = load_model()
    results = model.predict(
        source=image,
        conf=confidence_threshold,
        imgsz=IMAGE_SIZE,
        verbose=False,
    )
    result = results[0]

    detections = []
    class_names = result.names

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]

        detections.append(
            {
                "class_name": class_names[class_id],
                "confidence": round(confidence, 4),
                "bbox": {
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "x2": round(x2, 2),
                    "y2": round(y2, 2),
                },
            }
        )

    return detections


def draw_detections(image: Image.Image, detections: List[Dict]) -> Image.Image:
    """Draws bounding boxes and labels on an image."""
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default()

    for det in detections:
        box = det["bbox"]
        label = f"{det['class_name']} {det['confidence']:.2f}"
        draw.rectangle(
            [box["x1"], box["y1"], box["x2"], box["y2"]],
            outline="lime",
            width=3,
        )
        draw.text((box["x1"] + 4, max(box["y1"] - 14, 0)), label, fill="lime", font=font)

    return annotated
