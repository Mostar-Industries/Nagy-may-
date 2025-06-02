import firebase_functions as functions
from firebase_admin import initialize_app, firestore
import logging
import requests
import os
import json
from datetime import datetime, timedelta

# Initialize Firebase app
initialize_app()

# Configure logging
logger = functions.logger

@functions.firestore.on_document_created(document="detection_patterns/{documentId}")
def detect_anomalies(event):
    """
    Cloud Function triggered when a new detection pattern is created.
    Analyzes for anomalies and creates alerts if needed.
    """
    try:
        # Get the new document data
        new_detection = event.data.to_dict()
        document_id = event.document.id
        
        # Extract location data
        latitude = new_detection.get('latitude')
        longitude = new_detection.get('longitude')
        
        if not latitude or not longitude:
            logger.warning(f"Missing location data in detection {document_id}")
            return
        
        # Get recent detections in the same area
        db = firestore.client()
        
        # Define the geographic area (rough approximation)
        lat_delta = 0.1  # About 11km
        lon_delta = 0.1  # Varies by latitude
        
        # Query for recent detections in the area
        week_ago = datetime.now() - timedelta(days=7)
        
        area_detections = db.collection('detection_patterns').where(
            'latitude', '>=', latitude - lat_delta
        ).where(
            'latitude', '<=', latitude + lat_delta
        ).where(
            'detection_timestamp', '>=', week_ago
        ).get()
        
        # Filter by longitude (Firestore can't do multiple range queries)
        filtered_detections = [
            d.to_dict() for d in area_detections 
            if abs(d.to_dict().get('longitude', 0) - longitude) <= lon_delta
        ]
        
        # Check for anomalies
        if len(filtered_detections) >= 5:  # Threshold for potential outbreak
            # Calculate average confidence score
            confidence_scores = [d.get('confidence_score', 0) for d in filtered_detections]
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            # If high confidence and multiple detections, create an alert
            if avg_confidence > 0.7:
                # Create an outbreak alert
                alert_ref = db.collection('outbreak_alerts').document()
                alert_ref.set({
                    'alert_type': 'population_spike',
                    'severity_level': 3,  # Medium severity
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius_km': 10,
                    'description': f"Potential Mastomys population spike detected with {len(filtered_detections)} observations in the last week",
                    'status': 'active',
                    'alert_timestamp': firestore.SERVER_TIMESTAMP,
                    'resolved_timestamp': None,
                    'metadata': {
                        'detection_count': len(filtered_detections),
                        'avg_confidence': avg_confidence,
                        'triggering_detection_id': document_id
                    },
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                
                logger.info(f"Created outbreak alert: {alert_ref.id}")
                
                # Send notification if configured
                notification_url = os.environ.get('NOTIFICATION_WEBHOOK_URL')
                if notification_url:
                    requests.post(
                        notification_url,
                        json={
                            'type': 'outbreak_alert',
                            'severity': 3,
                            'message': f"Potential Mastomys population spike detected near {latitude}, {longitude}",
                            'location': {'latitude': latitude, 'longitude': longitude},
                            'alert_id': alert_ref.id
                        }
                    )
    
    except Exception as e:
        logger.error(f"Error in detect_anomalies: {e}")
