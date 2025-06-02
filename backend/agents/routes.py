# Agents blueprint: handles Mastomys tracking ingestion.
from flask import Blueprint, request, jsonify, current_app
from api.shared.database import get_db
from datetime import datetime
from firebase_admin import firestore # For firestore.SERVER_TIMESTAMP

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('/track', methods=['POST'])
def track_mastomys():
    data = request.get_json() or {}
    device_id = data.get('device_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    timestamp_str = data.get('timestamp')

    # Validate input fields
    missing = [k for k in ('device_id','latitude','longitude','timestamp') if not data.get(k)]
    if missing:
        return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 400
    
    try:
        # Validate ISO format for timestamp
        # The replace('Z', '+00:00') is good for robust parsing if 'Z' is present.
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format. Please use ISO 8601 (e.g., YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+00:00).'}), 400

    try:
        lat_float = float(latitude)
        lon_float = float(longitude)
    except ValueError:
        return jsonify({'error': 'Latitude and Longitude must be valid numbers.'}), 400

    sighting_data = {
        'device_id': device_id,
        'latitude': lat_float,
        'longitude': lon_float,
        'timestamp': timestamp_str, # Storing as ISO string as validated
        'created_at': firestore.SERVER_TIMESTAMP # Firestore server-side timestamp
    }

    try:
        db = get_db()
        doc_ref = db.collection('mastomys_sightings').document() # Auto-generate document ID
        doc_ref.set(sighting_data)
        
        # Return the data that was sent, plus the generated ID.
        # Note: 'created_at' will be a placeholder locally until written to Firestore.
        # If you need the actual server timestamp back, you'd have to re-fetch the document.
        response_data = sighting_data.copy()
        response_data['id'] = doc_ref.id
        # For 'created_at', you could return a string indicating it's a server timestamp
        # or omit it if the client doesn't immediately need its resolved value.
        response_data['created_at'] = "Pending server timestamp" 

        return jsonify(response_data), 201
    except Exception as e:
        current_app.logger.error(f"Error persisting sighting to Firestore: {e}")
        return jsonify({'error': f'Failed to record sighting: {str(e)}'}), 500
