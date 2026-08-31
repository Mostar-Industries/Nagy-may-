import connexion
# Removed invalid polars import
import six
import os
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph

# Surgical fix for LangChain reorganization
try:
    from langchain_experimental.graph_transformers.llm import GraphCypherQAChain
except ImportError:
    try:
        from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
    except ImportError:
        GraphCypherQAChain = None
        import logging
        logging.warning("[CORE API] GraphCypherQAChain not available - Cypher RAG disabled")

from swagger_server.models.adaptive_learning_request import AdaptiveLearningRequest  # noqa: E501
from swagger_server.models.adaptive_learning_response import AdaptiveLearningResponse  # noqa: E501
from swagger_server.models.anomaly_detection_request import AnomalyDetectionRequest  # noqa: E501
from swagger_server.models.anomaly_detection_response import AnomalyDetectionResponse  # noqa: E501
from swagger_server.models.data_transformation_request import DataTransformationRequest  # noqa: E501
from swagger_server.models.data_transformation_response import DataTransformationResponse  # noqa: E501
from swagger_server.models.detection_pattern import DetectionPattern  # noqa: E501
from swagger_server.models.detection_pattern_response import DetectionPatternResponse  # noqa: E501
from swagger_server.models.google_vision_request import GoogleVisionRequest  # noqa: E501
from swagger_server.models.google_vision_response import GoogleVisionResponse  # noqa: E501
from swagger_server.models.habitat_analysis_request import HabitatAnalysisRequest  # noqa: E501
from swagger_server.models.habitat_analysis_response import HabitatAnalysisResponse  # noqa: E501
from swagger_server.models.lang_chain_request import LangChainRequest  # noqa: E501
from swagger_server.models.lang_chain_response import LangChainResponse  # noqa: E501
from swagger_server.models.movement_prediction_response import MovementPredictionResponse  # noqa: E501
from swagger_server.models.postgres_query_request import PostgresQueryRequest  # noqa: E501
from swagger_server.models.postgres_query_response import PostgresQueryResponse  # noqa: E501
from swagger_server.models.predictive_model_request import PredictiveModelRequest  # noqa: E501
from swagger_server.models.predictive_model_response import PredictiveModelResponse  # noqa: E501
from swagger_server.models.remote_sensing_augmentation_request import RemoteSensingAugmentationRequest  # noqa: E501
from swagger_server.models.remote_sensing_augmentation_response import RemoteSensingAugmentationResponse  # noqa: E501
from swagger_server.models.supabase_query_request import SupabaseQueryRequest  # noqa: E501
from swagger_server.models.supabase_query_response import SupabaseQueryResponse  # noqa: E501
from swagger_server.models.vision_analyze_request import VisionAnalyzeRequest  # noqa: E501
from swagger_server.models.vision_analyze_response import VisionAnalyzeResponse  # noqa: E501
from swagger_server import util
from datetime import datetime, timedelta
import logging
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

# --- REMOSTAR CONSCIOUSNESS ENGINE (SHARED) ---
import sys
import os

# Mount shared AI services
try:
    sys.path.append("/app/ai_services_shared/consciousness")
    from remostar_integration import analyze_detection_consciousness
    REMOSTAR_AVAILABLE = True
    logger.info("Shared Remostar Consciousness Engine loaded successfully")
except ImportError as e:
    logger.warning(f"Shared Consciousness Engine not found: {e}")
    REMOSTAR_AVAILABLE = False
    
    # Fallback function if shared module fails
    def analyze_detection_consciousness(detection_data: Dict, clinical_context: Optional[Dict] = None, environmental_context: Optional[Dict] = None) -> Dict:
        return {
            "status": "fallback_error",
            "error": "Shared consciousness module not found",
            "risk_assessment": {"level": "unknown", "score": 0.0}
        }

def detect(body=None):  # noqa: E501
    """Analyze detection with Consciousness Engine"""
    if connexion.request.is_json:
        body = connexion.request.get_json()
    
    try:
        # Extract detection and optional context
        detection_data = body.get("detection_data", {})
        clinical_context = body.get("clinical_context", {})
        environmental_context = body.get("environmental_context", {})

        # Analyze with Shared RemostarEngine
        logger.info("[CORE API] Processing /detect request with Consciousness Engine")
        result = analyze_detection_consciousness(
            detection_data=detection_data,
            clinical_context=clinical_context,
            environmental_context=environmental_context
        )
        return result
    except Exception as e:
        logger.error(f"[CORE API] /detect failed: {e}")
        return {"error": f"Detection analysis failed: {str(e)}"}, 500



