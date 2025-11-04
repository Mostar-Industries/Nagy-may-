# 🚀 Fully Automated Real-Time Detection System

**Status:** ✅ READY TO DEPLOY  
**Mode:** AUTONOMOUS - Zero Manual Intervention  
**Flow:** RTSP → Capture → Inference → Database → Map Visualization

---

## 🎯 System Architecture

```
[RTSP Camera Feed]
       ↓ (every 5 seconds)
[Frame Capture Service]
       ↓ (base64 encoding)
[YOLO ML Inference]
       ↓ (detections)
[Database + Supabase]
       ↓ (real-time SSE)
[Frontend Dashboard + Cesium Map]
```

**No uploads. No buttons. Pure automation.**

---

## 📦 Components

### 1. **Capture Service** (`backend/capture_service/`)

Autonomous frame capture from multiple RTSP streams.

**Key Files:**
- `capture_loop.py` - Main automation entry point
- `app.py` - Service orchestrator
- `rtsp_watcher.py` - RTSP stream monitoring
- `config.py` - Stream configuration
- `inference_client.py` - ML service client
- `detection_pusher.py` - Database writer
- `motion_filter.py` - Motion detection filter

**Features:**
- ✅ Multi-stream monitoring
- ✅ Automatic reconnection on stream loss
- ✅ Motion-based filtering (skip static frames)
- ✅ Configurable capture interval
- ✅ Thread-safe frame queue
- ✅ Health monitoring

### 2. **ML Service** (`backend/ml_service/`)

YOLO inference with enhanced detection.

**Endpoints:**
- `POST /api/detections/inference` - Analyze image
- `GET /health` - Service health check

### 3. **Frontend** (`app/monitoring/`)

Real-time dashboard with Cesium map.

**Features:**
- ✅ Live SSE detection stream
- ✅ Animated marker drops on map
- ✅ Detection cards with confidence
- ✅ Colony grouping visualization
- ✅ Real-time statistics

---

## 🛠️ Setup Instructions

### Option 1: Docker Compose (Recommended)

**1. Configure RTSP Streams**

Edit `backend/capture_service/config.py`:

```python
RTSP_STREAMS = [
    {
        "name": "Field Camera 1",
        "url": "rtsp://username:password@192.168.1.100:554/stream1",
        "location": {"lat": -1.286389, "lon": 36.817223},
        "region": "Kenya - Wildlife Reserve",
        "enabled": True,
    },
    {
        "name": "Border Monitor",
        "url": "rtsp://admin:pass123@10.0.0.50:554/h264",
        "location": {"lat": 9.0820, "lon": 8.6753},
        "region": "Nigeria - Abuja",
        "enabled": True,
    },
]
```

**2. Set Environment Variables**

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/db
POSTGRES_USER=mastomys
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DATABASE=mastomys_tracker

# Supabase (for real-time)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Capture Settings
INFERENCE_INTERVAL=5           # Capture every 5 seconds
MOTION_THRESHOLD=0.1           # Motion sensitivity
MIN_CONFIDENCE=0.5             # Min detection confidence
ENABLE_SNAPSHOTS=true          # Save detection images

# ML Service
YOLO_API_URL=http://ml-service:5000
```

**3. Start All Services**

```bash
cd backend
docker-compose up -d
```

**4. Monitor Logs**

```bash
# Watch capture service
docker-compose logs -f capture-service

# Watch all services
docker-compose logs -f
```

**5. View Detections**

Open: `http://localhost:5000/monitoring`

Detections will appear automatically on the map!

---

### Option 2: Standalone Python

**1. Install Dependencies**

```bash
cd backend/capture_service
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Set Environment Variables**

```bash
export DATABASE_URL="your_database_url"
export YOLO_API_URL="http://localhost:5001"
export INFERENCE_INTERVAL=5
```

**3. Start ML Service**

```bash
cd backend/ml_service
source .venv/bin/activate
python app.py
```

**4. Start Capture Service**

```bash
cd backend/capture_service
python capture_loop.py
```

---

## 🔧 Configuration Options

### Capture Service (`config.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `INFERENCE_INTERVAL` | 5 | Seconds between captures |
| `MOTION_THRESHOLD` | 0.1 | Motion sensitivity (0-1) |
| `MIN_CONFIDENCE` | 0.5 | Min detection confidence |
| `ENABLE_SNAPSHOTS` | true | Save detection images |
| `SNAPSHOTS_DIR` | `/tmp/snapshots` | Where to save images |
| `MAX_RETRIES` | 3 | RTSP reconnection attempts |

### RTSP Stream Configuration

Each stream requires:
- **name**: Human-readable identifier
- **url**: RTSP URL (`rtsp://user:pass@ip:port/path`)
- **location**: GPS coordinates `{lat, lon}`
- **region**: Geographic description
- **enabled**: Boolean to enable/disable

**RTSP URL Formats:**

```
# Hikvision
rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101

# Dahua
rtsp://admin:password@192.168.1.101:554/cam/realmonitor?channel=1&subtype=0

# Axis
rtsp://root:password@192.168.1.102/axis-media/media.amp

# Generic
rtsp://username:password@ip:port/stream1
```

---

## 📊 Monitoring & Health

### Service Health Checks

```bash
# Check ML service
curl http://localhost:5001/health

# Check capture service logs
docker-compose logs capture-service | tail -n 50

# Check all services status
docker-compose ps
```

### Key Metrics

Monitor these in logs:

