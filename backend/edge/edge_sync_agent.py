"""
MNTRK Sovereign Observatory - Edge Sync Agent
Synchronizes field data from edge devices to central systems
"""

import asyncio
import logging
from datetime import datetime
import json
import os
from typing import Dict, List, Any
import aiohttp
from shared.database import create_detection_pattern, get_db

logger = logging.getLogger("Edge-Sync")

class EdgeSyncAgent:
    """
    Edge synchronization agent for field devices.
    Handles data collection, preprocessing, and sync to central systems.
    """
    
    def __init__(self):
        self.device_id = os.getenv('EDGE_DEVICE_ID', 'edge_device_001')
        self.sync_interval = int(os.getenv('SYNC_INTERVAL', '300'))  # 5 minutes default
        self.central_api_url = os.getenv('CENTRAL_API_URL', 'http://localhost:8080')
        self.offline_buffer = []
        self.is_running = False
        
    async def start_sync_service(self):
        """Start the edge sync service."""
        logger.info(f"🔄 Starting Edge Sync Agent - Device: {self.device_id}")
        self.is_running = True
        
        while self.is_running:
            try:
                # Collect local data
                local_data = await self._collect_local_data()
                
                # Process and validate data
                processed_data = await self._process_field_data(local_data)
                
                # Attempt sync to central system
                sync_result = await self._sync_to_central(processed_data)
                
                if sync_result['success']:
                    logger.info(f"✅ Synced {len(processed_data)} records to central system")
                    # Clear offline buffer on successful sync
                    self.offline_buffer.clear()
                else:
                    # Store in offline buffer
                    self.offline_buffer.extend(processed_data)
                    logger.warning(f"⚠️ Sync failed, buffered {len(processed_data)} records")
                
                # Wait for next sync interval
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Sync cycle failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _collect_local_data(self) -> List[Dict]:
        """Collect data from local sensors and cameras."""
        try:
            local_data = []
            
            # Simulate camera detection data
            camera_data = await self._get_camera_detections()
            local_data.extend(camera_data)
            
            # Simulate environmental sensor data
            sensor_data = await self._get_sensor_readings()
            local_data.extend(sensor_data)
            
            # Add any buffered offline data
            if self.offline_buffer:
                local_data.extend(self.offline_buffer)
                logger.info(f"📦 Including {len(self.offline_buffer)} buffered records")
            
            return local_data
            
        except Exception as e:
            logger.error(f"Local data collection failed: {e}")
            return []
    
    async def _get_camera_detections(self) -> List[Dict]:
        """Get detection data from field cameras."""
        # Simulate camera detection data
        # In production, this would interface with actual camera systems
        
        detections = []
        
        # Simulate 1-3 detections per sync cycle
        import random
        detection_count = random.randint(0, 3)
        
        for i in range(detection_count):
            detection = {
                "detection_type": "camera",
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "latitude": random.uniform(8.0, 12.0),  # Sierra Leone region
                "longitude": random.uniform(-13.0, -10.0),
                "detection_count": random.randint(1, 8),
                "confidence_score": random.uniform(0.7, 0.95),
                "image_path": f"/data/images/detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.jpg",
                "species": "mastomys_natalensis"
            }
            detections.append(detection)
        
        return detections
    
    async def _get_sensor_readings(self) -> List[Dict]:
        """Get environmental sensor readings."""
        # Simulate environmental sensor data
        # In production, this would interface with actual sensors
        
        import random
        
        sensor_reading = {
            "reading_type": "environmental",
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "latitude": random.uniform(8.0, 12.0),
            "longitude": random.uniform(-13.0, -10.0),
            "temperature": round(random.uniform(22, 35), 1),
            "humidity": round(random.uniform(60, 95), 1),
            "rainfall": round(random.uniform(0, 50), 1),
            "vegetation_index": round(random.uniform(0.3, 0.8), 3),
            "soil_moisture": round(random.uniform(20, 80), 1)
        }
        
        return [sensor_reading]
    
    async def _process_field_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Process and validate field data."""
        processed_data = []
        
        for record in raw_data:
            try:
                # Validate required fields
                if not self._validate_record(record):
                    logger.warning(f"Invalid record skipped: {record}")
                    continue
                
                # Enrich with metadata
                enriched_record = await self._enrich_record(record)
                
                # Add processing timestamp
                enriched_record['processed_at'] = datetime.now().isoformat()
                enriched_record['edge_device'] = self.device_id
                
                processed_data.append(enriched_record)
                
            except Exception as e:
                logger.error(f"Record processing failed: {e}")
                continue
        
        logger.info(f"📊 Processed {len(processed_data)} valid records")
        return processed_data
    
    def _validate_record(self, record: Dict) -> bool:
        """Validate field data record."""
        required_fields = ['timestamp', 'latitude', 'longitude', 'device_id']
        
        for field in required_fields:
            if field not in record:
                return False
        
        # Validate coordinate ranges
        lat = record.get('latitude', 0)
        lon = record.get('longitude', 0)
        
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return False
        
        return True
    
    async def _enrich_record(self, record: Dict) -> Dict:
        """Enrich record with additional metadata."""
        enriched = record.copy()
        
        # Add geographic region
        lat = record.get('latitude', 0)
        lon = record.get('longitude', 0)
        
        if 8 <= lat <= 12 and -13 <= lon <= -10:
            enriched['region'] = 'sierra_leone'
        elif 6 <= lat <= 10 and -12 <= lon <= -8:
            enriched['region'] = 'guinea'
        else:
            enriched['region'] = 'west_africa'
        
        # Add season based on timestamp
        try:
            timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
            month = timestamp.month
            
            if month in [12, 1, 2, 3]:
                enriched['season'] = 'dry'
            elif month in [6, 7, 8, 9]:
                enriched['season'] = 'wet'
            else:
                enriched['season'] = 'transition'
        except:
            enriched['season'] = 'unknown'
        
        # Add data quality score
        quality_score = 1.0
        
        if 'confidence_score' in record:
            quality_score *= record['confidence_score']
        
        if record.get('detection_type') == 'camera':
            quality_score *= 0.9  # Camera data slightly less certain
        
        enriched['data_quality_score'] = round(quality_score, 3)
        
        return enriched
    
    async def _sync_to_central(self, data: List[Dict]) -> Dict:
        """Sync processed data to central system."""
        try:
            if not data:
                return {"success": True, "message": "No data to sync"}
            
            # Prepare sync payload
            sync_payload = {
                "device_id": self.device_id,
                "sync_timestamp": datetime.now().isoformat(),
                "data_count": len(data),
                "data": data
            }
            
            # Attempt HTTP sync to central API
            async with aiohttp.ClientSession() as session:
                url = f"{self.central_api_url}/api/edge/sync"
                
                async with session.post(
                    url,
                    json=sync_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return {"success": True, "response": result}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
            
        except aiohttp.ClientError as e:
            logger.error(f"Network sync failed: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_sync_service(self):
        """Stop the edge sync service."""
        logger.info("🛑 Stopping Edge Sync Agent")
        self.is_running = False
    
    async def get_status(self) -> Dict:
        """Get edge sync agent status."""
        return {
            "device_id": self.device_id,
            "is_running": self.is_running,
            "sync_interval": self.sync_interval,
            "central_api_url": self.central_api_url,
            "offline_buffer_size": len(self.offline_buffer),
            "last_sync": datetime.now().isoformat()
        }

# Global edge sync agent
edge_sync_agent = EdgeSyncAgent()

async def start_edge_sync():
    """Start edge sync service."""
    await edge_sync_agent.start_sync_service()

async def stop_edge_sync():
    """Stop edge sync service."""
    await edge_sync_agent.stop_sync_service()
