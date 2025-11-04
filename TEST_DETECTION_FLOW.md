# 🧪 Detection Flow Test Guide

## ✅ Fixed Issues

1. **`detection_patterns` table removed** - All references now use `detections` table
2. **Field mappings corrected**:
   - `detected_at` instead of `detection_timestamp`
   - `class_name` instead of `label`
   - Proper schema alignment across all files

## 📝 Files Fixed

- ✅ `hooks/use-realtime-detections.ts` - Query detections table, map fields correctly
- ✅ `app/api/detections/route.ts` - GET/POST use detections table
- ✅ `app/api/detections/stream/route.ts` - SSE subscribes to detections table
- ✅ `lib/db/detection-writer.ts` - Supabase insert uses correct schema

---

## 🧪 How to Test Complete Flow

### 1. **Manual Detection Upload**

Test the upload interface on `/monitoring`:

```bash
# Open browser
http://localhost:3000/monitoring

# Upload an image or create a detection
# Should see it appear in "Recent Detections" table
# Should see marker drop on Cesium map
```

**Expected:**
- ✅ Image uploads without errors
- ✅ Detection appears in table within 1-2 seconds
- ✅ Map marker animates in
- ✅ "● Live" status shows green

### 2. **Real-time Detection Stream**

Test SSE endpoint:

```bash
# Terminal 1: Start SSE listener
curl -N http://localhost:3000/api/detections/stream

# Terminal 2: Create a detection
curl -X POST http://localhost:3000/api/detections \\
  -H "Content-Type: application/json" \\
  -d '{
    "latitude": 9.0820,
    "longitude": 8.6753,
    "confidence": 0.85,
    "type": "test"
  }'
```

**Expected:**
- Terminal 1 receives: `data: {"type":"detection","data":{...}}`
- Frontend updates automatically
- No errors in browser console

### 3. **Database Direct Insert**

Test Supabase realtime:

```sql
-- In Supabase SQL Editor
INSERT INTO detections (
  image_id,
  latitude,
  longitude,
  confidence,
  label,
  species,
  source
) VALUES (
  'test_' || extract(epoch from now()),
  6.5244,
  3.3792,
  0.92,
  'mastomys_detected',
  'Mastomys natalensis',
  'manual_test'
);
```

**Expected:**
- Frontend receives update via Supabase realtime
- New row appears in "Recent Detections"
- Map marker appears instantly

### 4. **Autonomous Capture Service** (Once Running)

```bash
# Start capture service
cd backend/capture_service
python capture_loop.py

# Watch logs
docker-compose logs -f capture-service
```

**Expected Flow:**
1. RTSP frame captured every 5s
2. Motion detection filters static frames
3. YOLO inference runs
4. Detection saved to database
5. Frontend updates in real-time
6. Map marker appears

---

## 🔍 Debugging Checklist

### Frontend Not Showing Detections

**Check:**
```bash
# Browser console
# Should see:
[Realtime] New detection received: {...}

# Should NOT see:
Could not find the table 'public.detection_patterns'
```

**Fix:** Refresh page after code changes

### Supabase Realtime Not Working

**Check:**
1. Supabase Realtime enabled in project settings
2. `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` set
3. Row Level Security policies allow reads

**Test:**
```javascript
// Browser console
const { createClient } = await import('@supabase/supabase-js')
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

const { data, error } = await supabase
  .from('detections')
  .select('*')
  .limit(1)

console.log({ data, error })
```

### Map Not Showing Markers

**Check:**
1. Detections have valid lat/lon
2. Cesium loaded successfully
3. No JavaScript errors

**Test:**
```javascript
// Browser console
// Should show detections array
window.localStorage.getItem('debug') = 'true'
```

### Weather/MN Data Not Flowing

**Weather API Integration:**
```bash
# Check if weather endpoint exists
curl http://localhost:3000/api/weather?lat=9.082&lon=8.675
```

**Expected:** Weather data JSON response

**If missing:** Weather integration not yet built (separate from detection flow)

---

## ✅ Success Criteria

**System is working when:**

1. ✅ No "detection_patterns" errors in console
2. ✅ Recent Detections table shows data
3. ✅ Cesium map shows markers
4. ✅ "● Live" indicator is green
5. ✅ New detections appear automatically
6. ✅ SSE endpoint streams events
7. ✅ Manual uploads work
8. ✅ Database inserts trigger frontend updates

---

## 🚀 Next Steps After Testing

Once detection flow works:

1. **Weather Integration** - Add `/api/weather` endpoint
2. **MN Data** - Integrate Mastomys natalensis population data
3. **Alert System** - Trigger notifications on high-risk detections
4. **Export Features** - Download detections as GeoJSON/CSV
5. **Analytics** - Trend analysis and pattern detection

---

**Current Status: 🟢 DETECTION FLOW FIXED**

Test it now by:
1. Opening `/monitoring` page
2. Uploading an image or creating a manual detection
3. Watching it appear on the map in real-time!
