# Deployment & API Usage Guide

Complete guide for building, running, and interacting with the **Bangladeshi Taka Note Detection API**.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Building the Docker Image](#1-building-the-docker-image)
- [2. Running the Container](#2-running-the-container)
- [3. Using the API Endpoints](#3-using-the-api-endpoints)
- [4. Troubleshooting](#4-troubleshooting)

---

## Prerequisites

Before you begin, make sure you have the following installed:

| Tool             | Minimum Version | Installation                                    |
| :--------------- | :-------------- | :---------------------------------------------- |
| Docker           | 20.10+          | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| Docker Compose   | 2.0+ (optional) | Included with Docker Desktop                    |

You also need the **trained YOLOv11 model weights** file (`best.pt`) placed at:

```
models/weights/best.pt
```

> **Note:** The Docker image copies this file during the build step. If the weights file is missing, the build will succeed but the API will return a `500` error on prediction requests.

---

## 1. Building the Docker Image

### Option A — Using `docker build` (Recommended for Single Containers)

From the project root directory, run:

```bash
docker build -t taka-note-detector .
```

**What this does:**

1. Uses `python:3.10-slim` as the base image.
2. Installs system dependencies required by OpenCV (`libgl1`, `libglib2.0-0`).
3. Installs Python packages from `requirements.txt`.
4. Copies the `app/` source code and `models/` weights into the container.
5. Exposes port `8000` and sets the startup command.

**Build options:**

```bash
# Tag with a specific version
docker build -t taka-note-detector:v1.0 .

# Build with no cache (forces fresh install of all layers)
docker build --no-cache -t taka-note-detector .
```

### Option B — Using Docker Compose

Docker Compose builds the image automatically when you run:

```bash
docker compose up --build
```

This reads the `docker-compose.yml` file, which references the `Dockerfile` in the current directory.

### Verifying the Build

After building, confirm the image exists:

```bash
docker images | grep taka-note-detector
```

Expected output:

```
taka-note-detector   latest   abc123def456   10 seconds ago   1.2GB
```

---

## 2. Running the Container

### Option A — Using `docker run`

```bash
docker run -d -p 8000:8000 --name taka-api taka-note-detector
```

| Flag            | Purpose                                          |
| :-------------- | :----------------------------------------------- |
| `-d`            | Run in detached (background) mode                |
| `-p 8000:8000`  | Map host port 8000 → container port 8000         |
| `--name taka-api` | Assign a human-readable container name         |

#### Customizing with Environment Variables

Override defaults by passing `-e` flags:

```bash
docker run -d \
  -p 9000:9000 \
  --name taka-api \
  -e PORT=9000 \
  -e CONFIDENCE_THRESHOLD=0.5 \
  -e IMAGE_SIZE=640 \
  taka-note-detector
```

**Available environment variables:**

| Variable               | Default                  | Description                              |
| :--------------------- | :----------------------- | :--------------------------------------- |
| `HOST`                 | `0.0.0.0`               | Network interface to bind to             |
| `PORT`                 | `8000`                   | Port the API server listens on           |
| `MODEL_PATH`           | `models/weights/best.pt` | Path to YOLOv11 weights inside container |
| `CONFIDENCE_THRESHOLD` | `0.25`                   | Minimum detection confidence (0.0–1.0)   |
| `IMAGE_SIZE`           | `640`                    | Input image dimension for YOLO inference |

### Option B — Using Docker Compose (Recommended)

```bash
# Start in background (builds if needed)
docker compose up -d --build

# Start in foreground (see logs in real-time)
docker compose up --build
```

The `docker-compose.yml` is pre-configured with sensible defaults:

```yaml
services:
  app:
    build: .
    container_name: taka-note-api
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
    restart: unless-stopped
```

### Managing the Container

```bash
# View running containers
docker ps

# View container logs
docker logs taka-api            # docker run
docker compose logs -f          # docker compose

# Stop the container
docker stop taka-api            # docker run
docker compose down             # docker compose

# Restart the container
docker restart taka-api         # docker run
docker compose restart          # docker compose

# Remove the container
docker rm taka-api              # docker run
docker compose down --rmi all   # docker compose (also removes image)
```

### Verifying the Container is Running

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok"}
```

---

## 3. Using the API Endpoints

Once the container is running, the API is available at `http://localhost:8000`.

### Interactive Documentation (Swagger UI)

Open your browser and navigate to:

```
http://localhost:8000/docs
```

This provides a fully interactive interface to explore and test all endpoints without writing any code.

---

### `GET /` — Root

Returns a welcome message and lists available endpoints.

**Request:**

```bash
curl http://localhost:8000/
```

**Response:**

```json
{
  "message": "Bangladeshi Taka Note Detection API is running.",
  "docs": "/docs",
  "predict_endpoint": "/predict (POST)"
}
```

---

### `GET /health` — Health Check

Confirms the API server is up and the model is loaded.

**Request:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{"status": "ok"}
```

Use this endpoint for container health checks and monitoring.

---

### `POST /predict` — Detect Taka Notes

The core endpoint. Upload an image and receive detected banknote denominations with bounding boxes.

#### Request

- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Field name:** `file`
- **Accepted formats:** JPEG (`.jpg`, `.jpeg`) and PNG (`.png`)

#### Using `curl`

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@path/to/your/image.jpg"
```

#### Using Python (`requests`)

```python
import requests

url = "http://localhost:8000/predict"

with open("path/to/your/image.jpg", "rb") as f:
    response = requests.post(url, files={"file": ("image.jpg", f, "image/jpeg")})

data = response.json()
print(f"Detected {data['num_detections']} note(s):")
for det in data["detections"]:
    print(f"  {det['class_name']} — confidence: {det['confidence']}")
```

#### Using PowerShell

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method Post `
  -Form @{ file = Get-Item "path\to\your\image.jpg" }

$response | ConvertTo-Json -Depth 5
```

#### Using JavaScript (`fetch`)

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("http://localhost:8000/predict", {
  method: "POST",
  body: formData,
});

const data = await response.json();
console.log(`Detected ${data.num_detections} note(s)`);
```

#### Successful Response (`200 OK`)

```json
{
  "filename": "sample_1.jpg",
  "num_detections": 1,
  "detections": [
    {
      "class_name": "500taka",
      "confidence": 0.932,
      "bbox": {
        "x1": 80.12,
        "y1": 193.68,
        "x2": 380.31,
        "y2": 355.19
      }
    }
  ],
  "inference_time_ms": 75.2
}
```

**Response fields:**

| Field              | Type     | Description                                  |
| :----------------- | :------- | :------------------------------------------- |
| `filename`         | `string` | Original uploaded filename                   |
| `num_detections`   | `int`    | Number of banknotes detected in the image    |
| `detections`       | `array`  | List of detection objects (see below)        |
| `inference_time_ms`| `float`  | Model inference time in milliseconds         |

**Each detection object:**

| Field        | Type     | Description                                       |
| :----------- | :------- | :------------------------------------------------ |
| `class_name` | `string` | Detected denomination (e.g., `"500taka"`)         |
| `confidence` | `float`  | Confidence score between `0.0` and `1.0`          |
| `bbox`       | `object` | Bounding box with `x1`, `y1`, `x2`, `y2` (pixels)|

#### Error Responses

| Status Code | Cause                                          | Example `detail`                                         |
| :---------- | :--------------------------------------------- | :------------------------------------------------------- |
| `400`       | No file uploaded                               | `"No file uploaded."`                                    |
| `400`       | Unsupported file type (not JPEG/PNG)           | `"Unsupported file type 'text/plain'. Please upload a JPEG or PNG image."` |
| `400`       | Empty file                                     | `"Uploaded file is empty."`                              |
| `400`       | Corrupt/invalid image                          | `"Invalid image file format."`                           |
| `422`       | Missing required `file` field                  | Validation error (auto-generated by FastAPI)             |
| `500`       | Model weights not found                        | `"Model weights not found at '...'."`                    |
| `500`       | Unexpected inference failure                   | `"Inference error: ..."`                                 |

Error responses follow this format:

```json
{
  "detail": "Descriptive error message here."
}
```

---

## 4. Troubleshooting

### Container Exits Immediately

**Symptom:** `docker ps` shows no running container.

```bash
# Check logs for the error
docker logs taka-api
```

Common causes:
- **Missing model weights** — ensure `models/weights/best.pt` exists before building.
- **Port conflict** — another process is using port 8000. Use a different port: `-p 9000:8000`.

### `Connection Refused` When Calling the API

- Verify the container is running: `docker ps`
- Verify port mapping: `docker port taka-api`
- If using Docker Toolbox (older Windows/Mac), use `docker-machine ip` instead of `localhost`.

### Slow First Prediction

The first `/predict` request may take a few seconds longer than usual. This is normal — the YOLOv11 model performs warm-up computations on the first inference. Subsequent requests will be significantly faster.

### High Memory Usage

The YOLOv11 model requires approximately **1–2 GB of RAM**. Ensure your Docker engine has sufficient memory allocated (check Docker Desktop → Settings → Resources).
