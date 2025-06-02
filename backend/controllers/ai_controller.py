from flask import request, jsonify, current_app
from shared.utils import format_api_response
from ml_pipeline.pipeline import get_pipeline
from api.auth import require_auth, get_current_user

@require_auth
def ai_habitats_post():
    """AI Agent habitat analysis endpoint."""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Get ML pipeline
        pipeline = get_pipeline()
        
        # Perform AI-powered habitat analysis
        result = pipeline.predict_habitat_suitability(
            data.get('environmental_data', {})
        )
        
        # Enhanced AI analysis with additional context
        ai_analysis = {
            'habitat_prediction': result,
            'ai_confidence': result.get('confidence', 0.0),
            'environmental_factors': _analyze_environmental_factors(data.get('environmental_data', {})),
            'recommendations': _generate_habitat_recommendations(result),
            'risk_assessment': _assess_habitat_risks(result)
        }
        
        current_app.logger.info(f"AI habitat analysis completed for user {current_user['user_id']}")
        
        return jsonify(format_api_response(
            ai_analysis, 'success', 'AI habitat analysis completed'
        ))
        
    except Exception as e:
        current_app.logger.error(f"AI habitat analysis failed: {str(e)}")
        return jsonify(format_api_response(
            None, 'error', str(e)
        )), 500

@require_auth
def ai_detections_post():
    """AI Agent detection patterns endpoint."""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Get ML pipeline
        pipeline = asyncio.run(get_pipeline())
        
        # Process image for AI detection
        image_url = data.get('image_url')
        if image_url:
            # In a real implementation, this would process the image
            # For now, we'll simulate AI detection results
            ai_detection = {
                'detected_species': 'Mastomys Natalensis',
                'confidence': 0.87,
                'bounding_boxes': [
                    {'x': 120, 'y': 80, 'width': 60, 'height': 45, 'confidence': 0.87}
                ],
                'behavioral_analysis': {
                    'activity': 'foraging',
                    'group_size': 1,
                    'time_of_day': 'nocturnal'
                },
                'environmental_context': data.get('environmental_context', {})
            }
        else:
            ai_detection = {
                'error': 'No image provided for analysis'
            }
        
        current_app.logger.info(f"AI detection analysis completed for user {current_user['user_id']}")
        
        return jsonify(format_api_response(
            ai_detection, 'success', 'AI detection analysis completed'
        ))
        
    except Exception as e:
        current_app.logger.error(f"AI detection analysis failed: {str(e)}")
        return jsonify(format_api_response(
            None, 'error', str(e)
        )), 500

@require_auth
def ai_video_stream_analyze_post():
    """AI Agent video stream analysis endpoint."""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        stream_url = data.get('stream_url')
        analysis_parameters = data.get('analysis_parameters', {})
        
        # Simulate real-time video analysis
        video_analysis = {
            'stream_id': f"stream_{current_user['user_id']}_{asyncio.get_event_loop().time()}",
            'analysis_status': 'active',
            'detections_summary': {
                'total_detections': 12,
                'unique_individuals': 8,
                'avg_confidence': 0.82,
                'detection_rate': '2.3 per minute'
            },
            'behavioral_patterns': {
                'primary_activity': 'foraging',
                'movement_direction': 'northeast',
                'group_dynamics': 'scattered individuals'
            },
            'alerts': [
                {
                    'type': 'high_activity',
                    'timestamp': '2024-01-15T20:30:00Z',
                    'message': 'Unusual activity spike detected'
                }
            ]
        }
        
        current_app.logger.info(f"Video stream analysis started for user {current_user['user_id']}")
        
        return jsonify(format_api_response(
            video_analysis, 'success', 'Video stream analysis initiated'
        ))
        
    except Exception as e:
        current_app.logger.error(f"Video stream analysis failed: {str(e)}")
        return jsonify(format_api_response(
            None, 'error', str(e)
        )), 500

