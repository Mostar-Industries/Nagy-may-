

# Skyhawk Backend Architecture - Mastomys Detection System

**Skyhawk** is a realtime surveillance system for detecting *Mastomys natalensis* (African rodents) using YOLOv8 computer vision, AI-powered risk scoring, and intelligent agent-based querying. This is the backend orchestration layer for the complete system.

## System Overview


┌──────────────────────────────────────────────────────────────────┐
│                   Skyhawk Backend System                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT LAYER (Video/Image)                                      │
│  ├─ RTSP Streams (camera feeds)                                 │
│  ├─ Uploaded Images (field technicians)                         │
│  └─ Batch Image Processing                                      │
│         ↓                                                        │
│  ML INFERENCE LAYER (ml_service - Port 5001)                    │
│  ├─ YOLOv8 Nano Model (fast, accurate)                          │
│  ├─ Bounding Box Extraction                                     │
│  ├─ Confidence Scoring                                          │
│  └─ Risk Score Calculation                                      │
│         ↓                                                        │
│  REST API LAYER (MNTRK_API - Port 5002)                         │
│  ├─ Detection Ingestion                                         │
│  ├─ Database Integration                                        │
│  ├─ Image Upload Management                                     │
│  └─ Geospatial Queries                                          │
│         ↓                                                        │
│  AGENT LAYER (MNTRK_Agent_API - Port 5003)                      │
│  ├─ LLM-Powered Queries                                         │
│  ├─ Intelligent Risk Analysis                                   │
│  ├─ External Data Augmentation                                  │
│  └─ Conversational Interface                                    │
│         ↓                                                        │
│  DATA LAYER (PostgreSQL)                                        │
│  └─ detection_patterns table                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘


## Services Directory

The backend is organized into three main services plus ML infrastructure:

| Service | Port | Purpose | Language |
|---------|------|---------|----------|
| **ml_service** | 5001 | YOLO inference + risk scoring | Python/FastAPI |
| **MNTRK_API** | 5002 | REST endpoint for detections | Python/Connexion |
| **MNTRK_Agent_API** | 5003 | LLM agent for querying | Python/Connexion |
| **PostgreSQL** | 5432 | Data layer | Database |

## Quick Start - Using Docker Compose

### Prerequisites
- Docker & Docker Compose installed
- 4GB RAM minimum

### Setup

1. **Clone and navigate to backend**:
bash
cd backend


2. **Create `.env` file** (from example):
bash
cp .env.example .env
# Edit .env with your database credentials if needed


3. **Start all services**:
bash
docker-compose up -d


4. **Verify services are running**:
bash
docker-compose ps


Expected output:

NAME                      STATUS
skyhawk-postgres          Up (healthy)
skyhawk-ml-service        Up (healthy)
skyhawk-api-service       Up (healthy)
skyhawk-agent-service     Up (healthy)


5. **Test services**:
bash
# Run bash tests
bash scripts/test-endpoints.sh

# Run Python integration tests
python scripts/test-integration.py


### Stopping Services
bash
# Stop all services
docker-compose down

# Stop and remove volumes (database data)
docker-compose down -v


## Individual Service Documentation

### 1. ML Service (Port 5001)

**Purpose**: Core YOLO inference and risk scoring engine

**Tech Stack**: FastAPI, YOLOv8, NumPy, OpenCV, Python 3.10+

**Key Files**:
- `ml_service/app.py` - FastAPI application
- `ml_service/models/yolo_detector.py` - YOLO inference
- `ml_service/utils/image_processor.py` - Image preprocessing
- `ml_service/utils/risk_scorer.py` - Risk calculation

**Endpoints**:

GET  /health               - Service health check
POST /detect               - Single image inference
POST /detect/batch         - Batch image processing
GET  /model/info           - Model metadata
GET  /docs                 - Interactive documentation


**Example Usage**:
bash
curl -X POST -F "image=@rodent.jpg" http://localhost:5001/detect


**Running Locally**:
bash
cd ml_service
pip install -r requirements.txt
python -m app


### 2. API Service (Port 5002)

**Purpose**: REST endpoint for detection storage, querying, and integration

**Tech Stack**: Connexion, Flask, SQLAlchemy, PostgreSQL

**Key Files**:
- `MNTRK_API/swagger_server/__main__.py` - Application entry point
- `MNTRK_API/swagger_server/controllers/default_controller.py` - Handlers
- `MNTRK_API/swagger_server/swagger/swagger.yaml` - API specification

**Endpoints**:

GET  /detections            - List detections (with filters)
POST /detections            - Create detection
GET  /detections/{id}       - Get detection by ID
POST /predict               - Upload image + get YOLO + risk
GET  /ui/                   - Swagger documentation


**Example Usage**:
bash
# Upload image and get detection
curl -X POST -F "image=@rodent.jpg" http://localhost:5002/predict

# Fetch recent detections
curl "http://localhost:5002/detections?limit=10"


**Running Locally**:
bash
cd MNTRK_API
pip install -r requirements.txt
python -m swagger_server


### 3. Agent Service (Port 5003)

**Purpose**: LLM-powered conversational interface for intelligent querying

**Tech Stack**: Connexion, Google Gemini API, PostgreSQL integration

**Key Files**:
- `MNTRK_Agent_API/swagger_server/__main__.py` - Agent service entry point
- `MNTRK_Agent_API/swagger_server/models/` - Request/response schemas
- `MNTRK_Agent_API/swagger_server/controllers/` - Agent logic

