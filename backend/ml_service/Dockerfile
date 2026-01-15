FROM python:3.11-slim

LABEL maintainer="MoStar Industries - African Flame Initiative"
LABEL version="2.0.0"
LABEL description="Skyhawk Mastomys Detection Service - REMOSTAR Enhanced"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 libxext6 libxrender-dev libglib2.0-0 libgl1-mesa-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p models/weights

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5001
ENV HOST=0.0.0.0

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

CMD ["python", "-m", "app"]