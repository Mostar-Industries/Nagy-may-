import firebase_functions as functions
from firebase_admin import initialize_app
import asyncio
import logging
import sys
import os
import json

# Add the project root to Python path
sys.path.append('/workspace')

from ml_pipeline.orchestrator import trigger_scheduled_training, trigger_full_training

# Initialize Firebase app
initialize_app()

logger = functions.logger

@functions.firestore.on_document_created(document="training_triggers/{documentId}")
def on_training_trigger_created(event):
    """Triggered when a new training trigger document is created."""
    try:
        # Get trigger data
        trigger_data = event.data.to_dict() if event.data else {}
        trigger_type = trigger_data.get('type', 'scheduled')
        
        logger.info(f"Training trigger received: {trigger_type}")
        
        # Run the appropriate training function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if trigger_type == 'full':
            result = loop.run_until_complete(trigger_full_training())
        else:
            result = loop.run_until_complete(trigger_scheduled_training())
        
        loop.close()
        
        # Update the trigger document with results
        if event.document:
            event.document.reference.update({
                'status': 'completed',
                'results': result,
                'completed_at': functions.firestore.server_timestamp()
            })
        
        logger.info(f"Training completed: {json.dumps(result)}")
        
    except Exception as e:
        logger.error(f"Error in training trigger: {e}")
        
        # Update document with error
        if event.document:
            event.document.reference.update({
                'status': 'error',
                'error': str(e),
                'completed_at': functions.firestore.server_timestamp()
            })

@functions.pubsub.on_schedule(schedule="every 24 hours")
def scheduled_training_job(event):
    """Daily scheduled training job."""
    try:
        logger.info("Running daily scheduled training")
        
        # Run the scheduled training
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(trigger_scheduled_training())
        loop.close()
        
        # Log results
        logger.info(f"Scheduled training completed: {json.dumps(result)}")
        
        # Create a record in Firestore
        from firebase_admin import firestore
        db = firestore.client()
        
        db.collection('training_history').add({
            'type': 'scheduled',
            'status': 'completed',
            'results': result,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
    except Exception as e:
        logger.error(f"Error in scheduled training job: {e}")
        
        # Log error in Firestore
        from firebase_admin import firestore
        db = firestore.client()
        
        db.collection('training_history').add({
            'type': 'scheduled',
            'status': 'error',
            'error': str(e),
            'timestamp': firestore.SERVER_TIMESTAMP
        })

@functions.https.on_request
def manual_training_trigger(req):
    """Manual endpoint to trigger training."""
    try:
        # Get parameters
        model_type = req.args.get('model_type', 'all')
        force_full = req.args.get('force_full', 'false').lower() == 'true'
        
        logger.info(f"Manual training trigger: model_type={model_type}, force_full={force_full}")
        
        # Run the appropriate training function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if force_full or model_type == 'all':
            result = loop.run_until_complete(trigger_full_training())
        else:
            # Create a specific model training function if needed
            result = {"error": "Single model training not implemented"}
        
        loop.close()
        
        return functions.https.Response(
            json.dumps(result),
            status=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Error in manual training trigger: {e}")
        
        return functions.https.Response(
            json.dumps({"status": "error", "error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"}
        )
