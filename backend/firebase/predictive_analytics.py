from firebase.client import get_firestore
from firebase_admin import firestore
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Configure logging
logger = logging.getLogger(__name__)

# Collection name
COLLECTION = 'ai_predictions'

# Schema validation
REQUIRED_FIELDS = ['prediction_type', 'input_data', 'prediction_result']

def validate_ai_prediction(data: Dict[str, Any]) -> bool:
    """Validate AI prediction data against schema."""
    for field in REQUIRED_FIELDS:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Type validation
    if not isinstance(data.get('prediction_type'), str):
        logger.error("Prediction type must be a string")
        return False
    
    if not isinstance(data.get('input_data'), dict):
        logger.error("Input data must be a dictionary")
        return False
    
    if not isinstance(data.get('prediction_result'), dict):
        logger.error("Prediction result must be a dictionary")
        return False
    
    return True

def create_ai_prediction(data: Dict[str, Any]) -> str:
    """Create a new AI prediction in Firestore."""
    try:
        # Validate data
        if not validate_ai_prediction(data):
            raise ValueError("Invalid AI prediction data")
        
        # Get Firestore client
        db = get_firestore()
        
        # Add timestamps
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['prediction_timestamp'] = data.get('prediction_timestamp', firestore.SERVER_TIMESTAMP)
        
        # Create document with auto-generated ID
        doc_ref = db.collection(COLLECTION).document()
        doc_ref.set(data)
        
        logger.info(f"Created AI prediction with ID: {doc_ref.id}")
        return doc_ref.id
    
    except Exception as e:
        logger.error(f"Failed to create AI prediction: {e}")
        raise

def get_ai_prediction(prediction_id: str) -> Optional[Dict[str, Any]]:
    """Get an AI prediction by ID."""
    try:
        db = get_firestore()
        doc = db.collection(COLLECTION).document(prediction_id).get()
        
        if not doc.exists:
            logger.warning(f"AI prediction not found: {prediction_id}")
            return None
        
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    
    except Exception as e:
        logger.error(f"Failed to get AI prediction: {e}")
        raise

def query_ai_predictions(
    prediction_type: Optional[str] = None,
    limit: int = 100,
    order_by: str = 'prediction_timestamp',
    direction: str = 'desc'
) -> List[Dict[str, Any]]:
    """Query AI predictions by type."""
    try:
        db = get_firestore()
        
        # Start with base query
        query = db.collection(COLLECTION)
        
        # Apply prediction type filter if provided
        if prediction_type:
            query = query.where('prediction_type', '==', prediction_type)
        
        # Apply ordering
        dir_method = firestore.Query.DESCENDING if direction.lower() == 'desc' else firestore.Query.ASCENDING
        query = query.order_by(order_by, direction=dir_method)
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query
        docs = query.stream()
        
        # Process results
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        
        return results
    
    except Exception as e:
        logger.error(f"Failed to query AI predictions: {e}")
        raise

def get_prediction_metrics(prediction_type: str) -> Dict[str, Any]:
    """Get metrics for a specific prediction type."""
    try:
        # Get recent predictions of the specified type
        predictions = query_ai_predictions(prediction_type=prediction_type, limit=100)
        
        if not predictions:
            return {
                'count': 0,
                'avg_confidence': None,
                'prediction_type': prediction_type
            }
        
        # Calculate metrics
        confidence_scores = [
            p.get('confidence_score', 0) 
            for p in predictions 
            if 'confidence_score' in p
        ]
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
        else:
            avg_confidence = None
        
        return {
            'count': len(predictions),
            'avg_confidence': avg_confidence,
            'prediction_type': prediction_type,
            'latest_timestamp': predictions[0].get('prediction_timestamp')
        }
    
    except Exception as e:
        logger.error(f"Failed to get prediction metrics: {e}")
        raise
