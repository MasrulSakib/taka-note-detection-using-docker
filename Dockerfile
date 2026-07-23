# ==============================================================================
# Bangladeshi Taka Note Detection API Dockerfile
#
# 1. How to build this Docker image:
#    docker build -t taka-note-detector .
#
# 2. How to run the container:
#    docker run -d -p 8000:8000 --name taka-api taka-note-detector
#
# 3. How to use the API endpoint:
#    - Interactive API Docs: http://localhost:8000/docs
#    - Prediction endpoint: POST http://localhost:8000/predict
#      Example curl command:
#        curl -X POST "http://localhost:8000/predict" -F "file=@path/to/image.jpg"
# ==============================================================================

FROM python:3.10-slim

WORKDIR /app

# Install system libraries required for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and weights
COPY app/ ./app/
COPY models/ ./models/

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
