# Skyhawk Automated Detection - Deployment Guide

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Detection Sources                         │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│ Trap Cams   │  IP Streams │  Drones     │  Edge Devices    │
│ (Folders)   │  (RTSP)     │  (EXIF GPS) │  (Any Source)    │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬───────────┘
       │             │             │             │
       └─────────────┴─────────────┴─────────────┘
                         │
                    ┌────▼────┐
                    │Pipeline │ auto_detection_pipeline.py
                    │ Service │ Monitors all sources 24/7
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │   ML    │ http://localhost:5001/detect
                    │ Service │ YOLOv8 Mastomys detection
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │Next.js  │ /api/detections
                    │   API   │ Stores in Supabase
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │Supabase │ detection_patterns table
                    │Realtime │ Broadcasts to frontend
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ Cesium  │ Live map with risk markers
                    │   Map   │ Auto-updates on detection
                    └─────────┘
```

## Setup Steps

### 1. Database Setup

```bash
# Run in Supabase SQL Editor
psql -f supabase_schema.sql

# Or copy/paste supabase_schema.sql contents
```

### 2. Environment Variables

```bash
# .env.local (Next.js)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Pipeline environment
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. Install Pipeline Dependencies

```bash
pip install asyncio httpx opencv-python watchdog pillow
```

### 4. Configure Sources

Edit `auto_detection_pipeline.py`:

```python
# Trap camera folders
TRAP_CAMERA_FOLDERS = [
    "/data/trap_cameras/site_alpha",
    "/data/trap_cameras/site_beta",
]

# IP cameras
IP_CAMERAS = [
    {
        "name": "Field_Cam_North", 
        "url": "rtsp://admin:pass@192.168.1.101/stream",
        "lat": 9.082,
        "lon": 8.675
    },
]

# Drone captures
DRONE_FEED_FOLDER = "/data/drone_captures"
```

### 5. Deploy Services

#### ML Service (Docker):
```bash
cd backend/ml_service
docker build -t skyhawk-ml:v2 .
docker run -d -p 5001:5001 --name ml-service skyhawk-ml:v2
```

#### Pipeline Service (systemd):
```bash
# Create service file: /etc/systemd/system/skyhawk-pipeline.service

[Unit]
Description=Skyhawk Automated Detection Pipeline
After=network.target

[Service]
Type=simple
User=skyhawk
WorkingDirectory=/opt/skyhawk
ExecStart=/usr/bin/python3 auto_detection_pipeline.py
Restart=always
RestartSec=10
Environment="SUPABASE_URL=https://your-project.supabase.co"
Environment="SUPABASE_SERVICE_ROLE_KEY=your-key"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable skyhawk-pipeline
sudo systemctl start skyhawk-pipeline
sudo systemctl status skyhawk-pipeline
```

### 6. Frontend Integration

#### Add API route:
```bash
# Copy to: app/api/detections/route.ts
cp nextjs_api_route.ts your-project/app/api/detections/route.ts
```

#### Add realtime hook:
```bash
# Copy to: hooks/useRealtimeDetections.ts
cp useRealtimeDetections.ts your-project/hooks/
```

#### Use in map component:
```typescript
import { useRealtimeDetections } from '@/hooks/useRealtimeDetections';

export function CesiumMap() {
  const [viewer, setViewer] = useState<Viewer | null>(null);
  
  // Auto-subscribe to detections
  useRealtimeDetections(viewer);
  
  return <CesiumViewer onViewerReady={setViewer} />;
}
```

## Operation

### Pipeline starts automatically and:
1. **Watches** trap camera folders for new images
2. **Streams** IP cameras (1 frame/sec)
3. **Monitors** drone capture folder with GPS extraction
4. **Detects** rodents via ML service
5. **Stores** in Supabase
6. **Broadcasts** to all connected frontends

### Map shows:
- 🔴 **Red**: High Lassa risk (M. natalensis in endemic area)
- 🟠 **Orange**: Medium risk
- 🟡 **Yellow**: Low risk
- **Auto-fly** to high-risk detections
- **Click marker** for details

## Monitoring

```bash
# Pipeline logs
journalctl -u skyhawk-pipeline -f

# ML service logs
docker logs -f ml-service

# Check recent detections
curl "http://localhost:3000/api/detections?hours=1"
```

## Troubleshooting

**No detections appearing:**
- Check ML service: `curl http://localhost:5001/health`
- Check pipeline: `systemctl status skyhawk-pipeline`
- Verify Supabase realtime is enabled: `ALTER PUBLICATION supabase_realtime ADD TABLE detection_patterns;`

**Stream issues:**
- Verify RTSP URLs are accessible
- Check network firewall rules
- Ensure opencv-python has codec support

**GPS not working:**
- Install Pillow: `pip install pillow`
- Verify drone images have EXIF GPS data

## Production Recommendations

1. **Storage**: Use S3/Cloudinary for images (not local paths)
2. **Authentication**: Add API key auth to pipeline requests
3. **Scaling**: Run multiple pipeline instances for load balancing
4. **Alerting**: Add SMS/email for high-risk detections
5. **Retention**: Archive old detections (>30 days)

---
🔥 MoStar Industries | Lassa Shield | African Sovereignty

