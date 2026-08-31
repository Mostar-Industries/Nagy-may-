import cv2
import logging
import asyncio
import time
from typing import Optional, Dict
from datetime import datetime
import threading
from queue import Queue

logger = logging.getLogger(__name__)

class RTSPWatcher:
    """Watches RTSP streams and extracts frames for processing"""
    
    def __init__(self, stream_config: Dict, frame_queue: Queue):
        """
        Initialize RTSP watcher
        
        Args:
            stream_config: Stream configuration dict with url, name, location
            frame_queue: Queue to push extracted frames
        """
        self.stream_url = stream_config["url"]
        self.stream_name = stream_config["name"]
        self.location = stream_config["location"]
        self.frame_queue = frame_queue
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.thread = None
        self.last_frame = None
        self.frame_count = 0
        self.connection_attempts = 0
        self.max_retries = 3
        
    def connect(self) -> bool:
        """Connect to RTSP stream"""
        try:
            logger.info(f"[RTSP] Connecting to {self.stream_name} ({self.stream_url})")
            self.cap = cv2.VideoCapture(self.stream_url)
            
            # Set timeout
            self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            
            # Verify connection
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Cannot read frames from stream")
            
            self.last_frame = frame
            self.connection_attempts = 0
            logger.info(f"[RTSP] Connected to {self.stream_name}")
            return True
            
        except Exception as e:
            logger.error(f"[RTSP] Failed to connect to {self.stream_name}: {e}")
            self.connection_attempts += 1
            if self.cap:
                self.cap.release()
                self.cap = None
            return False
    
    def _watch_loop(self, interval: int):
        """Main watch loop - runs in separate thread"""
        while self.running:
            try:
                if not self.cap:
                    if self.connection_attempts < self.max_retries:
                        time.sleep(5)
                        self.connect()
                    continue
                
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning(f"[RTSP] Lost connection to {self.stream_name}")
                    self.cap.release()
                    self.cap = None
                    continue
                
                self.last_frame = frame
                self.frame_count += 1
                
                # Push frame to queue for processing
                frame_data = {
                    "stream_name": self.stream_name,
                    "location": self.location,
                    "frame": frame,
                    "timestamp": datetime.utcnow().isoformat(),
                    "frame_count": self.frame_count,
                }
                
                self.frame_queue.put(frame_data, block=False)
                
                # Sleep to maintain interval
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"[RTSP] Error in watch loop for {self.stream_name}: {e}")
                time.sleep(2)
    
    def start(self, interval: int = 5):
        """Start watching stream"""
        if self.running:
            logger.warning(f"[RTSP] {self.stream_name} already running")
            return
        
        if not self.connect():
            logger.error(f"[RTSP] Failed to start {self.stream_name}")
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._watch_loop,
            args=(interval,),
            daemon=True,
        )
        self.thread.start()
        logger.info(f"[RTSP] Started watching {self.stream_name}")
    
    def stop(self):
        """Stop watching stream"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.cap:
            self.cap.release()
        logger.info(f"[RTSP] Stopped watching {self.stream_name}")
    
    def get_last_frame(self):
        """Get most recent frame"""
        return self.last_frame
