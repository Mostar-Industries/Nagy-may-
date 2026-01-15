#!/usr/bin/env python3
"""
Skyhawk Automated Detection Pipeline
Monitors multiple sources and processes detections in real-time
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import httpx
import cv2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ML_SERVICE_URL = "http://localhost:5001"
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

# Watch folders for trap cameras
TRAP_CAMERA_FOLDERS = [
    "/data/trap_cameras/cam_001",
    "/data/trap_cameras/cam_002",
    # Add your trap camera folders
]

# IP Camera streams
IP_CAMERAS = [
    {"name": "Field_Camera_1", "url": "rtsp://admin:pass@192.168.1.101/stream", "lat": 9.082, "lon": 8.675},
    {"name": "Field_Camera_2", "url": "rtsp://admin:pass@192.168.1.102/stream", "lat": 9.083, "lon": 8.676},
]

# Drone feed
DRONE_FEED_FOLDER = "/data/drone_captures"


class DetectionPipeline:
    """Core detection pipeline"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.processing_queue = asyncio.Queue()
    
    async def detect_image(self, image_path: Path, source_id: str, location: Optional[Dict] = None) -> Dict:
        """Send image to ML service for detection"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/jpeg')}
                data = {}
                
                if location:
                    data['latitude'] = location.get('lat')
                    data['longitude'] = location.get('lon')
                
                response = await self.http_client.post(
                    f"{ML_SERVICE_URL}/detect",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    result['source_id'] = source_id
                    result['image_path'] = str(image_path)
                    result['timestamp'] = datetime.utcnow().isoformat()
                    if location:
                        result['location'] = {
                            'latitude': location.get('lat'),
                            'longitude': location.get('lon'),
                        }
                    return result
                else:
                    logger.error(f"Detection failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Detection error for {image_path}: {e}")
            return None
    
    async def store_detection(self, detection: Dict):
        """Store detection in Supabase"""
        try:
            location = detection.get('location', {}) or {}
            detections = detection.get('detections', []) or []
            detection_count = detection.get('metadata', {}).get('detection_count', len(detections))
            avg_confidence = (
                sum(d.get('confidence', 0) for d in detections) / len(detections)
                if detections else 0
            )

            payload = {
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude'),
                'detection_timestamp': detection.get('timestamp'),
                'detection_count': detection_count,
                'source': detection.get('source_id'),
                'environmental_context': {
                    'image_path': detection.get('image_path'),
                },
                'risk_assessment': {
                    'risk_score': detection.get('risk_score'),
                    'risk_level': detection.get('risk_level'),
                    'confidence': avg_confidence,
                    'detections': detections,
                },
            }

            supabase_base = SUPABASE_URL.rstrip('/')
            if not supabase_base.startswith('http'):
                supabase_base = f"https://{supabase_base}"

            response = await self.http_client.post(
                f"{supabase_base}/rest/v1/detection_patterns",
                headers={
                    'apikey': SUPABASE_KEY,
                    'Authorization': f'Bearer {SUPABASE_KEY}',
                    'Content-Type': 'application/json',
                },
                json=payload
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Stored detection: {detection.get('source_id')} - {detection_count} rodents")
                return True
            else:
                logger.error(f"Supabase insert failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Store error: {e}")
            return False
    
    async def process_image(self, image_path: Path, source_id: str, location: Optional[Dict] = None):
        """Full detection + storage pipeline"""
        logger.info(f"🔍 Processing: {image_path.name} from {source_id}")
        
        # Detect
        detection = await self.detect_image(image_path, source_id, location)
        
        if detection and detection.get('detections'):
            # Store in Supabase (triggers realtime update to map)
            await self.store_detection(detection)
        else:
            logger.info(f"No detections in {image_path.name}")


class TrapCameraHandler(FileSystemEventHandler):
    """Watches trap camera folders for new images"""
    
    def __init__(self, pipeline: DetectionPipeline, camera_id: str, location: Dict):
        self.pipeline = pipeline
        self.camera_id = camera_id
        self.location = location
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Only process images
        if not event.src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return
        
        # Queue for processing
        image_path = Path(event.src_path)
        asyncio.create_task(
            self.pipeline.process_image(image_path, self.camera_id, self.location)
        )


class IPCameraProcessor:
    """Processes IP camera streams"""
    
    def __init__(self, pipeline: DetectionPipeline):
        self.pipeline = pipeline
        self.active_streams = {}
    
    async def process_stream(self, camera: Dict):
        """Process IP camera stream with frame sampling"""
        camera_id = camera['name']
        stream_url = camera['url']
        location = {'lat': camera['lat'], 'lon': camera['lon']}
        
        logger.info(f"🎥 Starting stream: {camera_id}")
        
        cap = cv2.VideoCapture(stream_url)
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Stream ended: {camera_id}")
                    break
                
                frame_count += 1
                
                # Process every 30th frame (~1 per second at 30fps)
                if frame_count % 30 == 0:
                    # Save frame temporarily
                    temp_path = Path(f"/tmp/{camera_id}_{datetime.now().timestamp()}.jpg")
                    cv2.imwrite(str(temp_path), frame)
                    
                    # Process
                    await self.pipeline.process_image(temp_path, camera_id, location)
                    
                    # Cleanup
                    temp_path.unlink()
                
                # Prevent tight loop
                await asyncio.sleep(0.01)
                
        finally:
            cap.release()
            logger.info(f"Stream stopped: {camera_id}")


class DroneHandler(FileSystemEventHandler):
    """Watches drone capture folder"""
    
    def __init__(self, pipeline: DetectionPipeline):
        self.pipeline = pipeline
    
    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith(('.jpg', '.jpeg')):
            return
        
        # Extract GPS from EXIF if available
        image_path = Path(event.src_path)
        location = self._extract_gps(image_path)
        
        asyncio.create_task(
            self.pipeline.process_image(image_path, "DRONE", location)
        )
    
    def _extract_gps(self, image_path: Path) -> Optional[Dict]:
        """Extract GPS from image EXIF"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            img = Image.open(image_path)
            exif = img._getexif()
            
            if not exif:
                return None
            
            gps_info = {}
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_info[sub_decoded] = value[t]
            
            if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                lat = self._convert_to_degrees(gps_info['GPSLatitude'])
                lon = self._convert_to_degrees(gps_info['GPSLongitude'])
                
                if gps_info.get('GPSLatitudeRef') == 'S':
                    lat = -lat
                if gps_info.get('GPSLongitudeRef') == 'W':
                    lon = -lon
                
                return {'lat': lat, 'lon': lon}
                
        except Exception as e:
            logger.warning(f"GPS extraction failed: {e}")
        
        return None
    
    @staticmethod
    def _convert_to_degrees(value):
        """Convert GPS coordinates to degrees"""
        d, m, s = value
        return float(d) + float(m) / 60 + float(s) / 3600


