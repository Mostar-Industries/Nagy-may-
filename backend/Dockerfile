FROM python:3.11-slim

LABEL maintainer="MoStar Industries - African Flame Initiative"
LABEL version="2.0.0"
LABEL description="Skyhawk Mastomys Detection Service - Lassa fever surveillance"

WORKDIR /app

# Install system dependencies for OpenCV and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create weights directory
RUN mkdir -p /app/ml_service/models/weights

# Copy application code
COPY ml_service ./ml_service

# Copy model weights (if present in build context)
# The best.pt file should be placed in ml_service/models/weights/
COPY ml_service/models/weights/*.pt ./ml_service/models/weights/ 2>/dev/null || true
COPY ml_service/models/weights/*.onnx ./ml_service/models/weights/ 2>/dev/null || true

# Environment variables
ENV PORT=5001
ENV HOST=0.0.0.0
ENV YOLO_DEVICE=cpu
ENV YOLO_CONFIDENCE_THRESHOLD=0.5
ENV YOLO_MODEL_PATH=/app/ml_service/models/weights/best.pt
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run application
CMD ["python", "-m", "ml_service.app"]
