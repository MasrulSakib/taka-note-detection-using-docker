import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Model configuration
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "weights" / "best.pt"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", "640"))

# API configuration
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
