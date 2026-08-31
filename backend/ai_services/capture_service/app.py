import os
import sys
import logging
import asyncio
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capture_service.config import CaptureConfig
from capture_service.rtsp_watcher import RTSPWatcher
from capture_service.motion_filter import MotionDetector
from capture_service.inference_engine import InferenceEngine
from capture_service.detection_pusher import DetectionPusher

# Setup logging
logging.basicConfig(
    level=getattr(logging, CaptureConfig.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
logger.info(f"[SKYHAWK] Mock Mode: {MOCK_MODE}")

class SkyhawkCaptureService:
    """Main service orchestrating RTSP capture → inference → database"""
    
    def __init__(self):
        """Initialize capture service"""
        self.watchers: List[RTSPWatcher] = []
        self.frame_queue: Queue = Queue(maxsize=100)
        self.motion_detector = MotionDetector(threshold=CaptureConfig.MOTION_THRESHOLD)
        self.inference_engine = InferenceEngine(
            model_path=CaptureConfig.MODEL_PATH,
            conf_threshold=CaptureConfig.MIN_CONFIDENCE,
        )
        self.pusher = DetectionPusher(
            db_url=CaptureConfig.DATABASE_URL,
            supabase_url=CaptureConfig.SUPABASE_URL,
            supabase_key=CaptureConfig.SUPABASE_KEY,
        )
        self.running = False
        
    def initialize(self):
        """Initialize all components"""
        logger.info("[SKYHAWK] Initializing Capture Service")
        
        if not CaptureConfig.validate():
            logger.error("[SKYHAWK] Configuration validation failed")
            return False
        
        # Create snapshot directory
        if CaptureConfig.ENABLE_SNAPSHOTS:
            os.makedirs(CaptureConfig.SNAPSHOTS_DIR, exist_ok=True)
            logger.info(f"[SKYHAWK] Snapshots enabled: {CaptureConfig.SNAPSHOTS_DIR}")
        
        # Initialize watchers for all streams
        for stream_config in CaptureConfig.get_enabled_streams():
            watcher = RTSPWatcher(stream_config, self.frame_queue)
            self.watchers.append(watcher)
        
        logger.info(f"[SKYHAWK] Initialized {len(self.watchers)} RTSP watchers")
        return True
    
    async def _process_frames(self):
        """Process frames from queue"""
        logger.info("[SKYHAWK] Frame processor started")
        
        while self.running:
            try:
                if self.frame_queue.empty():
                    await asyncio.sleep(0.1)
                    continue
                
                frame_data = self.frame_queue.get_nowait()
                frame = frame_data["frame"]
                
                # Motion detection
                if not self.motion_detector.detect_motion(frame):
                    continue
                
                # YOLO inference
                result = self.inference_engine.predict(frame)
                if not result:
                    continue
                
                # Calculate risk score (placeholder)
                risk_score = result.get("avg_confidence", 0.5)
                
                # Push to database
                await self.pusher.push_detection(frame_data, result, risk_score)
                
            except Exception as e:
                logger.error(f"[SKYHAWK] Frame processing error: {e}")
                await asyncio.sleep(0.5)
    
    def start(self):
        """Start capture service"""
        if not self.initialize():
            logger.error("[SKYHAWK] Failed to initialize")
            return
        
        self.running = True
        
        # Start all RTSP watchers
        for watcher in self.watchers:
            watcher.start(interval=CaptureConfig.INFERENCE_INTERVAL)
        
        logger.info("[SKYHAWK] All RTSP watchers started")
        
        # Start frame processor
        try:
            asyncio.run(self._process_frames())
        except KeyboardInterrupt:
            logger.info("[SKYHAWK] Shutdown requested")
        finally:
            self.stop()
    
    def stop(self):
        """Stop capture service"""
        logger.info("[SKYHAWK] Stopping capture service")
        self.running = False
        
        for watcher in self.watchers:
            watcher.stop()
        
        logger.info("[SKYHAWK] Capture service stopped")

if __name__ == "__main__":
    service = SkyhawkCaptureService()
    service.start()
