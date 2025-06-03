"""
MNTRK Sovereign Observatory - Neuro-Symbolic Reasoning Engine
Experta + NetworkX based symbolic reasoning for biosurveillance
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import networkx as nx
from experta import *

logger = logging.getLogger("Symbolic-Engine")

class BiosurveillanceFacts(Fact):
    """Facts for biosurveillance reasoning."""
    pass

class SymbolicReasoningEngine(KnowledgeEngine):
    """
    Neuro-Symbolic Reasoning Engine for MNTRK Sovereign Observatory.
    Combines rule-based reasoning with graph-based analysis.
    """
    
    def __init__(self):
        super().__init__()
        self.version = "1.0.0"
        self.knowledge_graph = nx.DiGraph()
        self.rules_loaded = False
        self.inference_history = []
        
    async def initialize(self):
        """Initialize the symbolic reasoning engine."""
        try:
            logger.info("🔎 Initializing Symbolic Reasoning Engine")
            
            # Initialize knowledge graph
            await self._build_knowledge_graph()
            
            # Load default rules
            await self._load_default_rules()
            
            self.rules_loaded = True
            logger.info("✅ Symbolic Reasoning Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Symbolic engine initialization failed: {e}")
            raise
    
    async def _build_knowledge_graph(self):
        """Build knowledge graph for biosurveillance domain."""
        # Environmental factors
        self.knowledge_graph.add_node("temperature", type="environmental", importance=0.8)
        self.knowledge_graph.add_node("rainfall", type="environmental", importance=0.7)
        self.knowledge_graph.add_node("vegetation", type="environmental", importance=0.6)
        self.knowledge_graph.add_node("humidity", type="environmental", importance=0.5)
        
        # Species and disease nodes
        self.knowledge_graph.add_node("mastomys", type="species", risk_factor=0.9)
        self.knowledge_graph.add_node("lassa_fever", type="disease", severity=0.95)
        
        # Risk factors
        self.knowledge_graph.add_node("high_density", type="risk_factor", weight=0.8)
        self.knowledge_graph.add_node("seasonal_migration", type="risk_factor", weight=0.7)
        self.knowledge_graph.add_node("human_contact", type="risk_factor", weight=0.9)
        
        # Add relationships
        self.knowledge_graph.add_edge("temperature", "mastomys", relationship="influences", strength=0.8)
        self.knowledge_graph.add_edge("rainfall", "mastomys", relationship="influences", strength=0.7)
        self.knowledge_graph.add_edge("vegetation", "mastomys", relationship="habitat", strength=0.9)
        self.knowledge_graph.add_edge("mastomys", "lassa_fever", relationship="vector", strength=0.95)
        self.knowledge_graph.add_edge("high_density", "lassa_fever", relationship="increases_risk", strength=0.8)
        
        logger.info(f"🔗 Built knowledge graph with {self.knowledge_graph.number_of_nodes()} nodes")
    
    async def _load_default_rules(self):
        """Load default reasoning rules."""
        # Rules are defined as methods with @Rule decorators
        logger.info("📋 Loading default symbolic reasoning rules")
    
    @Rule(BiosurveillanceFacts(temperature=MATCH.temp, detection_count=MATCH.count))
    def high_temperature_risk(self, temp, count):
        """Rule: High temperature increases Mastomys activity and disease risk."""
        if temp > 30 and count > 5:
            self.declare(BiosurveillanceFacts(risk_level="high", reason="high_temperature_activity"))
            logger.info(f"🔥 High temperature risk triggered: {temp}°C, {count} detections")
    
    @Rule(BiosurveillanceFacts(rainfall=MATCH.rain, season=MATCH.season))
    def wet_season_risk(self, rain, season):
        """Rule: Wet season increases breeding and migration."""
        if season == "wet" and rain > 100:
            self.declare(BiosurveillanceFacts(risk_level="elevated", reason="wet_season_breeding"))
            logger.info(f"🌧️ Wet season risk triggered: {rain}mm rainfall")
    
    @Rule(BiosurveillanceFacts(detection_count=MATCH.count, latitude=MATCH.lat, longitude=MATCH.lon))
    def high_density_cluster(self, count, lat, lon):
        """Rule: High detection density indicates population cluster."""
        if count > 10:
            self.declare(BiosurveillanceFacts(
                cluster_detected=True, 
                cluster_location=(lat, lon),
                reason="high_density_cluster"
            ))
            logger.info(f"🎯 High density cluster detected: {count} at ({lat}, {lon})")
    
    @Rule(BiosurveillanceFacts(vegetation_index=MATCH.veg, temperature=MATCH.temp))
    def optimal_habitat_conditions(self, veg, temp):
        """Rule: Optimal habitat conditions increase risk."""
        if 0.4 <= veg <= 0.8 and 20 <= temp <= 35:
            self.declare(BiosurveillanceFacts(
                habitat_suitability="optimal",
                reason="optimal_habitat_conditions"
            ))
            logger.info(f"🌿 Optimal habitat conditions: vegetation={veg}, temp={temp}°C")
    
    async def evaluate_risk(self, observation_data: Dict) -> Dict:
        """
        Evaluate risk using symbolic reasoning.
        
        Args:
            observation_data: Environmental and detection data
            
        Returns:
            Dict with risk assessment and reasoning
        """
        try:
            # Reset engine
            self.reset()
            
            # Declare facts from observation data
            facts = BiosurveillanceFacts(
                temperature=observation_data.get('temperature', 25),
                rainfall=observation_data.get('rainfall', 0),
                vegetation_index=observation_data.get('vegetation_index', 0.5),
                detection_count=observation_data.get('detection_count', 0),
                latitude=observation_data.get('latitude', 0),
                longitude=observation_data.get('longitude', 0),
                season=observation_data.get('season', 'transition')
            )
            
            self.declare(facts)
            
            # Run inference
            self.run()
            
            # Collect results
            risk_factors = []
            risk_level = "low"
            confidence = 0.5
            
            for fact in self.facts:
                if hasattr(fact, 'risk_level'):
                    if fact.risk_level == "high":
                        risk_level = "high"
                        confidence = 0.9
                    elif fact.risk_level == "elevated" and risk_level != "high":
                        risk_level = "medium"
                        confidence = 0.7
                
                if hasattr(fact, 'reason'):
                    risk_factors.append(fact.reason)
            
            # Graph-based analysis
            graph_analysis = await self._analyze_knowledge_graph(observation_data)
            
            # Combine symbolic and graph reasoning
            final_assessment = await self._combine_reasoning(
                symbolic_risk=risk_level,
                graph_analysis=graph_analysis,
                risk_factors=risk_factors
            )
            
            # Store inference history
            inference_record = {
                "timestamp": datetime.now().isoformat(),
                "input_data": observation_data,
                "symbolic_risk": risk_level,
                "graph_analysis": graph_analysis,
                "final_assessment": final_assessment,
                "confidence": confidence
            }
            
            self.inference_history.append(inference_record)
            
            return final_assessment
            
        except Exception as e:
            logger.error(f"Risk evaluation failed: {e}")
            return {
                "risk_level": "unknown",
                "confidence": 0.0,
                "error": str(e),
                "reasoning": ["evaluation_failed"]
            }
    
    async def _analyze_knowledge_graph(self, data: Dict) -> Dict:
        """Analyze data using knowledge graph."""
        try:
            # Calculate influence scores
            influence_scores = {}
            
            # Temperature influence
            temp = data.get('temperature', 25)
            if 'temperature' in self.knowledge_graph:
                temp_influence = min(1.0, abs(temp - 25) / 15)  # Normalize temperature deviation
                influence_scores['temperature'] = temp_influence
            
            # Rainfall influence
            rainfall = data.get('rainfall', 0)
            if 'rainfall' in self.knowledge_graph:
                rain_influence = min(1.0, rainfall / 200)  # Normalize rainfall
                influence_scores['rainfall'] = rain_influence
            
            # Vegetation influence
            vegetation = data.get('vegetation_index', 0.5)
            if 'vegetation' in self.knowledge_graph:
                veg_influence = vegetation  # Already normalized 0-1
                influence_scores['vegetation'] = veg_influence
            
            # Calculate overall graph risk score
            total_influence = sum(influence_scores.values())
            avg_influence = total_influence / len(influence_scores) if influence_scores else 0
            
            # Determine graph-based risk level
            if avg_influence > 0.7:
                graph_risk = "high"
            elif avg_influence > 0.4:
                graph_risk = "medium"
            else:
                graph_risk = "low"
            
            return {
                "graph_risk_level": graph_risk,
                "influence_scores": influence_scores,
                "total_influence": round(total_influence, 3),
                "average_influence": round(avg_influence, 3)
            }
            
        except Exception as e:
            logger.error(f"Knowledge graph analysis failed: {e}")
            return {"graph_risk_level": "unknown", "error": str(e)}
    
    async def _combine_reasoning(self, symbolic_risk: str, graph_analysis: Dict, risk_factors: List[str]) -> Dict:
        """Combine symbolic and graph-based reasoning."""
        try:
            # Risk level mapping
            risk_mapping = {"low": 0, "medium": 1, "high": 2, "unknown": 0}
            
            symbolic_score = risk_mapping.get(symbolic_risk, 0)
            graph_score = risk_mapping.get(graph_analysis.get("graph_risk_level", "low"), 0)
            
            # Weighted combination (symbolic reasoning gets higher weight)
            combined_score = (0.7 * symbolic_score) + (0.3 * graph_score)
            
            # Convert back to risk level
            if combined_score >= 1.5:
                final_risk = "high"
                confidence = 0.85
            elif combined_score >= 0.7:
                final_risk = "medium"
                confidence = 0.75
            else:
                final_risk = "low"
                confidence = 0.65
            
            # Generate reasoning explanation
            reasoning = risk_factors.copy()
            if graph_analysis.get("average_influence", 0) > 0.5:
                reasoning.append("environmental_factors_elevated")
            
            return {
                "risk_level": final_risk,
                "confidence": confidence,
                "reasoning": reasoning,
                "symbolic_contribution": symbolic_score,
                "graph_contribution": graph_score,
                "combined_score": round(combined_score, 3),
                "assessment_method": "hybrid_symbolic_graph"
            }
            
        except Exception as e:
            logger.error(f"Reasoning combination failed: {e}")
            return {
                "risk_level": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def load_rules(self, rules: List[Dict]):
        """Load custom rules into the engine."""
        try:
            logger.info(f"📋 Loading {len(rules)} custom rules")
            
            for rule in rules:
                rule_id = rule.get('rule_id')
                condition = rule.get('condition')
                action = rule.get('action')
                confidence = rule.get('confidence', 0.5)
                
                # Store rule metadata
                self.knowledge_graph.add_node(
                    rule_id,
                    type="rule",
                    condition=condition,
                    action=action,
                    confidence=confidence
                )
            
            logger.info(f"✅ Loaded {len(rules)} custom rules successfully")
            
        except Exception as e:
            logger.error(f"Rule loading failed: {e}")
            raise
    
    async def get_status(self) -> Dict:
        """Get symbolic engine status."""
        return {
            "engine_version": self.version,
            "rules_loaded": self.rules_loaded,
            "knowledge_graph_nodes": self.knowledge_graph.number_of_nodes(),
            "knowledge_graph_edges": self.knowledge_graph.number_of_edges(),
            "inference_history_count": len(self.inference_history),
            "last_inference": self.inference_history[-1]["timestamp"] if self.inference_history else None
        }

# Global symbolic engine instance
symbolic_engine = SymbolicReasoningEngine()
