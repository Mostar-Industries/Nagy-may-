import asyncio
import logging
import json
from typing import Dict, Optional
from realtime.connection import Socket

logger = logging.getLogger(__name__)

class SupabaseRealtimeClient:
    """Client for Supabase Realtime broadcasts"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize Supabase Realtime client
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.socket: Optional[Socket] = None
        self.channel = None
    
    async def connect(self) -> bool:
        """Connect to Supabase Realtime"""
        try:
            # Extract socket URL from Supabase URL
            socket_url = self.supabase_url.replace("https://", "wss://").replace("http://", "ws://")
            socket_url = f"{socket_url}/realtime/v1?apikey={self.supabase_key}"
            
            self.socket = Socket(socket_url)
            self.socket.connect()
            
            logger.info("[SUPABASE] Connected to Realtime")
            return True
        except Exception as e:
            logger.error(f"[SUPABASE] Connection failed: {e}")
            return False
    
    async def subscribe_to_detections(self):
        """Subscribe to detection_patterns table changes"""
        try:
            if not self.socket:
                logger.error("[SUPABASE] Not connected")
                return
            
            self.channel = self.socket.channel("public:detection_patterns")
            self.channel.on("INSERT", self._on_detection_insert)
            self.channel.subscribe()
            
            logger.info("[SUPABASE] Subscribed to detection_patterns changes")
        except Exception as e:
            logger.error(f"[SUPABASE] Subscription error: {e}")
    
    def _on_detection_insert(self, payload):
        """Handle new detection insert event"""
        logger.info(f"[SUPABASE] New detection: {payload}")
    
    async def broadcast_detection(self, detection: Dict) -> bool:
        """
        Broadcast detection event to all connected clients
        
        Args:
            detection: Detection data
            
        Returns:
            True if successful
        """
        try:
            if not self.socket:
                logger.error("[SUPABASE] Not connected")
                return False
            
            self.channel.send({
                "type": "broadcast",
                "event": "new_detection",
                "payload": detection,
            })
            
            logger.debug(f"[SUPABASE] Broadcasted detection")
            return True
        except Exception as e:
            logger.error(f"[SUPABASE] Broadcast error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Supabase Realtime"""
        if self.socket:
            self.socket.disconnect()
            logger.info("[SUPABASE] Disconnected")
