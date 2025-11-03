# 🎯 Mastomys Detection System - Quick Reference

## 🚀 What You Have Now

A complete, production-ready AI detection system for Mastomys rodent tracking with:

✅ **YOLO AI Inference** - Real-time image analysis  
✅ **Dual Database** - Neon (primary) + Supabase (realtime)  
✅ **Live Updates** - Server-Sent Events streaming  
✅ **Web Upload UI** - Drag-and-drop + camera capture  
✅ **REST API** - Full detection endpoints  
✅ **Geospatial** - GPS tagging and mapping  

## ⚡ Quick Start (5 Minutes)

### 1. Setup Database
```bash
psql $DATABASE_URL -f scripts/init-detections-table.sql
```

### 2. Setup Python ML
```powershell
# Windows
.\scripts\setup-inference.ps1

# Or Linux/Mac
bash scripts/setup-inference.sh
```

### 3. Start Server
```bash
pnpm dev
```

### 4. Test It
- **Web UI**: http://localhost:5000/monitoring
- **Upload Image**: Use the "Upload Image for Detection" card
- **See Results**: Real-time detection results appear instantly

## 📡 API Endpoints

### Upload Image for Detection
```bash
POST /api/detections/inference
Content-Type: application/json

{
  "imageBase64": "data:image/jpeg;base64,...",
  "latitude": 9.0820,
  "longitude": 8.6753,
  "confThreshold": 0.5
}
```

### Get Real-time Stream
```bash
GET /api/detections/stream
Accept: text/event-stream
```

### Get Detection History
```bash
GET /api/detections
```

## 📁 Key Files Created

| File | Purpose |
|------|---------|
| `app/api/detections/inference/route.ts` | Image inference endpoint |
| `app/api/detections/stream/route.ts` | SSE realtime stream |
| `lib/yolo/inference.ts` | YOLO TypeScript client |
| `lib/db/detection-writer.ts` | Database persistence |
| `components/detection-uploader.tsx` | Upload UI component |
| `backend/ml_service/inference_api.py` | Python CLI inference |
| `scripts/init-detections-table.sql` | Database schema |
| `INFERENCE_SETUP.md` | Full documentation |
| `IMPLEMENTATION_COMPLETE.md` | Complete feature list |

## 🧪 Test Commands

```bash
# Test Python inference directly
cd backend/ml_service
python inference_api.py --image test.jpg --conf 0.5

# Test API endpoint
curl -X POST http://localhost:5000/api/detections/inference \
  -H "Content-Type: application/json" \
  -d '{"imageBase64":"data:image/..."}'

# Test SSE stream
curl -N http://localhost:5000/api/detections/stream

# Run automated test suite
npx tsx scripts/test-inference.ts
```

## 🗺️ System Architecture

```
User Upload → Next.js API → Python YOLO → Database → Frontend Update
     ↓             ↓             ↓           ↓            ↓
   Image     /inference    ML Model    Neon+Supabase   Real-time UI
```

## 📊 What Gets Detected

- **Mastomys natalensis** (primary target)
- **Mastomys coucha** (related species)
- **Other rodents** (generic detection)

Each detection includes:
- Bounding box coordinates
- Confidence score (0-1)
- Species classification
- Processing time
- GPS coordinates (if available)

## 🎨 UI Features

The `/monitoring` page now has:
- 📤 **Upload Card**: Drag-and-drop or camera capture
- 🖼️ **Image Preview**: See uploaded image
- 🎯 **Detection Results**: Species, confidence, bounding boxes
- ⚡ **Real-time Updates**: New detections appear automatically
- 📊 **Statistics**: Live detection counts and metrics

## 🔧 Configuration

Required in `.env`:
```bash
DATABASE_URL=postgresql://...
POSTGRES_URL=postgresql://...
CESIUM_ION_TOKEN=your_token
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key
```

Optional:
```bash
YOLO_MODEL_PATH=backend/ml_service/models/mastomys_natalensis.pt
```

## 🐛 Troubleshooting

**No detections appearing?**
- Check database is initialized: `psql $DATABASE_URL -c "SELECT COUNT(*) FROM detections;"`
- Verify Supabase URL is set correctly
- Check browser console for errors

**Python not found?**
- Install Python 3.8+
- Run setup script: `.\scripts\setup-inference.ps1`

**Slow inference?**
- Use GPU if available (edit `yolo_detector.py` to use `device='cuda'`)
- Compress images before upload
- Use smaller YOLO model (yolov8n vs yolov8x)

## 📚 Documentation

- **Full Setup Guide**: `INFERENCE_SETUP.md`
- **Implementation Details**: `IMPLEMENTATION_COMPLETE.md`
- **API Reference**: See endpoints section above
- **Database Schema**: `scripts/init-detections-table.sql`

## 🎉 You're Ready!

Your detection system is fully operational. Upload an image and watch the AI identify Mastomys in real-time!

**Start here**: http://localhost:5000/monitoring

---

**Need help?** Check the troubleshooting section or review the full documentation in `INFERENCE_SETUP.md`.
