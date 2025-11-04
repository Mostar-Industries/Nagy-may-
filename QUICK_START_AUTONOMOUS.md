# ⚡ Quick Start - Autonomous Detection

**Zero manual uploads. Pure automation.**

---

## 🚀 Start in 3 Steps

### Step 1: Configure RTSP Streams

Edit `backend/capture_service/config.py`:

```python
RTSP_STREAMS = [
    {
        "name": "Your Camera Name",
        "url": "rtsp://username:password@camera-ip:554/stream",
        "location": {"lat": YOUR_LAT, "lon": YOUR_LON},
        "region": "Your Location",
        "enabled": True,
    },
]
```

### Step 2: Set Environment Variables

Create `backend/.env`:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-key
```

### Step 3: Start System

**Windows:**
```cmd
start_autonomous.bat
```

**Linux/Mac:**
```bash
chmod +x start_autonomous.sh
./start_autonomous.sh
```

---

## ✅ What Happens

1. **RTSP streams connect** automatically
2. **Frames capture** every 5 seconds
3. **YOLO analyzes** each frame
4. **Detections save** to database
5. **Map updates** in real-time

**No clicks. No uploads. Just works.**

---

## 🔍 Monitor Status

**View Logs:**
```bash
cd backend
docker-compose logs -f capture-service
```

**Check Health:**
```bash
curl http://localhost:5001/health
```

**View Detections:**
Open: `http://localhost:5000/monitoring`

---

## 🧪 Test Before Starting

Run configuration test:

```bash
cd backend/capture_service
python test_capture.py
```

This validates:
- ✅ Environment variables
- ✅ RTSP URL formats
- ✅ ML service connectivity
- ✅ Database connection

---

## 🛠️ Troubleshooting

**Problem:** RTSP won't connect

**Fix:**
1. Test URL in VLC: `vlc rtsp://your-url`
2. Check camera is online: `ping camera-ip`
3. Verify credentials are correct
4. Check firewall allows port 554

**Problem:** No detections appearing

**Fix:**
1. Lower confidence: `MIN_CONFIDENCE=0.3` in .env
2. Check motion filter: `MOTION_THRESHOLD=0.0` to disable
3. Verify ML service is running: `docker-compose ps ml-service`

**Problem:** Service crashes

**Fix:**
1. Check logs: `docker-compose logs capture-service`
2. Verify all required env vars are set
3. Test configuration: `python test_capture.py`

---

## 📊 Expected Output

```
[INFO] SKYHAWK AUTONOMOUS DETECTION SYSTEM
[INFO] Mode: FULLY AUTOMATED
[RTSP] Connected to Field Camera 1
[RTSP] Connected to Border Monitor
[INFO] All RTSP watchers started
[MOTION] Motion detected in Field Camera 1
[YOLO] Running inference...
[YOLO] Detected 2 objects (0.87, 0.72 confidence)
[DB] Saved detection to database
[SSE] Pushed to real-time stream
```

---

## 🎯 Next Steps

Once running:

1. **Open Map**: `http://localhost:5000/monitoring`
2. **Watch Detections**: Appear automatically
3. **Monitor Logs**: `docker-compose logs -f`
4. **Add Streams**: Edit `config.py` and restart

---

**System Status: 🟢 READY**

Your autonomous detection system is configured!

Start it now:
- Windows: `start_autonomous.bat`
- Linux/Mac: `./start_autonomous.sh`

Detections will flow automatically from camera to map! 🚀
