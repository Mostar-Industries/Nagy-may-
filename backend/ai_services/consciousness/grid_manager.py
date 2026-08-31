"""
Mostar Grid Manager - Knowledge Graph & Persistence Handler
Authority: Management of Neo4j Knowledge Graph and Supabase historical data
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from neo4j import GraphDatabase
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class GridManager:
    """
    Handles synchronization between real-time detections, 
    the Neo4j Knowledge Graph (Mostar Grid), and Supabase persistence.
    """
    
    def __init__(self):
        # Neo4j Config
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://skyhawk_graph:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "mostar123")
        self.neo4j_db = os.getenv("NEO4J_DB", "neo4j") # Default to standard neo4j DB
        self.neo4j_driver = None
        
        # Supabase Config
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        self.supabase: Optional[Client] = None
        
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize database connections safely"""
        try:
            if self.neo4j_uri:
                self.neo4j_driver = GraphDatabase.driver(
                    self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
                )
                logger.info("[GRID] Neo4j driver initialized")
        except Exception as e:
            logger.error(f"[GRID] Failed to connect to Neo4j: {e}")

        try:
            if self.supabase_url and self.supabase_key:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                logger.info("[GRID] Supabase client initialized")
        except Exception as e:
            logger.error(f"[GRID] Failed to connect to Supabase: {e}")

    def persist_detection(self, detection_data: Dict, consciousness_analysis: Dict):
        """
        Entry point for data persistence.
        Saves to both Supabase (Long-term) and Neo4j (Cognitive Linkage).
        """
        # 1. Save to Supabase
        self._save_to_supabase(detection_data, consciousness_analysis)
        
        # 2. Update Mostar Grid (Neo4j)
        self._update_knowledge_graph(detection_data, consciousness_analysis)

    def _save_to_supabase(self, detection_data: Dict, analysis: Dict):
        """Save detection and analysis to Supabase history table"""
        if not self.supabase:
            return

        try:
            location = detection_data.get("location", {})
            lat = location.get("latitude", 0.0)
            lon = location.get("longitude", 0.0)
            
            # Align with frontend table and schema
            payload = {
                "latitude": lat,
                "longitude": lon,
                "detection_timestamp": analysis.get("timestamp", datetime.utcnow().isoformat()),
                "detection_count": len(detection_data.get("detections", [])),
                "source": detection_data.get("source", "ml_service"),
                "environmental_context": {
                    "detections": detection_data.get("detections"),
                    "location": detection_data.get("location"),
                    "consciousness_state": analysis.get("consciousness_metrics", {}).get("consciousness_state"),
                },
                "risk_assessment": {
                    "risk_score": analysis.get("risk_assessment", {}).get("score"),
                    "risk_level": analysis.get("risk_assessment", {}).get("level"),
                    "odu_pattern": analysis.get("odu_pattern"),
                    "ubuntu_guidance": analysis.get("ubuntu_guidance"),
                    "reasoning": analysis.get("reasoning_chain"),
                    "full_analysis": analysis
                }
            }
            
            result = self.supabase.table("detection_patterns").insert(payload).execute()
            logger.info(f"[GRID] Persistence successful in detection_patterns: {result.data[0].get('id') if result.data else 'Success'}")
        except Exception as e:
            logger.error(f"[GRID] Supabase persistence failed: {e}")

    def _update_knowledge_graph(self, detection_data: Dict, analysis: Dict):
        """Update Neo4j with new detection nodes and risk relationships"""
        if not self.neo4j_driver:
            return

        with self.neo4j_driver.session(database=self.neo4j_db) as session:
            try:
                # Cypher logic: Create Habitat if not exists, create DetectionNode, link them
                location = detection_data.get("location", {})
                lat = location.get("latitude")
                lon = location.get("longitude")
                
                # Default to Lagos if data is missing, to at least verify connection
                if lat is None or lon is None:
                    logger.warning("[GRID] Missing coordinates for graph update. Using default (0,0)")
                    lat, lon = 0.0, 0.0
                
                habitat_id = f"habitat_{round(lat, 2)}_{round(lon, 2)}"
                
                query = """
                MERGE (h:Habitat {id: $habitat_id})
                SET h.latitude = $lat, h.longitude = $lon
                
                CREATE (d:DetectionNode {
                    id: $vector_id,
                    timestamp: $ts,
                    species: $species,
                    risk_score: $risk,
                    odu_pattern: $odu,
                    ubuntu_guidance: $ubuntu
                })
                
                MERGE (d)-[:DETECTED_IN]->(h)
                """
                
                # Extract primary species for simplicity in graph
                detections = detection_data.get("detections", [])
                primary_species = detections[0].get("species") if detections else "unknown"
                
                session.run(query, 
                    habitat_id=habitat_id,
                    lat=lat, lon=lon,
                    vector_id=f"det_{datetime.utcnow().timestamp()}",
                    ts=analysis.get("timestamp"),
                    species=primary_species,
                    risk=analysis.get("risk_assessment", {}).get("score"),
                    odu=analysis.get("odu_pattern"),
                    ubuntu=analysis.get("ubuntu_guidance")
                )
                logger.info(f"[GRID] Knowledge graph updated for habitat: {habitat_id}")
            except Exception as e:
                logger.error(f"[GRID] Neo4j update failed: {e}")

    def close(self):
        if self.neo4j_driver:
            self.neo4j_driver.close()
    
    def query_regional_risk(self, region: str = None, lat: float = None, lon: float = None) -> Dict:
        """
        Query the Mostar Grid for regional risk aggregation.
        Used by the /risk-analysis endpoint.
        """
        if not self.neo4j_driver:
            logger.warning("[GRID] Neo4j not available for risk query")
            return {"error": "Knowledge graph unavailable"}
        
        with self.neo4j_driver.session(database=self.neo4j_db) as session:
            try:
                # Query by habitat proximity if lat/lon provided
                if lat is not None and lon is not None:
                    habitat_id = f"habitat_{round(lat, 2)}_{round(lon, 2)}"
                    
                    query = """
                    MATCH (h:Habitat {id: $habitat_id})<-[:DETECTED_IN]-(d:DetectionNode)
                    RETURN 
                        avg(d.risk_score) as avg_risk,
                        collect(d.odu_pattern) as odus,
                        collect(d.species) as species,
                        count(d) as detection_count
                    """
                    
                    result = session.run(query, habitat_id=habitat_id)
                else:
                    # Query all habitats (system-wide)
                    query = """
                    MATCH (h:Habitat)<-[:DETECTED_IN]-(d:DetectionNode)
                    RETURN 
                        avg(d.risk_score) as avg_risk,
                        collect(d.odu_pattern) as odus,
                        collect(d.species) as species,
                        count(d) as detection_count
                    """
                    result = session.run(query)
                
                record = result.single()
                
                if not record or record["detection_count"] == 0:
                    return {
                        "message": "No detection data found for this region",
                        "avg_risk": 0.0,
                        "detection_count": 0
                    }
                
                odus = record["odus"]
                species_list = record["species"]
                
                return {
                    "region": region or f"Habitat ({lat}, {lon})",
                    "average_risk": round(record["avg_risk"], 3) if record["avg_risk"] else 0.0,
                    "detection_count": record["detection_count"],
                    "recurring_odus": list(set(odus)),
                    "dominant_species": max(set(species_list), key=species_list.count) if species_list else "none",
                    "recommendation": "Increase surveillance in high-risk areas." if record["avg_risk"] > 0.7 else "Continue monitoring."
                }
                
            except Exception as e:
                logger.error(f"[GRID] Regional risk query failed: {e}")
                return {"error": str(e)}

# Singleton instance
grid_manager = GridManager()
