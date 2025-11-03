import asyncio
import logging
from typing import Dict, Optional, List
import asyncpg

logger = logging.getLogger(__name__)

class DetectionDatabase:
    """Async database client for detection_patterns table"""
    
    def __init__(self, database_url: str):
        """
        Initialize database client
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> bool:
        """Connect to database"""
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logger.info("[DB] Connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"[DB] Connection failed: {e}")
            return False
    
    async def insert_detection(self, detection: Dict) -> Optional[int]:
        """
        Insert detection into database
        
        Args:
            detection: Detection data with latitude, longitude, risk_assessment, etc.
            
        Returns:
            Detection ID or None on error
        """
        if not self.pool:
            logger.error("[DB] Not connected")
            return None
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    """
                    INSERT INTO detection_patterns (
                        latitude, longitude, detection_timestamp, detection_count,
                        source, environmental_context, risk_assessment, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                    RETURNING id
                    """,
                    detection["latitude"],
                    detection["longitude"],
                    detection.get("detection_timestamp"),
                    detection.get("detection_count", 1),
                    detection.get("source", "auto_inference"),
                    detection.get("environmental_context"),
                    detection.get("risk_assessment"),
                )
                
                logger.info(f"[DB] Inserted detection ID: {result}")
                return result
        except Exception as e:
            logger.error(f"[DB] Insert error: {e}")
            return None
    
    async def get_recent_detections(self, limit: int = 50) -> List[Dict]:
        """
        Get recent detections
        
        Args:
            limit: Number of detections to return
            
        Returns:
            List of detection records
        """
        if not self.pool:
            logger.error("[DB] Not connected")
            return []
        
        try:
            async with self.pool.acquire() as conn:
                records = await conn.fetch(
                    """
                    SELECT * FROM detection_patterns
                    ORDER BY detection_timestamp DESC
                    LIMIT $1
                    """,
                    limit,
                )
                return records
        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            return []
    
    async def get_detections_by_region(
        self,
        lat: float,
        lon: float,
        radius_km: float = 50,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get detections within region
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
            limit: Max results
            
        Returns:
            List of detection records
        """
        if not self.pool:
            logger.error("[DB] Not connected")
            return []
        
        try:
            async with self.pool.acquire() as conn:
                records = await conn.fetch(
                    """
                    SELECT * FROM detection_patterns
                    WHERE earth_distance(
                        ll_to_earth($1, $2),
                        ll_to_earth(latitude, longitude)
                    ) < $3 * 1000
                    ORDER BY detection_timestamp DESC
                    LIMIT $4
                    """,
                    lat,
                    lon,
                    radius_km,
                    limit,
                )
                return records
        except Exception as e:
            logger.error(f"[DB] Regional query error: {e}")
            return []
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.pool:
            await self.pool.close()
            logger.info("[DB] Disconnected")