- **Frame Capture Rate**: Should match `INFERENCE_INTERVAL`
- **Inference Time**: Typically 200-500ms (CPU) or 50-150ms (GPU)
- **Motion Detection**: % of frames passing motion filter
- **Database Writes**: Successful detection inserts
- **RTSP Connection Status**: Active/reconnecting

### Expected Log Output

```
2025-11-04 16:00:01 - [INFO] - SKYHAWK AUTONOMOUS DETECTION SYSTEM
2025-11-04 16:00:01 - [INFO] - Mode: FULLY AUTOMATED
2025-11-04 16:00:02 - [INFO] - Service initialized
2025-11-04 16:00:02 - [INFO] - Starting RTSP watchers...
2025-11-04 16:00:03 - [RTSP] - Connected to Field Camera 1
2025-11-04 16:00:03 - [RTSP] - Connected to Border Monitor
2025-11-04 16:00:03 - [INFO] - All RTSP watchers started
2025-11-04 16:00:08 - [MOTION] - Motion detected in Field Camera 1
2025-11-04 16:00:08 - [YOLO] - Running inference...
2025-11-04 16:00:09 - [YOLO] - Detected 2 objects (confidence: 0.87, 0.72)
2025-11-04 16:00:09 - [DB] - Saved detection to database
2025-11-04 16:00:09 - [SSE] - Pushed to real-time stream
```

---

## 🚨 Troubleshooting

### RTSP Connection Issues

**Problem:** Cannot connect to stream

**Solutions:**
1. Verify RTSP URL format
2. Check camera credentials
3. Test with VLC: `vlc rtsp://your-url`
4. Check firewall rules (port 554)
5. Verify network connectivity: `ping camera-ip`

**Problem:** Stream disconnects frequently

**Solutions:**
1. Increase `MAX_RETRIES` in config
2. Check network stability
3. Reduce `INFERENCE_INTERVAL` to capture less frequently
4. Verify camera bandwidth capacity

### ML Inference Issues

**Problem:** No detections appearing

**Solutions:**
1. Check `MIN_CONFIDENCE` threshold (try lowering to 0.3)
2. Verify YOLO model is loaded: Check ml_service logs
3. Test inference directly: `npx tsx scripts/test-inference.ts`
4. Check motion filter isn't too aggressive

**Problem:** Inference too slow

**Solutions:**
1. Use GPU if available (add GPU support to Docker)
2. Reduce image resolution in config
3. Use smaller YOLO model (yolov8n instead of yolov8m)
4. Increase `INFERENCE_INTERVAL`

### Database Issues

**Problem:** Detections not persisting

**Solutions:**
1. Verify `DATABASE_URL` is set correctly
2. Check database is running: `docker-compose ps postgres`
3. Test connection: `psql $DATABASE_URL -c "SELECT 1;"`
4. Check database schemas are applied
5. Review capture_service logs for DB errors

---

## 🎯 Performance Optimization

### For High-Volume Streams

```python
# config.py adjustments
INFERENCE_INTERVAL = 10  # Capture less frequently
MOTION_THRESHOLD = 0.15  # More aggressive filtering
MIN_CONFIDENCE = 0.6     # Only high-confidence detections
ENABLE_SNAPSHOTS = false # Disable to save disk space
```

### For Low-Power Devices

```python
# Use lightweight model
model_type = "yolov8n"  # Smallest, fastest

# Reduce resolution
img_size = 416  # Instead of 640

# Skip motion detection
MOTION_THRESHOLD = 0.0  # Process all frames
```

### For Maximum Accuracy

```python
# Use best model
model_type = "yolov8x"  # Largest, most accurate

# High resolution
img_size = 1280

# Low confidence threshold
MIN_CONFIDENCE = 0.3

# Capture frequently
INFERENCE_INTERVAL = 2
```

---

## 📈 Scalability

### Multiple Camera Streams

The system supports unlimited RTSP streams. Each stream runs in its own thread.

**Add new streams in `config.py`:**

```python
RTSP_STREAMS = [
    # ... existing streams ...
    {
        "name": "New Camera",
        "url": "rtsp://...",
        "location": {"lat": x, "lon": y},
        "region": "Location Name",
        "enabled": True,
    },
]
```

### Distributed Deployment

For large-scale deployments:

1. **Edge Devices**: Run capture service on Raspberry Pi/edge devices
2. **Central ML**: Run YOLO inference on central GPU server
3. **Cloud Database**: Use Neon/Supabase for global access
4. **Load Balancing**: Multiple ML service instances behind load balancer

---

## ✅ System Status Checklist

Before going live:

- [ ] RTSP URLs configured and tested
- [ ] Database schemas applied
- [ ] Environment variables set
- [ ] YOLO model loaded (6.23 MB yolov8n.pt)
- [ ] All Docker services running
- [ ] Frontend accessible at `/monitoring`
- [ ] Test detection appears on map
- [ ] Real-time SSE stream working
- [ ] Supabase real-time enabled
- [ ] Log monitoring setup

---

## 🎉 Ready to Deploy!

Your autonomous detection system is configured and ready!

**Start the system:**

```bash
cd backend
docker-compose up -d
```

**Watch it work:**

```bash
# Terminal 1: Watch logs
docker-compose logs -f capture-service

# Terminal 2: Watch detections
Open http://localhost:5000/monitoring
```

**Detections will:**
1. ✅ Auto-capture from RTSP streams
2. ✅ Auto-analyze with YOLO
3. ✅ Auto-save to database
4. ✅ Auto-appear on Cesium map
5. ✅ Auto-update in real-time

**No buttons. No uploads. Pure automation.** 🚀
