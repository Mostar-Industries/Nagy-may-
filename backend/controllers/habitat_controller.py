from flask import request, jsonify, current_app
from shared.database import create_habitat_analysis, query_habitat_analyses_by_region
from shared.utils import (
    validate_coordinates, 
    calculate_habitat_suitability_score,
    format_api_response
)
from ml_pipeline.pipeline import get_pipeline
from api.auth import require_auth, get_current_user
from google.cloud import firestore

@require_auth
def analyze_habitats():
    """
    Analyze environmental data for habitat prediction.
    Implements the /api/habitats POST endpoint.
    """
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Validate required fields
        required_fields = ['environmental_data', 'geographic_coordinates']
        for field in required_fields:
            if field not in data:
                return jsonify(format_api_response(
                    None, 'error', f'Missing required field: {field}'
                )), 400
        
        # Extract coordinates
        coords = data['geographic_coordinates']
        if not validate_coordinates(coords.get('latitude'), coords.get('longitude')):
            return jsonify(format_api_response(
                None, 'error', 'Invalid coordinates'
            )), 400
        
        # Get ML pipeline and make prediction
        pipeline = get_pipeline()
        prediction_result = pipeline.predict_habitat_suitability(data['environmental_data'])
        
        # Calculate additional metrics
        suitability_score = calculate_habitat_suitability_score(data['environmental_data'])
        
        # Prepare analysis data for Firebase
        analysis_data = {
            'user_id': current_user['user_id'],
            'latitude': coords['latitude'],
            'longitude': coords['longitude'],
            'suitability_score': suitability_score,
            'environmental_data': data['environmental_data'],
            'analysis_parameters': data.get('analysis_parameters', {}),
            'satellite_image_url': data.get('satellite_data'),
            'analysis_timestamp': firestore.SERVER_TIMESTAMP
        }
        
        # Store in Firebase Firestore
        analysis_id = create_habitat_analysis(analysis_data)
        
        # Prepare response
        response_data = {
            'id': analysis_id,
            'suitability_score': suitability_score,
            'ml_prediction': prediction_result,
            'risk_factors': prediction_result.get('risk_factors', []),
            'environmental_context': data['environmental_data'],
            'coordinates': coords
        }
        
        current_app.logger.info(f"Habitat analysis completed for user {current_user['user_id']}")
        
        return jsonify(format_api_response(
            response_data, 'success', 'Habitat analysis completed successfully'
        ))
        
    except Exception as e:
        current_app.logger.error(f"Habitat analysis failed: {str(e)}")
        return jsonify(format_api_response(
            None, 'error', f'Analysis failed: {str(e)}'
        )), 500

def get_habitat_history(latitude: float, longitude: float, radius_km: float = 10):
    """Get historical habitat analysis data for a region."""
    try:
        # Query Firebase for historical data
        results = query_habitat_analyses_by_region(latitude, longitude, radius_km)
        
        return jsonify(format_api_response(
            results, 'success', f'Retrieved {len(results)} habitat analyses'
        ))
        
    except Exception as e:
        current_app.logger.error(f"Failed to get habitat history: {str(e)}")
        return jsonify(format_api_response(None, 'error', str(e))), 500
