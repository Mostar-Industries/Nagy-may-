# Mastomys YOLO ML Service

Python FastAPI backend for Mastomys rodent detection using YOLOv8.

## Quick Start

### Prerequisites
- Python 3.11+
- pip or poetry

### Installation

\`\`\`bash
cd backend
pip install -r requirements.txt
\`\`\`

### Running Locally

\`\`\`bash
python -m ml_service.app
\`\`\`

The service will start on `http://localhost:5000`

### API Endpoints

- `GET /health` - Health check
- `POST /detect` - Single image detection
- `POST /detect/batch` - Batch image detection
- `GET /model/info` - Model information
- `GET /docs` - Interactive API documentation

### Docker Deployment

\`\`\`bash
docker build -t mastomys-ml .
docker run -p 5000:5000 mastomys-ml
\`\`\`

### Example Usage

\`\`\`python
import requests

# Upload image for detection
with open("rodent.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:5000/detect", files=files)
    print(response.json())
\`\`\`

## Configuration

Set environment variables in `.env`:
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 5000)
- `MODEL_NAME` - YOLO model to use (default: yolov8n.pt)
- `DEVICE` - Device for inference (cpu or cuda)
