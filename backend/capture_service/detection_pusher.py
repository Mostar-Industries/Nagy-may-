import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DetectionPusher:
    """Pushes detections to database and Supabase Realtime"""
    
    def __init__(self, db_url: str, supabase_url: str, supabase_key: str):
        """
        Initialize pusher
        
        Args:
            db_url: PostgreSQL connection string
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
        """
        self.db_url = db_url
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.db_conn = None
    
    async def push_detection(
        self,
        frame_data: Dict,
        inference_result: Dict,
        risk_score: float,
    ) -> bool:
        """
        Push detection to database and Supabase
        
        Args:
            frame_data: Frame metadata (stream_name, location, timestamp)
            inference_result: YOLO inference output
            risk_score: Calculated risk score (0-1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare detection record
            detection = {
                "latitude": frame_data["location"]["lat"],
                "longitude": frame_data["location"]["lon"],
                "detection_timestamp": frame_data["timestamp"],
                "detection_count": len(inference_result.get("detections", [])),
                "source": f"rtsp_auto:{frame_data['stream_name']}",
                "environmental_context": json.dumps({
                    "stream": frame_data["stream_name"],
                    "frame_count": frame_data.get("frame_count", 0),
                }),
                "risk_assessment": json.dumps({
                    "risk_score": risk_score,
                    "confidence": inference_result.get("avg_confidence", 0),
                    "detections": inference_result.get("detections", []),
                }),
            }
            
            # TODO: Insert into PostgreSQL
            logger.info(f"[PUSHER] New detection: {detection['source']} risk={risk_score:.2f}")
            
            # TODO: Broadcast to Supabase Realtime channel
            # This will trigger frontend to auto-update
            
            return True
            
        except Exception as e:
            logger.error(f"[PUSHER] Error pushing detection: {e}")
            return False
