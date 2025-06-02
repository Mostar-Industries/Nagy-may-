import firebase_functions as functions
from firebase_admin import initialize_app, firestore
import logging
import requests
import os
import json

# Initialize Firebase app
initialize_app()

# Configure logging
logger = functions.logger

@functions.firestore.on_document_created(document="detection_patterns/{documentId}")
def trigger_ml_retraining(event):
    """
    Cloud Function triggered when a new detection pattern is created.
    Triggers ML model retraining when enough new data is available.
    """
    try:
        # Get the new document data
        new_detection = event.data.to_dict()
        
        # Check if we need to retrain (e.g., every 10 new detections)
        db = firestore.client()
        
        # Get the ML model metadata
        model_meta_ref = db.collection('ml_models').document('habitat_predictor')
        model_meta = model_meta_ref.get()
        
        if not model_meta.exists:
            # Initialize model metadata if it doesn't exist
            model_meta_ref.set({
                'last_trained': firestore.SERVER_TIMESTAMP,
                'version': '1.0.0',
                'new_data_count': 1,
                'total_data_count': 1,
                'accuracy': 0.0,
                'status': 'initialized'
            })
            logger.info("Initialized ML model metadata")
            return
        
        # Get current metadata
        meta_data = model_meta.to_dict()
        new_count = meta_data.get('new_data_count', 0) + 1
        
        # Update the new data count
        model_meta_ref.update({
            'new_data_count': new_count
        })
        
        # Check if we should trigger retraining
        retrain_threshold = int(os.environ.get('ML_RETRAIN_THRESHOLD', '10'))
        
        if new_count >= retrain_threshold:
            # Trigger retraining by calling the ML API
            api_url = os.environ.get('ML_API_URL')
            api_key = os.environ.get('ML_API_KEY')
            
            if not api_url or not api_key:
                logger.error("ML_API_URL or ML_API_KEY environment variables not set")
                return
            
            # Call the ML API to trigger retraining
            response = requests.post(
                f"{api_url}/api/modeling/retrain",
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model_id': 'habitat_predictor',
                    'force': True
                }
            )
            
            if response.status_code == 200:
                # Update model metadata
                model_meta_ref.update({
                    'last_trained': firestore.SERVER_TIMESTAMP,
                    'new_data_count': 0,
                    'status': 'retraining'
                })
                logger.info(f"Triggered ML model retraining: {response.json()}")
            else:
                logger.error(f"Failed to trigger ML model retraining: {response.status_code} - {response.text}")
    
    except Exception as e:
        logger.error(f"Error in trigger_ml_retraining: {e}")
