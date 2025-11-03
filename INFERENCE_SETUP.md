# Mastomys Detection Inference System Setup

## Overview
Complete YOLO-based detection system with real-time updates for the Mastomys tracker.

## Architecture
```
Image Upload → YOLO Inference → Database Save → Real-time Broadcast
     ↓              ↓                 ↓               ↓
 /api/detections  Python ML      Neon + Supabase   SSE Stream
  /inference      Service         Databases         /stream
```

## Prerequisites

### 1. Database Setup
Run the initialization script:
```bash
psql $DATABASE_URL -f scripts/init-detections-table.sql
```

### 2. Python Dependencies
```bash
cd backend/ml_service
pip install ultralytics pillow numpy
```

### 3. YOLO Model
Place your trained model at:
```
backend/ml_service/models/mastomys_natalensis.pt
```
Or use the default YOLOv8 models (auto-downloaded).

### 4. Environment Variables
Add to your `.env`:
```bash
# Database (required)
DATABASE_URL=postgresql://...
POSTGRES_URL=postgresql://...

# Supabase (required for realtime)
NEXT_PUBLIC_SUPABASE_URL=https://yourproject.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Cesium (required for maps)
CESIUM_ION_TOKEN=your_token

# Optional
YOLO_MODEL_PATH=backend/ml_service/models/mastomys_natalensis.pt
```

## API Endpoints

### 1. Image Inference
**POST** `/api/detections/inference`

Request:
```json
{
  "imageBase64": "data:image/jpeg;base64,...",
  "latitude": 9.0820,
  "longitude": 8.6753,
  "source": "field_camera",
  "confThreshold": 0.5,
  "metadata": {
    "camera_id": "CAM001",
    "location_name": "Site A"
  }
}
```

Response:
```json
{
  "success": true,
  "detection": {
    "image_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z",
    "detections": [
      {
        "id": 0,
        "bbox": { "x": 100, "y": 150, "width": 200, "height": 180 },
        "confidence": 0.92,
        "class": 0,
        "class_name": "mastomys",
        "species": "Mastomys natalensis",
        "species_confidence": 0.92,
        "processing_time_ms": 245
      }
    ],
    "processing_time_ms": 1234,
    "saved_to": {
      "neon": true,
      "supabase": true
    }
  }
}
```

### 2. Real-time Stream
**GET** `/api/detections/stream`

Server-Sent Events stream for live detection updates.

JavaScript client example:
```javascript
const eventSource = new EventSource('/api/detections/stream')

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'detection') {
    console.log('New detection:', data.data)
    // Update UI
  }
}
```

### 3. Get Detections
**GET** `/api/detections`

Retrieve historical detections (existing endpoint).

## Frontend Integration

### Using the Realtime Hook
```typescript
import { useRealtimeDetections } from '@/hooks/use-realtime-detections'

function DetectionMonitor() {
  const { detections, isConnected, lastUpdate } = useRealtimeDetections()
  
  return (
    <div>
      <p>Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      <p>Detections: {detections.length}</p>
      <p>Last update: {lastUpdate}</p>
    </div>
  )
}
```

### Image Upload Component
```typescript
async function uploadImage(file: File) {
  const reader = new FileReader()
  reader.onload = async (e) => {
    const imageBase64 = e.target?.result as string
    
    const response = await fetch('/api/detections/inference', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        imageBase64,
        latitude: 9.0820,
        longitude: 8.6753,
        source: 'web_upload'
      })
    })
    
    const result = await response.json()
    console.log('Detection result:', result)
  }
  reader.readAsDataURL(file)
}
```

## Testing

### 1. Test Python Inference
```bash
cd backend/ml_service
python inference_api.py --image test_image.jpg --conf 0.5 --output json
```

### 2. Test API Endpoint
```bash
# Upload a test image
curl -X POST http://localhost:5000/api/detections/inference \
  -H "Content-Type: application/json" \
  -d '{"imageBase64":"data:image/jpeg;base64,/9j/4AAQ...","source":"test"}'
```

### 3. Test SSE Stream
```bash
curl -N http://localhost:5000/api/detections/stream
```

## File Structure
```
├── app/api/detections/
│   ├── route.ts              # GET/POST detections
│   ├── inference/
│   │   └── route.ts          # Image inference endpoint
│   └── stream/
│       └── route.ts          # SSE stream
├── backend/ml_service/
│   ├── models/
│   │   ├── yolo_detector.py  # YOLO wrapper class
│   │   └── *.pt              # Model weights
│   └── inference_api.py      # CLI inference script
├── lib/
│   ├── yolo/
│   │   └── inference.ts      # TypeScript inference client
│   └── db/
│       └── detection-writer.ts # Database persistence
├── hooks/
│   └── use-realtime-detections.ts # Realtime hook
└── scripts/
    └── init-detections-table.sql  # Database schema
```

## Troubleshooting

### Issue: Python process fails
- Check Python path: `which python3`
- Install dependencies: `pip install ultralytics pillow`
- Verify model exists at specified path

### Issue: No detections saved
- Check DATABASE_URL is correct
- Run database migration script
- Check logs for SQL errors

### Issue: SSE not working
- Verify NEXT_PUBLIC_SUPABASE_URL is set
- Check Supabase realtime is enabled
- Open browser devtools Network tab

### Issue: Images too large
- Max size is 10MB (configurable in route.ts)
- Compress images before upload
- Use appropriate JPEG quality

## Performance Optimization

1. **GPU Acceleration**: Set `device='cuda'` in Python if GPU available
2. **Model Size**: Use smaller models (yolov8n) for faster inference
3. **Batch Processing**: Process multiple images in one request
4. **Caching**: Cache model in memory (already implemented)
5. **CDN**: Store processed images in CDN (S3/Cloudflare)

## Security Considerations

1. Rate limiting on `/inference` endpoint (recommended)
2. Authentication required in production
3. Validate image format and size
4. Sanitize metadata inputs
5. Use environment secrets for API keys

## Next Steps

- [ ] Add image storage (S3/Cloudflare R2)
- [ ] Implement batch inference
- [ ] Add detection confidence thresholds
- [ ] Create admin dashboard
- [ ] Add detection annotations
- [ ] Export detection data (CSV/JSON)
- [ ] Mobile app integration
- [ ] WebSocket alternative to SSE
