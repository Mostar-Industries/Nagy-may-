from flask import Blueprint, request, jsonify
from ..services.ai_service import AIService
from flask_jwt_extended import jwt_required

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/predict/movement', methods=['POST'])
@jwt_required() # AI predictions should likely be protected
def ai_predict_movement():
    data = request.get_json()
    result, status_code = AIService.predict_movement(data)
    return jsonify(result), status_code

@ai_bp.route('/predict/habitat', methods=['POST'])
@jwt_required()
def ai_predict_habitat():
    data = request.get_json()
    result, status_code = AIService.predict_habitat(data)
    return jsonify(result), status_code

@ai_bp.route('/models', methods=['GET'])
@jwt_required()
def ai_list_models():
    result, status_code = AIService.list_models()
    return jsonify(result), status_code
