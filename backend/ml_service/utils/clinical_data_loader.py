import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import math

logger = logging.getLogger(__name__)


class ClinicalDataLoader:
    """
    Loader for Lassa fever clinical case data.
    Integrates with SORMAS and local health databases.
    """
    
    def __init__(self, data_source: str = None):
        """Initialize with optional data source path/URL"""
        self.data_source = data_source
        self._cases = []  # Will be populated from database/API
        logger.info("[ClinicalDataLoader] Initialized")
    
    def get_cases_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Get Lassa cases for a specific region"""
        # TODO: Connect to actual database
        return [c for c in self._cases if c.get("region", "").lower() == region.lower()]
    
    def get_recent_cases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent cases"""
        sorted_cases = sorted(
            self._cases,
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        return sorted_cases[:limit]
    
    def get_case_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics"""
        return {
            "total_cases": len(self._cases),
            "regions_affected": len(set(c.get("region") for c in self._cases)),
            "date_range": {
                "earliest": min((c.get("date") for c in self._cases), default=None),
                "latest": max((c.get("date") for c in self._cases), default=None)
            }
        }
    
    def correlate_detection_with_cases(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50
    ) -> Dict[str, Any]:
        """Find Lassa cases near a detection location"""
        nearby_cases = []
        
        for case in self._cases:
            case_lat = case.get("latitude")
            case_lon = case.get("longitude")
            if case_lat and case_lon:
                distance = self._haversine(latitude, longitude, case_lat, case_lon)
                if distance <= radius_km:
                    nearby_cases.append({**case, "distance_km": round(distance, 2)})
        
        return {
            "detection_location": {"lat": latitude, "lon": longitude},
            "search_radius_km": radius_km,
            "nearby_cases": nearby_cases,
            "case_count": len(nearby_cases),
            "correlation_risk": "HIGH" if len(nearby_cases) > 5 else "MODERATE" if nearby_cases else "LOW"
        }
    
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