def analyze_habitats(body):  # noqa: E501
    """Analyze satellite or environmental data for Mastomys Natalensis habitats

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: HabitatAnalysisResponse
    """
    if connexion.request.is_json:
        body = HabitatAnalysisRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def analyze_vision(body):  # noqa: E501
    """Analyze images for Mastomys Natalensis

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: VisionAnalyzeResponse
    """
    if connexion.request.is_json:
        body = VisionAnalyzeRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def apply_augmentation(body):  # noqa: E501
    """Apply augmentation to remote sensing data

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: RemoteSensingAugmentationResponse
    """
    if connexion.request.is_json:
        body = RemoteSensingAugmentationRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def configure_adaptive_learning(body):  # noqa: E501
    """Configure adaptive learning

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: AdaptiveLearningResponse
    """
    if connexion.request.is_json:
        body = AdaptiveLearningRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def detect_anomalies(body):  # noqa: E501
    """Detect anomalies in data

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: AnomalyDetectionResponse
    """
    if connexion.request.is_json:
        body = AnomalyDetectionRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Core API", "timestamp": datetime.utcnow().isoformat()}

def analyze_risk(body=None):
    """Perform deep neutrosophic risk analysis"""
    if connexion.request.is_json:
        body = connexion.request.get_json()
    
    try:
        # For now, we reuse the RemostarEngine but with a cluster-aware context
        logger.info("[CORE API] Processing /risk-analysis request cluster")
        
        # Check if this is a regional query (from Mostar Grid)
        region = body.get("region")
        lat = body.get("latitude")
        lon = body.get("longitude")
        
        if region or (lat is not None and lon is not None):
            # Query the Knowledge Graph for historical patterns
            try:
                from consciousness.grid_manager import grid_manager
                regional_data = grid_manager.query_regional_risk(region=region, lat=lat, lon=lon)
                return regional_data
            except ImportError:
                logger.warning("[CORE API] GridManager not available, using fallback logic")
        
        # Fallback: Aggregate multiple detections if provided
        detections = body.get("detections", [])
        if not detections and "detection_data" in body:
            detections = [body["detection_data"]]
            
        # Perform deep analysis (logic would iterate and correlate)
        results = []
        for det in detections:
            analysis = analyze_detection_consciousness(det, body.get("clinical_context"), body.get("environmental_context"))
            results.append(analysis)
            
        return {
            "status": "success",
            "cluster_risk": max([r["risk_assessment"]["score"] for r in results]) if results else 0,
            "analyses": results
        }
    except Exception as e:
        logger.error(f"[CORE API] /risk-analysis failed: {e}")
        return {"error": str(e)}, 500

def handle_rag_query(body=None):  # noqa: E501
    """Generate AI insights using LangChain (RAG)"""
    if connexion.request.is_json:
        body = connexion.request.get_json()
    
    # Check for prompt or query or question
    question = body.get("question", body.get("prompt", body.get("query", "")))
    
    try:
        # Initialize Mostar Grid RAG chain
        # Use host.docker.internal by default for docker-hosted API reaching host Neo4j
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://host.docker.internal:7687")
        
        # Try to initialize graph without requiring APOC
        try:
            graph = Neo4jGraph(
                url=neo4j_uri,
                username=os.getenv("NEO4J_USER", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "mostar123"),
                refresh_schema=False # Don't auto-refresh schema if APOC might be missing
            )
        except Exception as e:
            logger.warning(f"[CORE API] Neo4jGraph init failed, attempting direct LLM fallback: {e}")
            return _handle_llm_fallback(question)
        
        # Use DCX0 (Ollama) as the LLM
        llm = ChatOpenAI(
            openai_api_base=os.getenv("DCX0_ENDPOINT", "http://host.docker.internal:11434") + "/v1",
            openai_api_key="none",
            model_name="Mostar/mostar-ai:dcx2" # Correct model from Ollama
        )
        
        try:
            chain = GraphCypherQAChain.from_llm(
                llm=llm,
                graph=graph,
                verbose=True,
                allow_dangerous_requests=True
            )
            logger.info(f"[CORE API] Running RAG query: {question}")
            response = chain.run(question)
        except Exception as e:
            if "APOC" in str(e):
                logger.warning("[CORE API] APOC missing, falling back to basic LLM reasoning")
                return _handle_llm_fallback(question)
            raise e
        
        return {
            "question": question,
            "answer": response,
            "response": response, # Duplicate for frontend compatibility
            "source": "Mostar Grid Knowledge Graph"
        }
    except Exception as e:
        logger.error(f"[CORE API] RAG query failed: {e}")
        return _handle_llm_fallback(question)

