"""
MNTRK Sovereign Observatory - Database Management
Handles Firebase Firestore and Neon PostgreSQL connections
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from flask import current_app
from datetime import datetime, timezone
import logging

logger = logging.getLogger("Database")

# Global variable to store the Firestore client
_firestore_client = None

def init_db(app):
    """Initialize Firebase Admin SDK and Firestore client."""
    global _firestore_client
    
    try:
        # Get Firebase credentials from environment variable
        firebase_creds_path = app.config.get('FIREBASE_CREDENTIALS')
        
        if not firebase_creds_path:
            if app.config.get('DEBUG'):
                app.logger.warning("FIREBASE_CREDENTIALS not set. Using default credentials in debug mode.")
                cred = credentials.ApplicationDefault()
            else:
                raise ValueError("FIREBASE_CREDENTIALS environment variable is required in production")
        else:
            # Use service account credentials
            if os.path.exists(firebase_creds_path):
                cred = credentials.Certificate(firebase_creds_path)
            else:
                # Assume it's a JSON string (for environment variables containing JSON)
                import json
                cred_dict = json.loads(firebase_creds_path)
                cred = credentials.Certificate(cred_dict)
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            app.logger.info("Firebase Admin SDK initialized successfully")
        
        # Initialize Firestore client
        _firestore_client = firestore.client()
        app.logger.info("Firestore client initialized successfully")
        
    except Exception as e:
        app.logger.error(f"Failed to initialize Firebase/Firestore: {e}")
        if not app.config.get('DEBUG'):
            raise
        else:
            app.logger.warning("Continuing in debug mode without Firebase connection")

def get_db():
    """Get the Firestore client instance."""
    global _firestore_client
    
    if _firestore_client is None:
        if current_app and current_app.config.get('DEBUG'):
            current_app.logger.warning("Firestore client not initialized. This might be expected in test/debug mode.")
        raise RuntimeError("Firestore client not initialized. Call init_db() first.")
    
    return _firestore_client

# Firebase Firestore operations
def create_detection_pattern(data: dict):
    """Create a new detection pattern record in Firestore."""
    try:
        db = get_db()
        
        # Add server timestamp
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Create document with auto-generated ID
        doc_ref = db.collection('detection_patterns').document()
        doc_ref.set(data)
        
        return doc_ref.id
    except Exception as e:
        logger.error(f"Failed to create detection pattern: {e}")
        raise

def create_habitat_analysis(data: dict):
    """Create a new habitat analysis record in Firestore."""
    try:
        db = get_db()
        
        # Add server timestamp
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Create document with auto-generated ID
        doc_ref = db.collection('habitat_analyses').document()
        doc_ref.set(data)
        
        return doc_ref.id
    except Exception as e:
        logger.error(f"Failed to create habitat analysis: {e}")
        raise

def create_ai_prediction(data: dict):
    """Create a new AI prediction record in Firestore."""
    try:
        db = get_db()
        
        # Add server timestamp
        data['created_at'] = firestore.SERVER_TIMESTAMP
        
        # Create document with auto-generated ID
        doc_ref = db.collection('ai_predictions').document()
        doc_ref.set(data)
        
        return doc_ref.id
    except Exception as e:
        logger.error(f"Failed to create AI prediction: {e}")
        raise

def query_recent_detections(limit: int = 10):
    """Query recent detection patterns from Firestore."""
    try:
        db = get_db()
        
        # Query recent detections ordered by timestamp
        docs = db.collection('detection_patterns')\
                .order_by('detection_timestamp', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        
        return results
    except Exception as e:
        logger.error(f"Failed to query recent detections: {e}")
        raise

def query_habitat_analyses_by_region(latitude: float, longitude: float, radius_km: float = 10, limit: int = 20):
    """Query habitat analyses within a geographic region."""
    try:
        db = get_db()
        
        # For geographic queries, we'll use a simple bounding box approach
        # In production, you might want to use more sophisticated geospatial queries
        lat_delta = radius_km / 111.0  # Rough conversion: 1 degree ≈ 111 km
        lon_delta = radius_km / (111.0 * abs(latitude))  # Adjust for latitude
        
        docs = db.collection('habitat_analyses')\
                .where('latitude', '>=', latitude - lat_delta)\
                .where('latitude', '&lt;=', latitude + lat_delta)\
                .order_by('analysis_timestamp', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            # Additional longitude filtering
            if abs(data.get('longitude', 0) - longitude) &lt;= lon_delta:
                results.append(data)
        
        return results
    except Exception as e:
        logger.error(f"Failed to query habitat analyses: {e}")
        raise

def get_detection_pattern_by_id(detection_id: str):
    """Get a specific detection pattern by ID."""
    try:
        db = get_db()
        doc = db.collection('detection_patterns').document(detection_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to get detection pattern: {e}")
        raise

def update_detection_pattern(detection_id: str, update_data: dict):
    """Update a detection pattern record."""
    try:
        db = get_db()
        
        # Add update timestamp
        update_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Update document
        db.collection('detection_patterns').document(detection_id).update(update_data)
        
        return True
    except Exception as e:
        logger.error(f"Failed to update detection pattern: {e}")
        raise

def delete_detection_pattern(detection_id: str):
    """Delete a detection pattern record."""
    try:
        db = get_db()
        db.collection('detection_patterns').document(detection_id).delete()
        return True
    except Exception as e:
        logger.error(f"Failed to delete detection pattern: {e}")
        raise
