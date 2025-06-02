"""
MNTRK Sovereign Observatory - Neon PostgreSQL Database Integration
Historical data archive and analytics
"""

import os
from neon import neon
import logging
from typing import List, Dict, Any

logger = logging.getLogger("Neon-Database")

def get_neon_sql():
    """Get Neon SQL client instance."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    return neon(database_url)

async def query_historical_data(days: int = 365) -> List[Dict]:
    """Query historical detection data from Neon."""
    try:
        sql = get_neon_sql()
        
        query = f"""
        SELECT 
            id, latitude, longitude, detection_count,
            detection_timestamp, environmental_context,
            risk_assessment, created_at
        FROM detection_patterns 
        WHERE created_at >= NOW() - INTERVAL '{days} days'
        ORDER BY created_at DESC
        """
        
        result = sql(query)
        
        # Convert to list of dictionaries
        historical_data = []
        for row in result:
            record = {
                "id": row[0],
                "latitude": row[1],
                "longitude": row[2],
                "detection_count": row[3],
                "detection_timestamp": row[4],
                "environmental_context": row[5],
                "risk_assessment": row[6],
                "created_at": row[7]
            }
            historical_data.append(record)
        
        logger.info(f"Retrieved {len(historical_data)} historical records")
        return historical_data
        
    except Exception as e:
        logger.error(f"Failed to query historical data: {e}")
        raise

async def store_detection_archive(detection_data: Dict) -> str:
    """Store detection data in Neon archive."""
    try:
        sql = get_neon_sql()
        
        query = """
        INSERT INTO detection_patterns (
            latitude, longitude, detection_count, detection_timestamp,
            environmental_context, risk_assessment, source
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        values = (
            detection_data.get('latitude'),
            detection_data.get('longitude'),
            detection_data.get('detection_count'),
            detection_data.get('detection_timestamp'),
            detection_data.get('environmental_context'),
            detection_data.get('risk_assessment'),
            'firestore_sync'
        )
        
        result = sql(query, values)
        record_id = result[0][0]
        
        logger.info(f"Stored detection archive with ID: {record_id}")
        return record_id
        
    except Exception as e:
        logger.error(f"Failed to store detection archive: {e}")
        raise

async def get_analytics_summary() -> Dict:
    """Get analytics summary from historical data."""
    try:
        sql = get_neon_sql()
        
        # Total detections
        total_query = "SELECT COUNT(*) FROM detection_patterns"
        total_result = sql(total_query)
        total_detections = total_result[0][0]
        
        # Recent detections (last 30 days)
        recent_query = """
        SELECT COUNT(*) FROM detection_patterns 
        WHERE created_at >= NOW() - INTERVAL '30 days'
        """
        recent_result = sql(recent_query)
        recent_detections = recent_result[0][0]
        
        # Average detection count
        avg_query = "SELECT AVG(detection_count) FROM detection_patterns"
        avg_result = sql(avg_query)
        avg_detection_count = float(avg_result[0][0]) if avg_result[0][0] else 0
        
        # Geographic distribution
        geo_query = """
        SELECT 
            ROUND(latitude::numeric, 1) as lat_rounded,
            ROUND(longitude::numeric, 1) as lon_rounded,
            COUNT(*) as detection_count
        FROM detection_patterns 
        GROUP BY lat_rounded, lon_rounded
        ORDER BY detection_count DESC
        LIMIT 10
        """
        geo_result = sql(geo_query)
        
        hotspots = []
        for row in geo_result:
            hotspots.append({
                "latitude": float(row[0]),
                "longitude": float(row[1]),
                "detection_count": row[2]
            })
        
        summary = {
            "total_detections": total_detections,
            "recent_detections": recent_detections,
            "average_detection_count": round(avg_detection_count, 2),
            "detection_hotspots": hotspots,
            "data_period": "all_time",
            "last_updated": "now"
        }
        
        logger.info("Generated analytics summary")
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate analytics summary: {e}")
        raise
