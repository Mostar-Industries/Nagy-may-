from flask import Blueprint, request, jsonify, current_app
import asyncio
from DeepSeekIntegration import generate_text # Assuming DeepSeekIntegration.py is in root or python path
from api.auth import check_deepseek_auth

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/deepseek/generate', methods=['POST'])
def generate_deepseek_text_route(): # Renamed to avoid conflict if generate_text is imported directly
    auth_error_response = check_deepseek_auth()
    if auth_error_response: # check_deepseek_auth returns a response on error, None on success
        return auth_error_response
    
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error':'bad_request', 'message':'Request body must be JSON.'}), 400
        
    prompt = json_data.get('prompt')
    if not prompt:
        return jsonify({'error':'bad_request', 'message':'"prompt" is required in the JSON body.'}), 400
    
    # Use model from request, or app config default, or hardcoded default from DeepSeekIntegration
    model_to_use = json_data.get('model') # Pass None if not provided, DeepSeekIntegration will use default
    
    try:
        # Ensure temperature and max_tokens are valid types if provided
        temperature = float(json_data.get('temperature', 0.7))
        max_tokens = int(json_data.get('max_tokens', 256))
        if not (0.0 <= temperature <= 2.0): # Typical range for temperature
            return jsonify({'error':'bad_request', 'message':'"temperature" must be between 0.0 and 2.0.'}), 400
        if not (1 <= max_tokens <= 8192): # Typical range for max_tokens
             return jsonify({'error':'bad_request', 'message':'"max_tokens" must be between 1 and 8192.'}), 400
    except (ValueError, TypeError):
        return jsonify({'error':'bad_request', 'message':'"temperature" must be a float and "max_tokens" must be an integer.'}), 400

    try:
        # Flask is synchronous. To run asyncio code, you typically need to manage the event loop.
        # asyncio.run() creates a new event loop or uses the current one if available.
        # This can sometimes cause issues if an event loop is already running (e.g. in some test runners or WSGI servers).
        # For simple cases in development, it might work. For production, consider Quart or an async task queue.
        generated_text_result = asyncio.run(
            generate_text(
                prompt=prompt,
                model=model_to_use,
                temperature=temperature,
                max_tokens=max_tokens
            )
        )
        return jsonify({'generated_text': generated_text_result}), 200
    except RuntimeError as e: # Catch specific RuntimeError from generate_text
        current_app.logger.error(f"Service error during DeepSeek generation: {e}")
        # Avoid exposing internal error details directly from e unless it's a controlled message
        return jsonify({'error':'service_unavailable', 'message':'The AI generation service encountered an error.'}), 503
    except Exception as e: # Catch any other unexpected errors
        current_app.logger.exception(f"Unexpected error during DeepSeek text generation: {e}")
        return jsonify({'error':'internal_server_error', 'message':'An unexpected error occurred.'}), 500
