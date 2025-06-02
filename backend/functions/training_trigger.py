import firebase_functions as functions
from firebase_admin import initialize_app
import asyncio
import logging
import sys
import os

# Add the project root to Python path
sys.path.append('/workspace')

from ml_pipeline.training_manager import trigger_training_check

# Initialize Firebase app
initialize_app()

logger = functions.logger

@functions.firestore.on_document_created(document="detection_patterns/{documentId}")
def on_detection_created(event):
    """Triggered when a new detection pattern is created."""
    try:
        logger.info("New detection pattern created, checking training triggers")
        
        # Run the async training check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(trigger_training_check())
        loop.close()
        
        logger.info("Training trigger check completed")
        
    except Exception as e:
        logger.error(f"Error in detection pattern trigger: {e}")

@functions.firestore.on_document_created(document="habitat_analyses/{documentId}")
def on_habitat_created(event):
    """Triggered when a new habitat analysis is created."""
    try:
        logger.info("New habitat analysis created, checking training triggers")
        
        # Run the async training check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(trigger_training_check())
        loop.close()
        
        logger.info("Training trigger check completed")
        
    except Exception as e:
        logger.error(f"Error in habitat analysis trigger: {e}")

@functions.firestore.on_document_created(document="environmental_data/{documentId}")
def on_environmental_data_created(event):
    """Triggered when new environmental data is created."""
    try:
        logger.info("New environmental data created, checking training triggers")
        
        # Run the async training check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(trigger_training_check())
        loop.close()
        
        logger.info("Training trigger check completed")
        
    except Exception as e:
        logger.error(f"Error in environmental data trigger: {e}")

@functions.https.on_request
def manual_training_trigger(req):
    """Manual endpoint to trigger training."""
    try:
        model_type = req.args.get('model_type', 'all')
        
        logger.info(f"Manual training trigger for: {model_type}")
        
        # Run the async training check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(trigger_training_check())
        loop.close()
        
        return {'status': 'success', 'message': f'Training triggered for {model_type}'}
        
    except Exception as e:
        logger.error(f"Error in manual training trigger: {e}")
        return {'status': 'error', 'message': str(e)}, 500
