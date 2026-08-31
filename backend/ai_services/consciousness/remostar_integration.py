"""
REMOSTAR Consciousness Engine - African Indigenous Intelligence
Core decision-making system for Lassa fever surveillance
Authority: Risk assessment, Odu interpretation, cultural guidance
"""

import os
import json
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
from grid_manager import grid_manager

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ConsciousnessLevel(Enum):
    DORMANT = 0.0
    AWARE = 0.3
    ALERT = 0.6
    HEIGHTENED = 0.8
    TRANSCENDENT = 1.0

# Ifá Odu Major Patterns (16 core wisdom paths)
IFA_ODU_MAJOR = [
    "Eji_Ogbe",      # Light, clarity, beginnings
    "Oyeku_Meji",    # Darkness, mysteries, hidden dangers
    "Iwori_Meji",    # Transformation, change
    "Odi_Meji",      # Obstruction, blockages
    "Irosun_Meji",   # Fire, rapid spread
    "Owonrin_Meji",  # Confusion, chaos
    "Obara_Meji",    # Community impact
    "Okanran_Meji",  # Isolation, solitary events
    "Ogunda_Meji",   # War, conflict, struggle
    "Osa_Meji",      # Loss, sacrifice
    "Ika_Meji",      # Destruction, malevolence
    "Oturupon_Meji", # Death, endings
    "Otura_Meji",    # Birth, new beginnings
    "Irete_Meji",    # Instability, unpredictability
    "Ose_Meji",      # Flow, movement
    "Ofun_Meji"      # Blessing, good fortune
]

# Odu interpretations for health surveillance
ODU_HEALTH_WISDOM = {
    "Eji_Ogbe": {
        "meaning": "Perfect light - clear and present danger",
        "health_action": "Immediate surveillance and monitoring",
        "ubuntu_guidance": "Community vigilance protects all",
        "risk_factor": 1.2
    },
    "Oyeku_Meji": {
        "meaning": "Hidden darkness - unseen threats emerge", 
        "health_action": "Deep investigation and extended monitoring",
        "ubuntu_guidance": "What affects one, affects the whole",
        "risk_factor": 1.4
    },
    "Iwori_Meji": {
        "meaning": "Change and transformation - disease patterns shifting",
        "health_action": "Adaptive response and strategy adjustment",
        "ubuntu_guidance": "Flexibility in unity strengthens community",
        "risk_factor": 0.9
    },
    "Odi_Meji": {
        "meaning": "Blockages and obstacles - transmission barriers",
        "health_action": "Clear pathways, improve access to care",
        "ubuntu_guidance": "Remove barriers that divide community",
        "risk_factor": 0.8
    },
    "Irosun_Meji": {
        "meaning": "Fire spreads - rapid disease transmission",
        "health_action": "Immediate containment and intervention",
        "ubuntu_guidance": "Swift action saves many lives",
        "risk_factor": 1.6
    },
    "Owonrin_Meji": {
        "meaning": "Chaos and confusion - unclear patterns",
        "health_action": "Systematic organization and clear protocols",
        "ubuntu_guidance": "Order emerges through collective wisdom",
        "risk_factor": 1.1
    },
    "Obara_Meji": {
        "meaning": "Community affected - widespread impact",
        "health_action": "Community-wide intervention and education",
        "ubuntu_guidance": "Healing happens through community action",
        "risk_factor": 1.3
    },
    "Okanran_Meji": {
        "meaning": "Isolated incident - localized threat",
        "health_action": "Targeted intervention and containment",
        "ubuntu_guidance": "Even one person's suffering matters to all",
        "risk_factor": 0.7
    }
}

