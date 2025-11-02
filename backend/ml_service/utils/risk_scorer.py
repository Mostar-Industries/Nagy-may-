import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RiskScorer:
    """Risk assessment based on detections and epidemiological context"""
    
    # Mastomys species detection contributes to risk
    MASTOMYS_SPECIES_WEIGHT = 0.7
    
    # Detection confidence weights
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD = 0.6
    
    def __init__(self):
        """Initialize risk scorer"""
        logger.info("[v0] Risk scorer initialized")
    
    def score_detections(self, detections: List[Dict[str, Any]]) -> float:
        """
        Score overall risk based on detections
        
        Args:
            detections: List of detection results from YOLO
        
        Returns:
            Risk score between 0.0 and 1.0
        """
        if not detections:
            logger.info("[v0] No detections, risk score = 0.0")
            return 0.0
        
        # Calculate risk based on detections
        total_confidence = sum(d.get("confidence", 0) for d in detections)
        avg_confidence = total_confidence / len(detections)
        
        # Weight by detection count (more detections = higher risk)
        detection_count_factor = min(len(detections) / 5, 1.0)  # Cap at 5 detections
        
        # Calculate risk score
        risk_score = (avg_confidence * 0.7) + (detection_count_factor * 0.3)
        risk_score = min(risk_score, 1.0)
        
        logger.info(
            f"[v0] Risk scoring: {len(detections)} detections, "
            f"avg_confidence={avg_confidence:.2f}, risk_score={risk_score:.2f}"
        )
        
        return risk_score
    
    def score_with_context(
        self,
        detections: List[Dict[str, Any]],
        latitude: float = None,
        longitude: float = None,
        environment: str = None
    ) -> Dict[str, Any]:
        """
        Score risk with epidemiological context
        
        Args:
            detections: Detection results
            latitude: Geographic latitude
            longitude: Geographic longitude
            environment: Environment type (urban, rural, forest, etc.)
        
        Returns:
            Risk assessment dictionary
        """
        base_risk = self.score_detections(detections)
        
        # Environmental factors (example values)
        env_multiplier = {
            "forest": 1.2,
            "rural": 1.1,
            "urban": 0.8,
            "agricultural": 1.0
        }.get(environment, 1.0)
        
        adjusted_risk = min(base_risk * env_multiplier, 1.0)
        
        assessment = {
            "base_risk_score": base_risk,
            "environmental_factor": env_multiplier,
            "adjusted_risk_score": adjusted_risk,
            "risk_level": self._get_risk_level(adjusted_risk),
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "environment": environment,
            "detection_count": len(detections),
            "recommendation": self._get_recommendation(adjusted_risk)
        }
        
        logger.info(f"[v0] Risk assessment: {assessment['risk_level']}")
        return assessment
    
    @staticmethod
    def _get_risk_level(score: float) -> str:
        """Convert numeric score to risk level"""
        if score < 0.3:
            return "LOW"
        elif score < 0.6:
            return "MEDIUM"
        elif score < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"
    
    @staticmethod
    def _get_recommendation(score: float) -> str:
        """Get recommendation based on risk score"""
        if score < 0.3:
            return "Continue monitoring"
        elif score < 0.6:
            return "Increase surveillance frequency"
        elif score < 0.8:
            return "Activate alert protocols"
        else:
            return "Immediate intervention required"
