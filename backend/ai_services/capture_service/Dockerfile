FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into package directory
COPY . /app/capture_service

# Add /app to PYTHONPATH to allow imports using 'capture_service'
ENV PYTHONPATH=/app

# Run capture service as a module
CMD ["python", "-m", "capture_service.app"]
