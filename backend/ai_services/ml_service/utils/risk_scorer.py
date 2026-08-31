import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskScorer:
    """
    Lassa fever risk scoring based on Mastomys natalensis detections.
    
    Risk factors:
    - Species identification (Mastomys = highest risk)
    - Detection confidence
    - Number of detections
    - Proximity clustering
    """
    
    # Risk weights
    SPECIES_RISK = {
        "Mastomys natalensis": 1.0,    # Primary Lassa reservoir
        "Mastomys coucha": 0.7,         # Secondary reservoir
        "Rattus rattus": 0.3,           # Low risk
        "Rattus norvegicus": 0.2,       # Very low risk
        "Other rodent": 0.1,            # Minimal risk
        "Unknown": 0.05
    }
    
    # Detection count multipliers
    COUNT_MULTIPLIERS = {
        1: 0.5,      # Single detection - possible
        2: 0.7,      # Two detections - likely
        3: 0.85,     # Three - confirmed presence
        4: 0.95,     # Four+ - established population
    }
    
    def __init__(self):
        logger.info("[RiskScorer] Initialized Lassa risk scoring engine")
    
    def score_detections(self, detections: List[Dict[str, Any]]) -> float:
        """
        Calculate aggregate Lassa fever risk score from detections.
        
        Args:
            detections: List of detection dicts from YOLO
        
        Returns:
            Risk score between 0.0 and 1.0
        """
        if not detections:
            return 0.0
        
        # Filter valid detections
        valid_detections = [d for d in detections if d.get("confidence", 0) > 0.3]
        
        if not valid_detections:
            return 0.0
        
        # Calculate weighted species risk
        species_scores = []
        for det in valid_detections:
            species = det.get("species", "Unknown")
            confidence = det.get("confidence", 0.5)
            species_weight = self.SPECIES_RISK.get(species, 0.05)
            
            # Weighted by detection confidence
            species_scores.append(species_weight * confidence)
        
        # Average species risk
        avg_species_risk = sum(species_scores) / len(species_scores)
        
        # Count multiplier (more detections = higher confidence in presence)
        count = len(valid_detections)
        if count >= 4:
            count_mult = 0.95
        else:
            count_mult = self.COUNT_MULTIPLIERS.get(count, 0.5)
        
        # Check for Mastomys specifically (primary concern)
        mastomys_present = any(
            "mastomys" in d.get("species", "").lower() or
            d.get("is_primary_reservoir", False)
            for d in valid_detections
        )
        
        # Mastomys bonus (if detected, minimum risk floor)
        mastomys_bonus = 0.3 if mastomys_present else 0.0
        
        # High confidence detection bonus
        high_conf_count = sum(1 for d in valid_detections if d.get("confidence", 0) > 0.8)
        confidence_bonus = min(high_conf_count * 0.05, 0.15)
        
        # Calculate final risk
        base_risk = avg_species_risk * count_mult
        final_risk = min(base_risk + mastomys_bonus + confidence_bonus, 1.0)
        
        logger.info(f"[RiskScorer] Score: {final_risk:.3f} "
                   f"(species={avg_species_risk:.2f}, count={count}, mastomys={mastomys_present})")
        
        return round(final_risk, 4)
    
    def score_with_context(
        self,
        detections: List[Dict[str, Any]],
        latitude: float = None,
        longitude: float = None,
        region: str = None,
        season: str = None
    ) -> Dict[str, Any]:
        """
        Enhanced risk scoring with geographic and seasonal context.
        
        Returns detailed breakdown of risk factors.
        """
        base_score = self.score_detections(detections)
        
        # Geographic risk zones (Lassa endemic regions)
        endemic_regions = {
            "edo": 0.15, "ondo": 0.15, "ebonyi": 0.12, "bauchi": 0.10,
            "plateau": 0.10, "taraba": 0.08, "nasarawa": 0.08,
            "benue": 0.07, "kogi": 0.06
        }
        
        geo_bonus = 0.0
        if region:
            region_lower = region.lower()
            for endemic, bonus in endemic_regions.items():
                if endemic in region_lower:
                    geo_bonus = bonus
                    break
        
        # Seasonal risk (dry season = higher risk)
        seasonal_bonus = 0.0
        if season:
            season_lower = season.lower()
            if season_lower in ["dry", "harmattan"]:
                seasonal_bonus = 0.1
            elif season_lower == "transition":
                seasonal_bonus = 0.05
        
        # Auto-detect season from current month
        if not season:
            month = datetime.now().month
            if month in [11, 12, 1, 2, 3]:  # Nov-Mar = dry season
                seasonal_bonus = 0.08
        
        final_score = min(base_score + geo_bonus + seasonal_bonus, 1.0)
        
        mastomys_count = sum(1 for d in detections if d.get("is_primary_reservoir", False))
        
        return {
            "risk_score": round(final_score, 4),
            "risk_level": self._score_to_level(final_score),
            "breakdown": {
                "detection_risk": round(base_score, 4),
                "geographic_risk": round(geo_bonus, 4),
                "seasonal_risk": round(seasonal_bonus, 4),
            },
            "factors": {
                "total_detections": len(detections),
                "mastomys_count": mastomys_count,
                "high_confidence_detections": sum(1 for d in detections if d.get("confidence", 0) > 0.7),
                "region": region,
                "endemic_area": geo_bonus > 0,
            },
            "recommendation": self._get_recommendation(final_score, mastomys_count)
        }
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MODERATE"
        elif score >= 0.2:
            return "LOW"
        return "MINIMAL"
    
    def _get_recommendation(self, score: float, mastomys_count: int) -> str:
        """Generate action recommendation based on risk"""
        if score >= 0.8 or mastomys_count >= 3:
            return "IMMEDIATE ACTION: Deploy rodent control team. Alert local health authorities. Consider community screening."
        elif score >= 0.6 or mastomys_count >= 2:
            return "HIGH PRIORITY: Schedule rodent control intervention. Notify health surveillance unit."
        elif score >= 0.4 or mastomys_count >= 1:
            return "MODERATE: Increase monitoring frequency. Prepare control measures."
        elif score >= 0.2:
            return "LOW: Continue routine surveillance. Document findings."
        return "MINIMAL: Standard monitoring protocols."