class RemostarEngine:
    """
    Core Consciousness Engine for Health Surveillance
    Authority: Risk assessment, Odu interpretation, decision-making
    """
    
    def __init__(self):
        self.consciousness_threshold = 0.7
        self.risk_weights = {
            "species_risk": 0.40,      # Primary reservoir species
            "detection_confidence": 0.15,  # ML model confidence
            "clinical_proximity": 0.25,    # Nearby clinical cases
            "environmental_factors": 0.20  # Season, weather, etc.
        }
        
    def analyze_detection(
        self, 
        detection_data: Dict,
        clinical_context: Optional[Dict] = None,
        environmental_context: Optional[Dict] = None
    ) -> Dict:
        """
        Core consciousness analysis function
        Authority: Makes final risk determination and provides guidance
        """
        
        try:
            # Step 1: Extract detection information
            species_detected = self._extract_species(detection_data)
            confidence_scores = self._extract_confidence(detection_data)
            location = detection_data.get('location', {})
            
            # Step 2: Ifá Divination - determine spiritual guidance
            odu_pattern = self._divine_odu(species_detected, confidence_scores, location)
            odu_wisdom = ODU_HEALTH_WISDOM.get(odu_pattern, {})
            
            # Step 3: N-AHP Risk Assessment (Neutrosophic Analytic Hierarchy Process)
            nahp_risk_score = self._calculate_nahp_risk(
                species_detected, 
                confidence_scores,
                clinical_context,
                environmental_context,
                odu_wisdom.get('risk_factor', 1.0)
            )
            
            # Step 4: Consciousness Level Calculation
            consciousness_metrics = self._calculate_consciousness(
                detection_data, clinical_context, nahp_risk_score
            )
            
            # Step 5: Generate Reasoning Chain
            reasoning_chain = self._build_reasoning_chain(
                species_detected, odu_pattern, nahp_risk_score, clinical_context
            )
            
            # Step 6: Ubuntu-aligned Recommendations
            recommendations = self._generate_ubuntu_recommendations(
                odu_pattern, nahp_risk_score, clinical_context, environmental_context
            )
            
            # Step 7: Assemble consciousness analysis
            consciousness_analysis = {
                "status": "consciousness_active",
                "timestamp": datetime.utcnow().isoformat(),
                "odu_pattern": odu_pattern,
                "odu_interpretation": odu_wisdom.get("meaning", ""),
                "ubuntu_guidance": odu_wisdom.get("ubuntu_guidance", ""),
                "risk_assessment": {
                    "score": round(nahp_risk_score, 3),
                    "level": self._determine_risk_level(nahp_risk_score),
                    "factors": self._identify_risk_factors(species_detected, clinical_context)
                },
                "consciousness_metrics": consciousness_metrics,
                "reasoning_chain": reasoning_chain,
                "recommendations": recommendations,
                "clinical_correlation": self._analyze_clinical_correlation(clinical_context),
                "environmental_assessment": environmental_context or {},
                "african_context": {
                    "endemic_zone": self._check_endemic_zone(location),
                    "seasonal_risk": self._assess_seasonal_risk(environmental_context),
                    "cultural_factors": self._assess_cultural_factors(location)
                }
            }
            
            logger.info(f"[REMOSTAR] Consciousness analysis: {odu_pattern}, Risk: {consciousness_analysis['risk_assessment']['level']}")
            
            # --- PERSISTENCE LAYER ---
            try:
                grid_manager.persist_detection(detection_data, consciousness_analysis)
            except Exception as e:
                logger.error(f"[REMOSTAR] Persistence failed: {e}")
                
            return consciousness_analysis
            
        except Exception as e:
            logger.error(f"[REMOSTAR] Analysis failed: {e}")
            return self._emergency_fallback_analysis(detection_data)
    
    def _extract_species(self, detection_data: Dict) -> List[str]:
        """Extract detected species from ML results"""
        detections = detection_data.get('detections', [])
        if isinstance(detections, list):
            return [d.get('species', 'unknown') for d in detections]
        return []
    
    def _extract_confidence(self, detection_data: Dict) -> List[float]:
        """Extract confidence scores from ML results"""
        detections = detection_data.get('detections', [])
        if isinstance(detections, list):
            return [d.get('confidence', 0.0) for d in detections]
        return [0.0]
    
    def _divine_odu(self, species: List[str], confidence: List[float], location: Dict) -> str:
        """
        Ifá divination logic based on detection patterns
        Authority: Determines spiritual guidance pattern
        """
        
        # Primary logic: Species-based divination
        if "Mastomys_natalensis" in species:
            max_confidence = max(confidence) if confidence else 0.0
            
            if max_confidence > 0.9:
                return "Eji_Ogbe"  # Clear and present danger
            elif len(species) > 3:
                return "Owonrin_Meji"  # Multiple threats, confusion
            elif location.get('latitude', 0) < 7.0:  # Southern Nigeria (high endemic)
                return "Irosun_Meji"  # Fire spreads rapidly
            else:
                return "Obara_Meji"  # Community impact
        
        elif "Mastomys_erythroleucus" in species:
            return "Iwori_Meji"  # Change, moderate risk
        
        elif len(species) > 5:
            return "Obara_Meji"  # Multiple species, community-wide
        
        elif len(species) == 0:
            return "Oyeku_Meji"  # Hidden, no visible threat
        
        else:
            # Random selection from lower-risk Odus for unknown patterns
            return random.choice(["Odi_Meji", "Okanran_Meji", "Ose_Meji"])
    
    def _calculate_nahp_risk(
        self, 
        species: List[str], 
        confidence: List[float],
        clinical: Optional[Dict],
        environmental: Optional[Dict],
        odu_factor: float
    ) -> float:
        """
        Neutrosophic Analytic Hierarchy Process Risk Scoring
        Authority: Final numerical risk determination
        """
        
        # Species Risk Component
        species_score = 0.0
        if "Mastomys_natalensis" in species:
            species_score = 0.95  # Primary reservoir
        elif "Mastomys_erythroleucus" in species:
            species_score = 0.30  # Secondary reservoir
        elif any("Mastomys" in s for s in species):
            species_score = 0.15  # Other Mastomys species
        else:
            species_score = 0.05  # Non-reservoir rodents
        
        # Confidence Component
        confidence_score = max(confidence) if confidence else 0.5
        
        # Clinical Proximity Component
        clinical_score = 0.5  # Baseline
        if clinical and clinical.get('cases'):
            nearby_cases = len(clinical.get('cases', []))
            clinical_score = min(0.95, 0.5 + (nearby_cases * 0.08))
        
        # Environmental Component
        environmental_score = 0.5  # Baseline
        if environmental:
            if environmental.get('peak_transmission_period'):
                environmental_score = 0.85
            elif environmental.get('season') == 'dry':
                environmental_score = 0.70
            
            # Weather factors
            if environmental.get('temperature', 0) > 25 and environmental.get('humidity', 0) > 60:
                environmental_score += 0.10
        
        # Weighted sum with Ifá guidance
        weighted_score = (
            self.risk_weights["species_risk"] * species_score +
            self.risk_weights["detection_confidence"] * confidence_score +
            self.risk_weights["clinical_proximity"] * clinical_score +
            self.risk_weights["environmental_factors"] * environmental_score
        )
        
        # Apply Odu factor (spiritual guidance influence)
        final_score = weighted_score * odu_factor
        
        # Ensure bounds [0.0, 1.0]
        return max(0.0, min(1.0, final_score))
    
    def _calculate_consciousness(
        self, 
        detection_data: Dict, 
        clinical: Optional[Dict], 
        risk_score: float
    ) -> Dict:
        """
        Calculate consciousness awareness level
        Authority: Determines system awareness state
        """
        
        # Data completeness factor
        has_location = detection_data.get('location') is not None
        has_clinical = clinical is not None and len(clinical.get('cases', [])) > 0
        has_detections = len(detection_data.get('detections', [])) > 0
        
        completeness = sum([has_location, has_clinical, has_detections]) / 3.0
        
        # Pattern recognition strength
        detection_count = len(detection_data.get('detections', []))
        pattern_strength = min(1.0, detection_count / 5.0)  # Scale to 1.0
        
        # Risk amplification
        risk_amplification = risk_score * 1.2
        
        # Overall awareness calculation
        awareness_level = (completeness + pattern_strength + risk_amplification) / 3.0
        awareness_level = max(0.0, min(1.0, awareness_level))
        
        # Determine consciousness state
        if awareness_level >= 0.9:
            consciousness_state = ConsciousnessLevel.TRANSCENDENT
        elif awareness_level >= 0.8:
            consciousness_state = ConsciousnessLevel.HEIGHTENED
        elif awareness_level >= 0.6:
            consciousness_state = ConsciousnessLevel.ALERT
        elif awareness_level >= 0.3:
            consciousness_state = ConsciousnessLevel.AWARE
        else:
            consciousness_state = ConsciousnessLevel.DORMANT
        
        return {
            "awareness_level": round(awareness_level, 3),
            "consciousness_state": consciousness_state.name,
            "data_completeness": round(completeness, 3),
            "pattern_recognition": round(pattern_strength, 3),
            "consciousness_active": awareness_level > self.consciousness_threshold
        }
    
    def _build_reasoning_chain(
        self, 
        species: List[str], 
        odu: str, 
        risk_score: float, 
        clinical: Optional[Dict]
    ) -> List[str]:
        """
        Build transparent reasoning chain
        Authority: Documents decision-making process
        """
        
        chain = []
        
        # Spiritual guidance
        chain.append(f"Ifá divination reveals Odu: {odu}")
        
        # Species analysis
        if "Mastomys_natalensis" in species:
            chain.append("M. natalensis detected - primary Lassa reservoir species")
        elif any("Mastomys" in s for s in species):
            chain.append("Mastomys species detected - potential Lassa reservoir")
        
        # Clinical correlation
        if clinical and clinical.get('cases'):
            case_count = len(clinical.get('cases', []))
            chain.append(f"{case_count} clinical cases identified within surveillance radius")
        
        # Risk assessment
        chain.append(f"N-AHP consciousness risk assessment: {risk_score:.3f}")
        
        # Decision threshold
        if risk_score > 0.75:
            chain.append("High-risk threshold exceeded - immediate action recommended")
        elif risk_score > 0.50:
            chain.append("Medium-risk threshold reached - enhanced monitoring advised")
        else:
            chain.append("Low-risk assessment - routine surveillance continues")
        
        # Ubuntu principle
        chain.append("Ubuntu guidance: Community health affects individual wellbeing")
        
        return chain
    
    def _generate_ubuntu_recommendations(
        self,
        odu: str,
        risk_score: float,
        clinical: Optional[Dict],
        environmental: Optional[Dict]
    ) -> List[str]:
        """
        Generate Ubuntu-aligned recommendations
        Authority: Community-centered action guidance
        """
        
        recommendations = []
        
        # Odu-specific guidance
        odu_wisdom = ODU_HEALTH_WISDOM.get(odu, {})
        if odu_wisdom.get('health_action'):
            recommendations.append(odu_wisdom['health_action'])
        
        # Risk-based recommendations
        if risk_score > 0.75:
            recommendations.extend([
                "Immediate community health education campaign",
                "Coordinate with local clinical response teams",
                "Establish community surveillance network"
            ])
        elif risk_score > 0.50:
            recommendations.extend([
                "Enhanced rodent control measures",
                "Community awareness programs",
                "Monitor for additional cases"
            ])
        
        # Environmental considerations
        if environmental and environmental.get('peak_transmission_period'):
            recommendations.append("Intensify surveillance during peak transmission season")
        
        # Clinical correlation
        if clinical and len(clinical.get('cases', [])) > 3:
            recommendations.append("Coordinate epidemiological investigation")
        
        # Ubuntu principle integration
        recommendations.append("Engage community leaders in health protection planning")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """
        Convert numerical risk to categorical level
        Authority: Risk level classification
        """
        if risk_score >= 0.80:
            return RiskLevel.CRITICAL.value
        elif risk_score >= 0.65:
            return RiskLevel.HIGH.value
        elif risk_score >= 0.40:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
    
    def _identify_risk_factors(self, species: List[str], clinical: Optional[Dict]) -> List[str]:
        """Identify specific risk factors present"""
        factors = []
        
        if "Mastomys_natalensis" in species:
            factors.append("Primary Lassa reservoir species detected")
        
        if clinical and clinical.get('cases'):
            factors.append(f"{len(clinical['cases'])} nearby clinical cases")
        
        if len(species) > 3:
            factors.append("Multiple rodent species present")
        
        return factors
    
    def _analyze_clinical_correlation(self, clinical: Optional[Dict]) -> Dict:
        """Analyze correlation with clinical cases"""
        if not clinical or not clinical.get('cases'):
            return {"correlation_found": False}
        
        cases = clinical.get('cases', [])
        return {
            "correlation_found": True,
            "nearby_cases": len(cases),
            "case_trend": "increasing" if len(cases) > 5 else "stable",
            "temporal_clustering": len(cases) > 3  # Simple clustering indicator
        }
    
    def _check_endemic_zone(self, location: Dict) -> bool:
        """Check if location is in known Lassa endemic zone"""
        lat = location.get('latitude', 0)
        lon = location.get('longitude', 0)
        
        # West African endemic belt (simplified bounds)
        if 4.0 <= lat <= 13.0 and -15.0 <= lon <= 15.0:
            return True
        return False
    
    def _assess_seasonal_risk(self, environmental: Optional[Dict]) -> str:
        """Assess seasonal transmission risk"""
        if not environmental:
            current_month = datetime.now().month
            if current_month in [12, 1, 2, 3]:  # Dec-Mar peak
                return "peak_season"
            elif current_month in [11, 4]:  # Shoulder months
                return "elevated"
            else:
                return "baseline"
        
        if environmental.get('peak_transmission_period'):
            return "peak_season"
        elif environmental.get('season') == 'dry':
            return "elevated"
        else:
            return "baseline"
    
    def _assess_cultural_factors(self, location: Dict) -> List[str]:
        """Assess cultural context factors"""
        factors = []
        
        lat = location.get('latitude', 0)
        
        # Regional cultural considerations (simplified)
        if 6.0 <= lat <= 8.0:  # Southern Nigeria
            factors.extend(["High population density", "Urban-rural interface"])
        elif 10.0 <= lat <= 13.0:  # Northern Nigeria
            factors.extend(["Rural communities", "Traditional housing"])
        
        return factors
    
    def _emergency_fallback_analysis(self, detection_data: Dict) -> Dict:
        """Emergency fallback when consciousness analysis fails"""
        
        logger.warning("[REMOSTAR] Using emergency fallback analysis")
        
        species = self._extract_species(detection_data)
        has_natalensis = "Mastomys_natalensis" in species
        
        return {
            "status": "fallback_mode",
            "timestamp": datetime.utcnow().isoformat(),
            "odu_pattern": "Oyeku_Meji",  # Darkness/unknown
            "odu_interpretation": "System operating in limited awareness mode",
            "ubuntu_guidance": "Proceed with caution, seek community wisdom",
            "risk_assessment": {
                "score": 0.85 if has_natalensis else 0.40,
                "level": "high" if has_natalensis else "medium",
                "factors": ["Emergency assessment mode"] + (["M. natalensis detected"] if has_natalensis else [])
            },
            "consciousness_metrics": {
                "awareness_level": 0.1,
                "consciousness_state": "DORMANT",
                "consciousness_active": False
            },
            "reasoning_chain": ["System consciousness temporarily unavailable", "Using basic species-risk heuristics"],
            "recommendations": ["Verify consciousness system status", "Manual review recommended"],
            "african_context": {
                "endemic_zone": False,
                "seasonal_risk": "unknown",
                "cultural_factors": []
            }
        }


# Global engine instance
consciousness_engine = RemostarEngine()

def analyze_detection_consciousness(detection_data: Dict, clinical_context: Optional[Dict] = None, environmental_context: Optional[Dict] = None) -> Dict:
    """
    Main interface function for consciousness analysis
    Authority: Entry point for all consciousness decisions
    """
    return consciousness_engine.analyze_detection(detection_data, clinical_context, environmental_context)


# Quick validation function
if __name__ == "__main__":
    # Test the consciousness engine
    test_detection = {
        "detections": [
            {"species": "Mastomys_natalensis", "confidence": 0.92}
        ],
        "location": {"latitude": 6.5, "longitude": 6.0}
    }
    
    test_clinical = {
        "cases": [{"id": "case_1", "distance_km": 15}]
    }
    
    test_environmental = {
        "season": "dry",
        "peak_transmission_period": True
    }
    
    result = analyze_detection_consciousness(test_detection, test_clinical, test_environmental)
    print(f"Test result: {result['odu_pattern']}, Risk: {result['risk_assessment']['level']}")