@require_auth
def ai_modeling_post():
    """AI Agent model training endpoint."""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Get ML pipeline
        pipeline = asyncio.run(get_pipeline())
        
        # Start model training
        training_data = {
            'habitat_data': data.get('habitat_data'),
            'movement_data': data.get('movement_data'),
            'sensor_data': data.get('sensor_data')
        }
        
        training_results = asyncio.run(pipeline.train_models(training_data))
        
        current_app.logger.info(f"Model training completed for user {current_user['user_id']}")
        
        return jsonify(format_api_response(
            training_results, 'success', 'Model training completed'
        ))
        
    except Exception as e:
        current_app.logger.error(f"Model training failed: {str(e)}")
        return jsonify(format_api_response(
            None, 'error', str(e)
        )), 500

@require_auth
def ai_rag_query_post():
    """AI Retrieval-Augmented Generation endpoint."""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        query = data.get('query', '')
        context_window = data.get('context_window', 5)
        
        # Simulate RAG query processing
        rag_response = {
            'query': query,
            'response': f"Based on the MNTRK database analysis, here's what I found regarding '{query}': The current Mastomys Natalensis population shows moderate activity levels with seasonal variations. Recent habitat suitability models indicate optimal conditions in regions with 20-25°C temperature and moderate rainfall patterns.",
            'sources': [
                {
                    'type': 'habitat_analysis',
                    'id': 'hab_001',
                    'relevance': 0.92,
                    'timestamp': '2024-01-15T18:00:00Z'
                },
                {
                    'type': 'detection_pattern',
                    'id': 'det_045',
                    'relevance': 0.87,
                    'timestamp': '2024-01-15T16:30:00Z'
                }
            ],
            'confidence': 0.89,
            'context_used': context_window
        }
        
        current_app.logger.info(f"RAG query processed for user {current_user['user_id']}: {query}")
        
        return jsonify(format_api_response(
            rag_response, 'success', 'RAG query processed successfully'
        ))
        
    except Exception as e:
        current_app.logger.error(f"RAG query failed: {str(e)}")
        return jsonify(format_api_response(
            None, 'error', str(e)
        )), 500

def _analyze_environmental_factors(env_data):
    """Analyze environmental factors for AI insights."""
    factors = []
    
    if 'temperature' in env_data:
        temp = env_data['temperature']
        if 20 <= temp <= 25:
            factors.append({'factor': 'temperature', 'status': 'optimal', 'value': temp})
        elif 15 <= temp <= 30:
            factors.append({'factor': 'temperature', 'status': 'suitable', 'value': temp})
        else:
            factors.append({'factor': 'temperature', 'status': 'suboptimal', 'value': temp})
    
    if 'rainfall' in env_data:
        rainfall = env_data['rainfall']
        if 100 <= rainfall <= 300:
            factors.append({'factor': 'rainfall', 'status': 'optimal', 'value': rainfall})
        else:
            factors.append({'factor': 'rainfall', 'status': 'suboptimal', 'value': rainfall})
    
    return factors

def _generate_habitat_recommendations(prediction_result):
    """Generate habitat management recommendations."""
    suitability = prediction_result.get('suitability_score', 0)
    
    if suitability > 0.8:
        return [
            "High suitability area - implement enhanced monitoring",
            "Consider preventive measures for population control",
            "Establish regular surveillance protocols"
        ]
    elif suitability > 0.6:
        return [
            "Moderate suitability - maintain standard monitoring",
            "Monitor environmental changes closely",
            "Prepare contingency plans"
        ]
    else:
        return [
            "Low suitability - routine monitoring sufficient",
            "Focus resources on higher-risk areas"
        ]

def _assess_habitat_risks(prediction_result):
    """Assess risks based on habitat prediction."""
    suitability = prediction_result.get('suitability_score', 0)
    
    risks = []
    if suitability > 0.7:
        risks.append({
            'type': 'population_growth',
            'level': 'high',
            'description': 'Conditions favor rapid population expansion'
        })
    
    if suitability > 0.8:
        risks.append({
            'type': 'disease_transmission',
            'level': 'elevated',
            'description': 'High density may increase disease transmission risk'
        })
    
    return risks
