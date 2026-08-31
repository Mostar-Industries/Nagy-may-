import os
from typing import Dict, List

class CaptureConfig:
    """Configuration for RTSP capture service"""
    
    # RTSP stream sources
    RTSP_STREAMS: List[Dict] = [
        {
            "name": "Wildlife Kenya Live",
            "url": "rtsp://example.com/wildlife_kenya",
            "location": {"lat": -1.286389, "lon": 36.817223},
            "region": "Kenya - East Africa",
            "enabled": True,
        },
        {
            "name": "Lagos Traffic Cam",
            "url": "rtsp://example.com/lagos_traffic",
            "location": {"lat": 6.5244, "lon": 3.3792},
            "region": "Nigeria - Lagos",
            "enabled": True,
        },
        {
            "name": "Ibadan Botany Lab Feed",
            "url": "rtsp://example.com/ibadan_lab",
            "location": {"lat": 7.3775, "lon": 3.9470},
            "region": "Nigeria - Ibadan",
            "enabled": True,
        },
    ]
    
    # Inference settings
    INFERENCE_INTERVAL: int = int(os.getenv("INFERENCE_INTERVAL", "5"))  # seconds
    MOTION_THRESHOLD: float = float(os.getenv("MOTION_THRESHOLD", "0.1"))
    MIN_CONFIDENCE: float = float(os.getenv("MIN_CONFIDENCE", "0.5"))
    
    # Inference Engine
    MODEL_PATH: str = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "yolo11n.pt"))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_SNAPSHOTS: bool = os.getenv("ENABLE_SNAPSHOTS", "true").lower() == "true"
    SNAPSHOTS_DIR: str = os.getenv("SNAPSHOTS_DIR", "/tmp/snapshots")
    
    @classmethod
    def get_enabled_streams(cls) -> List[Dict]:
        """Return only enabled RTSP streams"""
        return [s for s in cls.RTSP_STREAMS if s.get("enabled", True)]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        if not cls.DATABASE_URL:
            print("[WARNING] DATABASE_URL not set - detections won't persist")
            return False
        if not os.path.exists(cls.MODEL_PATH):
            print(f"[ERROR] Model not found at {cls.MODEL_PATH}")
            return False
        return True
