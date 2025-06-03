from flask import Blueprint, request, jsonify
from ..services.ingestion_service import IngestionService # Agents might also use ingestion service
from flask_jwt_extended import jwt_required # Secure agent telemetry endpoint

agents_bp = Blueprint('agents_bp', __name__)

@agents_bp.route('/telemetry', methods=['POST'])
# @jwt_required() # Protect this endpoint, agents should authenticate
def agent_telemetry():
    data = request.get_json()
    # Here, you might want to add agent-specific processing or validation
    # For now, we'll assume telemetry data is similar to detection data
    # and can be stored by the IngestionService.
    # You might want a dedicated AgentService or enrich data here.
    if not data or not data.get('latitude') or not data.get('longitude'):
        return jsonify({'error': 'Missing required fields for telemetry'}), 400
    
    # Add a default source if not provided, or use agent ID from JWT
    data.setdefault('source', data.get('agent_id', 'unknown_agent'))

    result, status_code = IngestionService.store_detection(data)
    return jsonify(result), status_code

@agents_bp.route('/status', methods=['GET'])
# @jwt_required() # If only authenticated users can see agent statuses
def get_agent_statuses():
    # Placeholder for agent status logic
    # This might involve querying a different table or an in-memory store
    return jsonify([
        {"agent_id": "agent_001", "status": "online", "last_seen": "2024-06-03T10:00:00Z", "battery": "85%"},
        {"agent_id": "agent_002", "status": "offline", "last_seen": "2024-06-02T15:30:00Z", "battery": "20%"}
    ]), 200
