# Bangladeshi Taka Note Detection — REST API & Docker Deployment

A lightweight, beginner-friendly REST API for detecting Bangladeshi Taka banknotes using a trained **YOLOv11** model, built with **FastAPI** and containerized with **Docker**.

---

## 📁 Project Structure

```text
taka-note-detector/
├── app/
│   ├── __init__.py         # Package initializer
│   ├── config.py           # Application settings & environment variables
│   ├── inference.py        # Model loading & inference logic (Task 1)
│   ├── main.py             # FastAPI application & endpoints (Task 2)
│   └── schemas.py          # Request/Response Pydantic schemas
├── models/
│   └── weights/
│       └── best.pt         # Trained YOLOv11 model weights
├── scripts/
│   └── inference_demo.py   # Single image CLI inference demo (Task 1)
├── tests/
│   ├── sample_images/      # Test images
│   └── test_api.py         # Automated API test suite (Task 3)
├── Dockerfile              # Docker container recipe (Task 4)
├── docker-compose.yml      # Multi-container orchestration (Task 4)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # Documentation (Task 5)
```

---

## 🚀 Quick Start Guide

### 1. Local Setup

```bash
# Create and activate virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Task 1 — Single Image Inference Demo

Run detection on a single sample image and generate an annotated output image:

```bash
python scripts/inference_demo.py --image tests/sample_images/Note-Image-16-_jpeg.rf.457e59c3af0f241758329414b33379bc.jpg
```

---

### 3. Task 2 — Running the REST API

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive API Docs (Swagger)**: Access `http://localhost:8000/docs` in your browser.
- **Health Check**: `GET http://localhost:8000/health`
- **Predict Endpoint**: `POST http://localhost:8000/predict`

#### Sample `curl` Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@tests/sample_images/Note-Image-16-_jpeg.rf.457e59c3af0f241758329414b33379bc.jpg"
```

#### Sample JSON Response

```json
{
  "filename": "Note-Image-16-_jpeg.rf.457e59c3af0f241758329414b33379bc.jpg",
  "num_detections": 1,
  "detections": [
    {
      "class_name": "500_tk",
      "confidence": 0.7036,
      "bbox": {
        "x1": 80.12,
        "y1": 193.68,
        "x2": 380.31,
        "y2": 355.19
      }
    }
  ],
  "inference_time_ms": 79.93
}
```

---

### 4. Task 3 — API Testing & Validation

Ensure the API server is running, then execute the test suite:

```bash
python tests/test_api.py
```

This tests endpoint responsiveness, valid image predictions, and error handling for invalid/missing files.

---

### 5. Task 4 — Dockerization

#### Build the Docker Image

```bash
docker build -t taka-note-detector .
```

#### Run the Container

```bash
docker run -d -p 8000:8000 --name taka-api taka-note-detector
```

#### Or using Docker Compose:

```bash
docker compose up -d --build
```

---

## 📖 Detailed Documentation

For a comprehensive guide covering Docker builds, container management, API usage examples in multiple languages, and troubleshooting, see:

👉 **[Deployment & API Usage Guide](docs/DEPLOYMENT.md)**

---

## ⚙️ Configuration (.env)

| Environment Variable   | Default                  | Description                        |
| :--------------------- | :----------------------- | :--------------------------------- |
| `HOST`                 | `0.0.0.0`                | API bind address                   |
| `PORT`                 | `8000`                   | API server port                    |
| `MODEL_PATH`           | `models/weights/best.pt` | Path to YOLOv11 model weights      |
| `CONFIDENCE_THRESHOLD` | `0.25`                   | Minimum detection confidence score |
| `IMAGE_SIZE`           | `640`                    | YOLO image input dimension         |
