# Skyhawk Auto-Inference System - Real-Time Integration Guide

## Overview

Skyhawk is a real-time, autonomous rodent detection system that continuously monitors RTSP video streams, runs YOLO inference, and pushes detections to Supabase for instant dashboard updates.

\`\`\`
[RTSP Streams] → [Capture Service] → [YOLO Inference] → [Risk Scoring]
                                                             ↓
                                        [PostgreSQL] ← [Detection Pipeline]
                                             ↓
                                        [Supabase Realtime Broadcast]
                                             ↓
                        [Next.js Frontend Auto-Updates Map + Dashboard]
\`\`\`

## Quick Start

### 1. Local Development

\`\`\`bash
cd backend

# Setup environment
bash scripts/setup-local.sh

# Start all services with Docker
bash scripts/docker-up.sh

# Run tests
python scripts/test-services.py
\`\`\`

### 2. Production Deployment

\`\`\`bash
# Build services
docker-compose -f docker-compose.v2.yml build

# Deploy to cloud
docker-compose -f docker-compose.v2.yml up -d
\`\`\`

## Architecture

### Services

| Service | Port | Purpose | Tech |
|---------|------|---------|------|
| **ML Service** | 5001 | YOLO inference | Python/FastAPI |
| **API Service** | 5002 | Detection CRUD | Python/Flask |
| **Agent Service** | 5003 | LLM queries | Python/Flask |
| **Capture Service** | — | RTSP watcher | Python/asyncio |
| **PostgreSQL** | 5432 | Data store | Database |

### Data Flow

1. **RTSP Capture**: Capture Service pulls frames from configured streams every N seconds
2. **Motion Filter**: Skips static frames to reduce processing (optional)
3. **YOLO Inference**: Sends frames to ML Service for object detection
4. **Risk Scoring**: Calculates epidemiological risk based on location, time, environment
5. **Database Insert**: Stores detection in PostgreSQL `detection_patterns` table
6. **Supabase Broadcast**: Triggers Realtime channel update
7. **Frontend Sync**: React hooks receive update and refresh map/dashboard

## Configuration

### Environment Variables

#### Capture Service (`.env`)
\`\`\`
DATABASE_URL=postgresql://user:pass@localhost:5432/mastomys
SUPABASE_URL=https://project.supabase.co
SUPABASE_KEY=anon-key
YOLO_API_URL=http://localhost:5001
INFERENCE_INTERVAL=5              # Process frame every 5 seconds
MOTION_THRESHOLD=0.1              # Motion sensitivity (0-1)
LOG_LEVEL=INFO
ENABLE_SNAPSHOTS=true             # Save detection frames
\`\`\`

#### RTSP Streams

Edit `capture_service/config.py` to add streams:

\`\`\`python
RTSP_STREAMS = [
    {
        "name": "My Camera",
        "url": "rtsp://camera-ip/stream",
        "location": {"lat": 6.5244, "lon": 3.3792},
        "region": "Nigeria",
        "enabled": True,
    },
    # Add more...
]
\`\`\`

Or use the frontend RTSP manager to add streams via UI.

## Frontend Integration

### Real-Time Hooks

Use these hooks in React components:

\`\`\`typescript
import { useRealtimeDetections } from "@/hooks/use-realtime-detections"
import { useDetectionStats } from "@/hooks/use-detection-stats"
import { useDetectionMapData } from "@/hooks/use-detection-map-data"

export function MyComponent() {
  const { detections, isConnected } = useRealtimeDetections()
  const stats = useDetectionStats(detections)
  const mapMarkers = useDetectionMapData(detections)
  
  return (
    <div>
      {isConnected && <span>● Live</span>}
      <p>Total detections: {stats.total}</p>
    </div>
  )
}
\`\`\`

### Components Using Real-Time Data

- **CesiumMap**: Auto-updates with new detections
- **StatsCards**: Live metrics (high risk areas, confidence, etc.)
- **RecentDetections**: Live table of new detections
- **Dashboard**: All components sync in real-time

## Adding RTSP Streams

### Option 1: Frontend UI

Use the `RTSPStreamManager` component:

\`\`\`tsx
<RTSPStreamManager />
\`\`\`

This allows adding/removing streams without restarting the capture service.

### Option 2: Configuration File

Edit `backend/capture_service/config.py`:

\`\`\`python
RTSP_STREAMS = [
    {
        "name": "Wildlife Kenya",
        "url": "rtsp://...",
        "location": {"lat": -1.28, "lon": 36.81},
        "enabled": True,
    },
]
\`\`\`

### Option 3: Plug-and-Play Service

Restart capture service to pick up new streams:

\`\`\`bash
docker-compose restart skyhawk_capture
\`\`\`

## Monitoring

### View Logs

\`\`\`bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f skyhawk_capture
docker-compose logs -f skyhawk_ml
\`\`\`

### Health Checks

Services have built-in health endpoints:

\`\`\`bash
# ML Service
curl http://localhost:5001/health

# API Service
curl http://localhost:5002/health

# Agent Service
curl http://localhost:5003/health
\`\`\`

### Metrics

Check real-time stats from the dashboard:
- Detections in last 24h
- High-risk areas count
- Model average confidence
- Detection rate by region

## Testing

### Run Integration Tests

\`\`\`bash
python backend/scripts/test-services.py
\`\`\`

This validates:
- All services are healthy
- Endpoints return correct responses
- Database connectivity
- RTSP stream connectivity

### Manual Testing

\`\`\`bash
# Test ML inference
curl -X POST http://localhost:5001/detect \
  -F "image=@test-image.jpg"

# Test API
curl http://localhost:5002/detections

# Test Agent
curl http://localhost:5003/agent/alerts
\`\`\`

## Performance Tuning

### Inference Speed

Adjust in `capture_service/config.py`:

\`\`\`python
INFERENCE_INTERVAL = 2        # More frequent processing
MIN_CONFIDENCE = 0.6          # Stricter filtering
\`\`\`

### Database Optimization

Add indexes for common queries:

\`\`\`sql
CREATE INDEX idx_risk_score ON detection_patterns 
  ((risk_assessment->>'risk_score') DESC);

CREATE INDEX idx_timestamp ON detection_patterns 
  (detection_timestamp DESC);
\`\`\`

### Capture Service Scaling

Run multiple capture service instances for multiple streams:

\`\`\`bash
# docker-compose.yml
services:
  capture-1:
    # Stream set 1
  capture-2:
    # Stream set 2
\`\`\`

## Troubleshooting

### Detections not appearing on map

1. Check Supabase connection:
   \`\`\`bash
   docker-compose logs skyhawk_capture | grep SUPABASE
   \`\`\`

2. Verify Realtime is enabled in Supabase settings

3. Check browser console for errors

### RTSP streams failing to connect

1. Verify RTSP URLs are accessible:
   \`\`\`bash
   ffprobe rtsp://stream-url
   \`\`\`

2. Check network connectivity from container:
   \`\`\`bash
   docker-compose exec skyhawk_capture ping stream-host
   \`\`\`

3. Increase timeout in config:
   \`\`\`python
   RTSP_TIMEOUT = 10  # seconds
   \`\`\`

### High latency in updates

1. Reduce `INFERENCE_INTERVAL`
2. Lower image resolution in stream
3. Use GPU acceleration:
   \`\`\`bash
   DEVICE=cuda  # in .env
   \`\`\`

## Production Checklist

- [ ] Set strong database password
- [ ] Configure Supabase security rules
- [ ] Enable RLS on tables
- [ ] Set up monitoring/alerts
- [ ] Configure backup schedule
- [ ] Enable HTTPS for APIs
- [ ] Rate limit API endpoints
- [ ] Set up error logging (Sentry)
- [ ] Configure CDN for assets
- [ ] Test disaster recovery

## Next Steps

- Add email/SMS alerts
- Implement predictive modeling
- Add field technician routing
- Deploy to Kubernetes
- Integrate with health authorities
