from flask import Blueprint, request, jsonify, current_app
from shared.database import get_db # Assuming shared/database.py is in the project root
from datetime import datetime, timezone, ISOFORMAT_SUFFIXES
from firebase_admin import firestore # For firestore.SERVER_TIMESTAMP

agents_bp = Blueprint('agents', __name__)

def parse_iso_timestamp(timestamp_str):
    """Helper to parse ISO 8601 timestamps, handling 'Z' and timezone offsets."""
    for suffix, parse_func in ISOFORMAT_SUFFIXES.items():
        if timestamp_str.endswith(suffix):
            # Remove suffix and parse
            ts_part = timestamp_str[:-len(suffix)] if suffix else timestamp_str
            dt = datetime.fromisoformat(ts_part)
            # Add timezone info based on suffix
            if suffix == 'Z':
                return dt.replace(tzinfo=timezone.utc)
            elif suffix: # For +HH:MM or -HH:MM
                # fromisoformat should handle this directly if suffix is part of the string
                return datetime.fromisoformat(timestamp_str) 
            return dt # Should have tzinfo if parsed with offset
    # If no known suffix, try direct parsing (might be naive or have offset)
    dt = datetime.fromisoformat(timestamp_str)
    if dt.tzinfo is None: # If naive, assume UTC or raise error based on policy
        return dt.replace(tzinfo=timezone.utc) # Defaulting to UTC for naive timestamps
    return dt


@agents_bp.route('/track', methods=['POST'])
def track_mastomys_sighting(): # Renamed for clarity
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error':'bad_request', 'message':'Request body must be JSON.'}), 400

    required_fields = ['device_id', 'latitude', 'longitude', 'timestamp']
    missing_fields = [field for field in required_fields if field not in json_data or json_data[field] is None]
    if missing_fields:
        return jsonify({'error':'bad_request', 'message':f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        # Validate data types
        device_id = str(json_data['device_id'])
        latitude = float(json_data['latitude'])
        longitude = float(json_data['longitude'])
        # Validate timestamp format and convert to a consistent representation (e.g., UTC ISO string)
        parsed_timestamp = parse_iso_timestamp(str(json_data['timestamp']))
        timestamp_iso_utc = parsed_timestamp.astimezone(timezone.utc).isoformat()

        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180.")

    except (ValueError, TypeError) as e:
        return jsonify({'error':'bad_request', 'message':f"Invalid data type or format: {e}"}), 400
    
    sighting_payload = {
        'device_id': device_id,
        'latitude': latitude,
        'longitude': longitude,
        'timestamp': timestamp_iso_utc, # Store consistently in UTC ISO format
        'created_at': firestore.SERVER_TIMESTAMP # Firestore server-side timestamp for record creation
    }
    # Optionally, include other non-required fields from json_data if they exist
    # for key, value in json_data.items():
    #    if key not in required_fields and key not in sighting_payload:
    #        sighting_payload[key] = value

    try:
        firestore_db = get_db()
        # Auto-generate document ID by calling .document() without an ID
        doc_reference = firestore_db.collection('mastomys_sightings').document()
        doc_reference.set(sighting_payload)
        
        # Prepare response data
        response_data = sighting_payload.copy()
        response_data['id'] = doc_reference.id
        # Note: 'created_at' will be a server timestamp placeholder in the immediate response.
        # The actual timestamp is resolved by Firestore servers.
        response_data['created_at'] = "Pending server-side timestamp" 

        return jsonify(response_data), 201 # 201 Created
    except Exception as e:
        current_app.logger.exception(f"Error persisting Mastomys sighting to Firestore: {e}")
        return jsonify({'error':'internal_server_error', 'message':'Failed to record sighting due to a server error.'}), 500
