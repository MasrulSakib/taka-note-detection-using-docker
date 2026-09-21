# Bangladeshi Taka Note Detection — REST API & Docker Deployment

A lightweight REST API for detecting Bangladeshi Taka banknotes with a trained **YOLOv11** model. The API is built with **FastAPI** and can be run locally or packaged with **Docker**.

## Project Structure

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

## Getting Started

### 1. Set Up the Project Locally

Create a virtual environment and install the required dependencies.

```bash
# Create and activate virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Single-Image Inference

To test the trained model directly, run the inference script with one of the sample images. The script generates an annotated output image with the detected note.

```bash
python scripts/inference_demo.py --image tests/sample_images/Note-Image-16-_jpeg.rf.457e59c3af0f241758329414b33379bc.jpg
```

### 3. Start the REST API

Launch the FastAPI development server with:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once the server is running, you can use the following endpoints:

- **Swagger API Docs:** `http://localhost:8000/docs`
- **Health Check:** `GET http://localhost:8000/health`
- **Prediction:** `POST http://localhost:8000/predict`

#### Example Request

You can send an image to the prediction endpoint with `curl`:

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@tests/sample_images/Note-Image-16-_jpeg.rf.457e59c3af0f241758329414b33379bc.jpg"
```

#### Example Response

A successful prediction returns JSON similar to this:

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

### 4. Test the API

Make sure the API server is running before executing the test suite:

```bash
python tests/test_api.py
```

The tests cover API responsiveness, predictions for valid images, and error handling for invalid or missing files.

### 5. Run with Docker

Build the Docker image with:

```bash
docker build -t taka-note-detector .
```

Then start the container:

```bash
docker run -d -p 8000:8000 --name taka-api taka-note-detector
```

You can also use Docker Compose:

```bash
docker compose up -d --build
```

## Detailed Documentation

More detailed information about Docker deployment, container management, API usage with different programming languages, and troubleshooting is available here:

**[Deployment & API Usage Guide](docs/DEPLOYMENT.md)**

## Configuration

The application reads its main settings from environment variables:

| Environment Variable   | Default                  | Description                        |
| :--------------------- | :----------------------- | :--------------------------------- |
| `HOST`                 | `0.0.0.0`                | API bind address                   |
| `PORT`                 | `8000`                   | API server port                    |
| `MODEL_PATH`           | `models/weights/best.pt` | Path to YOLOv11 model weights      |
| `CONFIDENCE_THRESHOLD` | `0.25`                   | Minimum detection confidence score |
| `IMAGE_SIZE`           | `640`                    | YOLO image input dimension         |

## License

This project is licensed under the [MIT License](LICENSE).