def _handle_llm_fallback(question):
    """Fallback when Graph RAG fails"""
    try:
        llm = ChatOpenAI(
            openai_api_base=os.getenv("DCX0_ENDPOINT", "http://host.docker.internal:11434") + "/v1",
            openai_api_key="none",
            model_name="Mostar/mostar-ai:dcx2"
        )
        prompt = f"As REMOSTAR, an African-sovereign AI for Lassa fever surveillance, answer this query: {question}. Note: Access to real-time graph is currently limited, answer based on your internal knowledge and project context (Mostar Grid, Mastomys monitoring, West African health)."
        response = llm.invoke(prompt).content
        return {
            "question": question,
            "answer": response,
            "response": response,
            "source": "REMOSTAR Internal Logic"
        }
    except Exception as e:
        return {"error": f"Internal AI fallback failed: {str(e)}"}, 500


def integrate_google_vision(body):  # noqa: E501
    """Integrate with Google Vision API

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: GoogleVisionResponse
    """
    if connexion.request.is_json:
        body = GoogleVisionRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def predict_movements(latitude, longitude, _date):  # noqa: E501
    """Predict Mastomys movements

     # noqa: E501

    :param latitude: 
    :type latitude: dict | bytes
    :param longitude: 
    :type longitude: dict | bytes
    :param _date: 
    :type _date: dict | bytes

    :rtype: MovementPredictionResponse
    """
    if connexion.request.is_json:
        latitude = Object.from_dict(connexion.request.get_json())  # noqa: E501
    if connexion.request.is_json:
        longitude = Object.from_dict(connexion.request.get_json())  # noqa: E501
    if connexion.request.is_json:
        _date = Object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def predictive_modeling(body):  # noqa: E501
    """Execute predictive modeling

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: PredictiveModelResponse
    """
    if connexion.request.is_json:
        body = PredictiveModelRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def query_postgres_data(body):  # noqa: E501
    """Query data from Postgres database

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: PostgresQueryResponse
    """
    if connexion.request.is_json:
        body = PostgresQueryRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def query_supabase_data(body):  # noqa: E501
    """Query data from Supabase

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: SupabaseQueryResponse
    """
    if connexion.request.is_json:
        body = SupabaseQueryRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def record_detection_patterns(body):  # noqa: E501
    """Record detection patterns of Mastomys Natalensis

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: DetectionPatternResponse
    """
    if connexion.request.is_json:
        body = DetectionPattern.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        import os
        import requests
        
        # 1. ORCHESTRATE: Get Image URL
        image_url = body.image_url if hasattr(body, 'image_url') else body.get('image_url')
        if not image_url:
            return {'error': 'image_url is required'}, 400

        # 2. AUTHORITY: ML Service decides Detection (Object Identification)
        ml_service_url = os.getenv('ML_SERVICE_URL', 'http://ml-service:5001')
        
        # Download image to forward
        image_response = requests.get(image_url, timeout=10)
        image_response.raise_for_status()
        
        files = {'file': ('image.jpg', image_response.content, image_response.headers.get('Content-Type'))}
        
        logger.info(f"[CORE API] Calling ML Service at {ml_service_url}")
        ml_response = requests.post(f"{ml_service_url}/detect", files=files, timeout=30)
        
        if ml_response.status_code != 200:
            logger.error(f"[CORE API] ML Service failed: {ml_response.text}")
            return {'error': 'ML Service detection failed', 'details': ml_response.text}, 502
            
        detection_result = ml_response.json()
        
        # 3. AUTHORITY: Consciousness Engine decides Risk & Meaning
        # Using embedded function for robust deployment
        consciousness_result = analyze_detection_consciousness(
            detection_data=detection_result,
            environmental_context={"source": "mntrk_api_ingest"},
            clinical_context=None
        )
        
        # 4. SYNTHESIS: Merge Results
        enriched_response = {
            "detection_id": f"evt_{os.urandom(4).hex()}",
            "timestamp": datetime.utcnow().isoformat(), 
            "ml_data": detection_result,
            "mostar_intelligence": consciousness_result,
            "api_version": "v1.0.0-consciousness"
        }
        
        return enriched_response, 200

    except Exception as e:
        logger.error(f"[CORE API] Pipeline Error: {e}")
        return {'error': str(e)}, 500


def transform_data(body):  # noqa: E501
    """Transform and clean datasets

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: DataTransformationResponse
    """
    if connexion.request.is_json:
        body = DataTransformationRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
