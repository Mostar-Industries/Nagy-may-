from firebase.client import get_firestore
from firebase_admin import firestore
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Configure logging
logger = logging.getLogger(__name__)

# Collection name
COLLECTION = 'detection_patterns'

# Schema validation
REQUIRED_FIELDS = ['latitude', 'longitude', 'detection_timestamp', 'confidence_score']

def validate_detection_pattern(data: Dict[str, Any]) -> bool:
    """Validate detection pattern data against schema."""
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
    
    if not isinstance(data.get('confidence_score'), (int, float)):
        logger.error("Confidence score must be a number")
        return False
    
    return True

def create_detection_pattern(data: Dict[str, Any]) -> str:
    """Create a new detection pattern in Firestore."""
    try:
        # Validate data
        if not validate_detection_pattern(data):
            raise ValueError("Invalid detection pattern data")
        
        # Get Firestore client
        db = get_firestore()
        
        # Add timestamps
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Create document with auto-generated ID
        doc_ref = db.collection(COLLECTION).document()
        doc_ref.set(data)
        
        logger.info(f"Created detection pattern with ID: {doc_ref.id}")
        return doc_ref.id
    
    except Exception as e:
        logger.error(f"Failed to create detection pattern: {e}")
        raise

def get_detection_pattern(pattern_id: str) -> Optional[Dict[str, Any]]:
    """Get a detection pattern by ID."""
    try:
        db = get_firestore()
        doc = db.collection(COLLECTION).document(pattern_id).get()
        
        if not doc.exists:
            logger.warning(f"Detection pattern not found: {pattern_id}")
            return None
        
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    
    except Exception as e:
        logger.error(f"Failed to get detection pattern: {e}")
        raise

def update_detection_pattern(pattern_id: str, data: Dict[str, Any]) -> bool:
    """Update a detection pattern."""
    try:
        db = get_firestore()
        
        # Add updated timestamp
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Update document
        db.collection(COLLECTION).document(pattern_id).update(data)
        
        logger.info(f"Updated detection pattern: {pattern_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to update detection pattern: {e}")
        raise

def delete_detection_pattern(pattern_id: str) -> bool:
    """Delete a detection pattern."""
    try:
        db = get_firestore()
        db.collection(COLLECTION).document(pattern_id).delete()
        
        logger.info(f"Deleted detection pattern: {pattern_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to delete detection pattern: {e}")
        raise

def query_detection_patterns(
    limit: int = 100,
    order_by: str = 'detection_timestamp',
    direction: str = 'desc',
    filters: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """Query detection patterns with filters."""
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
        logger.error(f"Failed to query detection patterns: {e}")
        raise

def get_detection_patterns_by_region(
    latitude: float,
    longitude: float,
    radius_km: float = 10,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get detection patterns within a geographic region."""
    try:
        # For Firestore, we'll use a simple bounding box approach
        # In production, you might want to use Geohashing or GeoFirestore
        lat_delta = radius_km / 111.0  # Rough conversion: 1 degree ≈ 111 km
        lon_delta = radius_km / (111.0 * abs(latitude))  # Adjust for latitude
        
        # Query patterns within latitude range
        filters = [
            {'field': 'latitude', 'op': '>=', 'value': latitude - lat_delta},
            {'field': 'latitude', 'op': '<=', 'value': latitude + lat_delta}
        ]
        
        # Get patterns
        patterns = query_detection_patterns(limit=limit, filters=filters)
        
        # Filter by longitude (can't do this directly in Firestore query due to limitations)
        filtered_patterns = [
            p for p in patterns 
            if abs(p.get('longitude', 0) - longitude) <= lon_delta
        ]
        
        return filtered_patterns
    
    except Exception as e:
        logger.error(f"Failed to get detection patterns by region: {e}")
        raise