**Endpoints**:

GET  /agent/explain         - Explain detection risk
GET  /agent/alerts          - Recent alerts with AI summary
POST /agent/query           - Natural language query
POST /video/analyze         - Analyze video stream
POST /risk/analyze          - Deep risk analysis
GET  /ui/                   - Swagger documentation


**Example Queries**:
bash
# Get explanation for a detection
curl "http://localhost:5003/agent/explain?detection_id=42"

# Natural language query
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What rodent hotspots in Ondo State?"}' \
  http://localhost:5003/agent/query


**Running Locally**:
bash
cd MNTRK_Agent_API
pip install -r requirements.txt
python -m swagger_server


## Frontend Integration

### Calling Backend from Next.js

**File**: `lib/api-integration.ts` in the main Next.js app

typescript
// Call ML Service directly
export async function predictWithYOLO(image: File) {
  const formData = new FormData();
  formData.append('image', image);
  
  const response = await fetch('http://localhost:5001/detect', {
    method: 'POST',
    body: formData,
  });
  
  return response.json();
}

// Call REST API
export async function uploadDetection(image: File) {
  const formData = new FormData();
  formData.append('image', image);
  
  const response = await fetch('http://localhost:5002/predict', {
    method: 'POST',
    body: formData,
  });
  
  return response.json();
}

// Query Agent
export async function askAgent(query: string) {
  const response = await fetch('http://localhost:5003/agent/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  
  return response.json();
}


## Configuration

### Environment Variables

Key variables in `.env`:

bash
# Database
DATABASE_URL=postgresql://mastomys:password@localhost:5432/mastomys_tracker

# ML Service
YOLO_MODEL=yolov8n.pt
DEVICE=cpu                    # or 'cuda' for GPU
YOLO_CONFIDENCE_THRESHOLD=0.5

# Agent Service
GEMINI_API_KEY=your-key-here

# Optional External APIs
OPENWEATHER_API_KEY=
SORMAS_API_KEY=
CDC_API_KEY=


See `.env.example` for all available options.

## Monitoring & Debugging

### View Logs
bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ml-service
docker-compose logs -f api-service
docker-compose logs -f agent-service


### Database Access
bash
# Connect to PostgreSQL
docker exec -it skyhawk-postgres psql -U mastomys -d mastomys_tracker

# Query detections
SELECT id, latitude, longitude, created_at FROM detection_patterns LIMIT 10;


### API Documentation
- **ML Service**: http://localhost:5001/docs
- **API Service**: http://localhost:5002/ui/
- **Agent Service**: http://localhost:5003/ui/

## Deployment

### Docker Build
bash
docker build -t skyhawk-ml-service:0.2.1 ./ml_service/
docker build -t skyhawk-api-service:0.2.1 ./MNTRK_API/
docker build -t skyhawk-agent-service:0.2.1 ./MNTRK_Agent_API/


### Cloud Deployment (Google Cloud Run)

1. **Build and push images**:
bash
gcloud builds submit --tag gcr.io/PROJECT/skyhawk-ml-service ./ml_service/
gcloud builds submit --tag gcr.io/PROJECT/skyhawk-api-service ./MNTRK_API/


2. **Deploy to Cloud Run**:
bash
gcloud run deploy skyhawk-ml-service \
  --image gcr.io/PROJECT/skyhawk-ml-service \
  --memory 2Gi --timeout 120s


## Development Workflow

### Running Individual Services

**ML Service Only**:
bash
cd ml_service
pip install -r requirements.txt
python -m app


**API Service Only**:
bash
cd MNTRK_API
pip install -r requirements.txt
python -m swagger_server


**Agent Service Only**:
bash
cd MNTRK_Agent_API
pip install -r requirements.txt
python -m swagger_server


### Adding Dependencies

bash
cd SERVICE_NAME
pip install package_name
pip freeze > requirements.txt


Then rebuild Docker image:
bash
docker-compose build SERVICE_NAME
docker-compose restart SERVICE_NAME


## Performance Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Single image YOLO | 150-250ms | CPU-based |
| Batch detection (10 images) | 1.5-2.5s | Parallel |
| Risk scoring | 50-100ms | Per detection |
| Database insert | 10-50ms | Network dependent |
| Agent response | 1-3s | Includes LLM |

## Troubleshooting

### Service won't start
bash
# Check logs
docker-compose logs SERVICE_NAME

# Rebuild
docker-compose build --no-cache SERVICE_NAME
docker-compose restart SERVICE_NAME


### Database connection error
bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check credentials
cat .env | grep POSTGRES


### Out of memory
Increase Docker memory allocation in Docker Desktop preferences or adjust resource limits in docker-compose.yml.

## Templates & Architecture

This system implements 7 design templates:
- **video_library** - RTSP video ingestion and frame analysis
- **document_scanner** - Individual frame processing
- **bolt** - Real-time speed and low-latency inference
- **spark** - Gemini intelligence and risk fusion
- **voice_chat** - Conversational agent interface
- **google** - External context augmentation
- **maps** - Geospatial visualization

See `skyhawk_config.json` for complete template mapping.

## Contributing

1. Create feature branch
2. Make changes to one service
3. Test locally: `docker-compose up`
4. Submit PR with test results

## Support

For issues:
- Check logs: `docker-compose logs`
- Review API docs: http://localhost:5002/ui/
- Run integration tests: `python scripts/test-integration.py`

---

**Version**: 0.2.1  
**Skyhawk Team**
