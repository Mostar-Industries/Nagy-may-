import pytest
import json
from app import create_app # Your Flask app factory
from datetime import datetime, timezone

# Minimal mock for Firestore client and its methods
class MockFirestoreDocument:
    def __init__(self, doc_id='test_doc_id_abc'): # Default ID
        self.id = doc_id
    def set(self, data):
        # In a real mock, you might store 'data' for assertions
        pass 

class MockFirestoreCollection:
    def document(self, doc_id=None): # Allow doc_id to be passed or auto-generated
        return MockFirestoreDocument(doc_id if doc_id else 'auto_generated_test_id')

class MockFirestoreClient:
    def collection(self, name):
        # You could assert 'name' == 'mastomys_sightings' if needed
        return MockFirestoreCollection()

@pytest.fixture(scope="function") # Changed to function scope for cleaner test isolation
def client(monkeypatch, tmp_path):
    # Mock get_db to return our mock Firestore client
    monkeypatch.setattr('shared.database.get_db', lambda: MockFirestoreClient())
    
    # If init_db itself tries to load credentials and fails, mock it too:
    # This prevents actual Firebase SDK initialization during tests.
    monkeypatch.setattr('shared.database.init_db', lambda app_instance: None)
    
    # Ensure DEEPSEEK_API_KEY is set for app creation if auth checks it during init
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'test_deepseek_key_for_pytest')
    # Mock FIREBASE_CREDENTIALS to avoid issues if config.py checks it, even if init_db is mocked
    monkeypatch.setenv('FIREBASE_CREDENTIALS', '/mock/path/to/creds.json')


    app_instance = create_app() # Create app instance
    app_instance.config['TESTING'] = True # Enable Flask's testing mode
    
    with app_instance.test_client() as test_client:
        yield test_client


def test_track_sighting_success(client):
    """Test successful tracking of a Mastomys sighting."""
    valid_payload = {
        'device_id':'test_device_001',
        'latitude':10.12345,
        'longitude':-3.45678,
        'timestamp':'2025-05-30T12:00:00Z' # UTC timestamp
    }
    response = client.post('/api/agents/track', json=valid_payload)
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['id'] is not None 
    assert data['device_id'] == valid_payload['device_id']
    assert data['latitude'] == valid_payload['latitude']
    assert data['longitude'] == valid_payload['longitude']
    # Timestamp in response should be the same UTC ISO format as sent, or as processed
    parsed_sent_ts = datetime.fromisoformat(valid_payload['timestamp'].replace('Z', '+00:00'))
    assert data['timestamp'] == parsed_sent_ts.astimezone(timezone.utc).isoformat()
    assert data['created_at'] == "Pending server-side timestamp"

def test_track_sighting_missing_fields(client):
    """Test tracking with missing required fields."""
    invalid_payload = {
        'device_id':'test_device_002',
        'latitude':11.0
        # longitude and timestamp are missing
    }
    response = client.post('/api/agents/track', json=invalid_payload)
    assert response.status_code == 400
    data = response.get_json()
    assert 'Missing required fields' in data['message']
    assert 'longitude' in data['message']
    assert 'timestamp' in data['message']

def test_track_sighting_invalid_timestamp_format(client):
    """Test tracking with an invalid timestamp format."""
    payload_invalid_ts = {
        'device_id':'d_invalid_ts',
        'latitude':1.0,
        'longitude':2.0,
        'timestamp':'30-05-2025 12:00:00' # Not ISO 8601
    }
    response = client.post('/api/agents/track', json=payload_invalid_ts)
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid data type or format' in data['message'] # Updated to match new error message

def test_track_sighting_invalid_latitude_type(client):
    """Test tracking with invalid latitude type."""
    payload_invalid_lat = {
        'device_id':'d_invalid_lat',
        'latitude': "not-a-float", # Invalid type
        'longitude': 2.0,
        'timestamp':'2025-05-30T12:00:00Z'
    }
    response = client.post('/api/agents/track', json=payload_invalid_lat)
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid data type or format' in data['message']

def test_track_sighting_latitude_out_of_range(client):
    """Test tracking with latitude out of valid range."""
    payload_lat_oor = {
        'device_id':'d_lat_oor',
        'latitude': 90.001, # Out of range
        'longitude': 2.0,
        'timestamp':'2025-05-30T12:00:00Z'
    }
    response = client.post('/api/agents/track', json=payload_lat_oor)
    assert response.status_code == 400
    data = response.get_json()
    assert 'Latitude must be between -90 and 90' in data['message']

def test_track_sighting_no_json_body(client):
    """Test tracking endpoint when no JSON body is provided."""
    response = client.post('/api/agents/track', data="not json")
    assert response.status_code == 400 # Flask/Connexion might return 400 or 415
    data = response.get_json()
    assert 'Request body must be JSON' in data['message']