async def main():
    """Start all detection services"""
    logger.info("🔥 Starting Skyhawk Automated Detection Pipeline")
    
    pipeline = DetectionPipeline()
    
    # 1. Setup trap camera watchers
    observer = Observer()
    for idx, folder in enumerate(TRAP_CAMERA_FOLDERS):
        path = Path(folder)
        if path.exists():
            camera_id = f"TRAP_CAM_{idx+1:03d}"
            # You'd pull location from config/database
            location = {'lat': 9.082 + idx*0.001, 'lon': 8.675 + idx*0.001}
            
            handler = TrapCameraHandler(pipeline, camera_id, location)
            observer.schedule(handler, str(path), recursive=False)
            logger.info(f"👁️  Watching: {folder} ({camera_id})")
        else:
            logger.warning(f"Folder not found: {folder}")
    
    observer.start()
    
    # 2. Setup drone watcher
    drone_path = Path(DRONE_FEED_FOLDER)
    if drone_path.exists():
        drone_handler = DroneHandler(pipeline)
        observer.schedule(drone_handler, str(drone_path), recursive=False)
        logger.info(f"🚁 Watching drone folder: {DRONE_FEED_FOLDER}")
    
    # 3. Start IP camera streams
    ip_processor = IPCameraProcessor(pipeline)
    stream_tasks = [
        asyncio.create_task(ip_processor.process_stream(cam))
        for cam in IP_CAMERAS
    ]
    
    logger.info(f"✅ Pipeline active - monitoring {len(TRAP_CAMERA_FOLDERS)} trap cams, {len(IP_CAMERAS)} IP streams, drone feed")
    
    try:
        # Keep running
        await asyncio.gather(*stream_tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        observer.stop()
        observer.join()


if __name__ == '__main__':
    asyncio.run(main())

