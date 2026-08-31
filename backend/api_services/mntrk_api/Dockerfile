FROM python:3.11-slim

# System dependencies (Mirrored from healthy ML service)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 libxext6 libxrender-dev libglib2.0-0 libgl1-mesa-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Fix: Ensure host/port match Docker Compose mapping
CMD ["python", "-m", "swagger_server"]
