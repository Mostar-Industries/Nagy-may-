from flask import Blueprint, request, jsonify
from ml_pipeline.orchestrator import orchestrator
import asyncio
import logging

logger = logging.getLogger(__name__)

training_bp = Blueprint('training', __name__)

@training_bp.route('/training/status', methods=['GET'])
async def get_training_status():
    """Get current training status and schedule."""
    try:
        # Get database reference
        db = orchestrator.db
        
        # Get training schedule
        schedule_ref = db.collection('training_schedule').document('schedule')
        schedule_doc = schedule_ref.get()
        schedule = schedule_doc.to_dict() if schedule_doc.exists else {}
        
        # Get recent training history
        history_ref = db.collection('training_history').order_by(
            'timestamp', direction='DESCENDING'
        ).limit(10)
        history_docs = history_ref.stream()
        history = [doc.to_dict() for doc in history_docs]
        
        # Get model registry
        registry_ref = db.collection('model_registry').order_by(
            'created_at', direction='DESCENDING'
        ).limit(10)
        registry_docs = registry_ref.stream()
        registry = [doc.to_dict() for doc in registry_docs]
        
        # Check which models need training
        training_needed = await orchestrator.check_training_schedule()
        
        return jsonify({
            'status': 'success',
            'schedule': schedule,
            'history': history,
            'registry': registry,
            'training_needed': training_needed
        })
        
    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@training_bp.route('/training/trigger', methods=['POST'])
async def trigger_training():
    """Manually trigger model training."""
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'all')
        force_full = data.get('force_full', False)
        
        if model_type == 'all' or force_full:
            # Run full training cycle
            results = await orchestrator.run_full_training_cycle()
        else:
            # Train specific model
            results = await orchestrator.execute_training(model_type)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error triggering training: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@training_bp.route('/training/schedule', methods=['POST'])
async def update_schedule():
    """Update training schedule."""
    try:
        data = request.get_json()
        
        # Get database reference
        db = orchestrator.db
        schedule_ref = db.collection('training_schedule').document('schedule')
        
        # Update schedule
        schedule_ref.set(data, merge=True)
        
        return jsonify({
            'status': 'success',
            'message': 'Training schedule updated'
        })
        
    except Exception as e:
        logger.error(f"Error updating training schedule: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@training_bp.route('/training/models', methods=['GET'])
async def list_models():
    """List available trained models."""
    try:
        # Get database reference
        db = orchestrator.db
        
        # Get model registry
        registry_ref = db.collection('model_registry').order_by('created_at', direction='DESCENDING')
        registry_docs = registry_ref.stream()
        
        models = []
        for doc in registry_docs:
            model_data = doc.to_dict()
            model_data['id'] = doc.id
            models.append(model_data)
        
        return jsonify({
            'status': 'success',
            'models': models
        })
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@training_bp.route('/training/models/<model_id>', methods=['GET'])
async def get_model(model_id):
    """Get details for a specific model."""
    try:
        # Get database reference
        db = orchestrator.db
        
        # Get model document
        model_ref = db.collection('model_registry').document(model_id)
        model_doc = model_ref.get()
        
        if not model_doc.exists:
            return jsonify({'status': 'error', 'message': 'Model not found'}), 404
        
        model_data = model_doc.to_dict()
        model_data['id'] = model_doc.id
        
        return jsonify({
            'status': 'success',
            'model': model_data
        })
        
    except Exception as e:
        logger.error(f"Error getting model: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
