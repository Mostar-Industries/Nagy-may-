from flask import Blueprint, request, jsonify
from ..services.omniverse_service import OmniverseService
from flask_jwt_extended import jwt_required

omniverse_bp = Blueprint('omniverse_bp', __name__)

@omniverse_bp.route('/control', methods=['POST'])
@jwt_required() # Omniverse control should be protected
def omniverse_control():
    action_data = request.get_json()
    if not action_data or not action_data.get('action'):
        return jsonify({'error': 'Missing action field'}), 400
    result, status_code = OmniverseService.control_simulation(action_data)
    return jsonify(result), status_code

@omniverse_bp.route('/status', methods=['GET'])
@jwt_required() # Omniverse status might also be protected
def omniverse_status():
    result, status_code = OmniverseService.get_status()
    return jsonify(result), status_code
