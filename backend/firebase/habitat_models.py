from firebase.client import get_firestore
from firebase_admin import firestore
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Configure logging
logger = logging.getLogger(__name__)

# Collection name
COLLECTION = 'habitat_analyses'

# Schema validation
REQUIRED_FIELDS = ['latitude', 'longitude', 'suitability_score']

def validate_habitat_analysis(data: Dict[str, Any]) -> bool:
    """Validate habitat analysis data against schema."""
    for field in REQUIRED_FIELDS:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Type validation
    if not isinstance(data.get('latitude'), (int, float)):
        logger.error("Latitude must be a number")
        return False
    
    if not isinstance(data.get('longitude'), (int, float)):
        logger.error("Longitude must be a number")
        return False
    
    if not isinstance(data.get('suitability_score'), (int, float)):
        logger.error("Suitability score must be a number")
        return False
    
    return True

def create_habitat_analysis(data: Dict[str, Any]) -> str:
    """Create a new habitat analysis in Firestore."""
    try:
        # Validate data
        if not validate_habitat_analysis(data):
            raise ValueError("Invalid habitat analysis data")
        
        # Get Firestore client
        db = get_firestore()
        
        # Add timestamps
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Create document with auto-generated ID
        doc_ref = db.collection(COLLECTION).document()
        doc_ref.set(data)
        
        logger.info(f"Created habitat analysis with ID: {doc_ref.id}")
        return doc_ref.id
    
    except Exception as e:
        logger.error(f"Failed to create habitat analysis: {e}")
        raise

def get_habitat_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Get a habitat analysis by ID."""
    try:
        db = get_firestore()
        doc = db.collection(COLLECTION).document(analysis_id).get()
        
        if not doc.exists:
            logger.warning(f"Habitat analysis not found: {analysis_id}")
            return None
        
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    
    except Exception as e:
        logger.error(f"Failed to get habitat analysis: {e}")
        raise

def update_habitat_analysis(analysis_id: str, data: Dict[str, Any]) -> bool:
    """Update a habitat analysis."""
    try:
        db = get_firestore()
        
        # Add updated timestamp
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Update document
        db.collection(COLLECTION).document(analysis_id).update(data)
        
        logger.info(f"Updated habitat analysis: {analysis_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to update habitat analysis: {e}")
        raise

def delete_habitat_analysis(analysis_id: str) -> bool:
    """Delete a habitat analysis."""
    try:
        db = get_firestore()
        db.collection(COLLECTION).document(analysis_id).delete()
        
        logger.info(f"Deleted habitat analysis: {analysis_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to delete habitat analysis: {e}")
        raise

def query_habitat_analyses(
    limit: int = 100,
    order_by: str = 'created_at',
    direction: str = 'desc',
    filters: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """Query habitat analyses with filters."""
    try:
        db = get_firestore()
        
        # Start with base query
        query = db.collection(COLLECTION)
        
        # Apply filters if provided
        if filters:
            for filter_dict in filters:
                field = filter_dict.get('field')
                op = filter_dict.get('op')
                value = filter_dict.get('value')
                
                if field and op and value is not None:
                    query = query.where(field, op, value)
        
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
        logger.error(f"Failed to query habitat analyses: {e}")
        raise

def get_habitat_suitability_by_region(
    latitude: float,
    longitude: float,
    radius_km: float = 10
) -> Dict[str, Any]:
    """Get habitat suitability statistics for a region."""
    try:
        # Get habitat analyses in the region
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(latitude))
        
        filters = [
            {'field': 'latitude', 'op': '>=', 'value': latitude - lat_delta},
            {'field': 'latitude', 'op': '<=', 'value': latitude + lat_delta}
        ]
        
        analyses = query_habitat_analyses(limit=1000, filters=filters)
        
        # Filter by longitude
        filtered_analyses = [
            a for a in analyses 
            if abs(a.get('longitude', 0) - longitude) <= lon_delta
        ]
        
        # Calculate statistics
        if not filtered_analyses:
            return {
                'count': 0,
                'avg_suitability': None,
                'min_suitability': None,
                'max_suitability': None,
                'region': {
                    'center': {'latitude': latitude, 'longitude': longitude},
                    'radius_km': radius_km
                }
            }
        
        suitability_scores = [a.get('suitability_score', 0) for a in filtered_analyses]
        
        return {
            'count': len(filtered_analyses),
            'avg_suitability': sum(suitability_scores) / len(suitability_scores),
            'min_suitability': min(suitability_scores),
            'max_suitability': max(suitability_scores),
            'region': {
                'center': {'latitude': latitude, 'longitude': longitude},
                'radius_km': radius_km
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get habitat suitability by region: {e}")
        raise
