import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your REAL Firebase configuration
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "mntrk-fcd2b",
    "private_key_id": "",  # Will be filled from service account
    "private_key": "",     # Will be filled from service account
    "client_email": "",    # Will be filled from service account
    "client_id": "",       # Will be filled from service account
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": ""  # Will be filled from service account
}

# Global Firebase instances
_firebase_app = None
_firestore_client = None
_storage_bucket = None

def initialize_firebase():
    """Initialize Firebase Admin SDK with REAL mntrk-fcd2b project."""
    global _firebase_app, _firestore_client, _storage_bucket
    
    if _firebase_app:
        logger.info("Firebase already initialized for mntrk-fcd2b")
        return
    
    try:
        # Get Firebase credentials from environment
        firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
        
        if not firebase_creds:
            raise ValueError("FIREBASE_CREDENTIALS environment variable required")
        
        # Load credentials
        if os.path.exists(firebase_creds):
            cred = credentials.Certificate(firebase_creds)
        else:
            # Parse JSON string
            cred_dict = json.loads(firebase_creds)
            cred = credentials.Certificate(cred_dict)
        
        # Initialize with REAL project
        _firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': 'mntrk-fcd2b',
            'storageBucket': 'mntrk-fcd2b.firebasestorage.app'
        })
        
        # Initialize services
        _firestore_client = firestore.client()
        _storage_bucket = storage.bucket()
        
        logger.info("✅ Firebase initialized successfully for mntrk-fcd2b")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Firebase: {e}")
        raise

def get_firestore():
    """Get Firestore client for mntrk-fcd2b project."""
    if not _firestore_client:
        initialize_firebase()
    return _firestore_client

def get_storage():
    """Get Storage bucket for mntrk-fcd2b project."""
    if not _storage_bucket:
        initialize_firebase()
    return _storage_bucket

def get_auth():
    """Get Firebase Auth for mntrk-fcd2b project."""
    if not _firebase_app:
        initialize_firebase()
    return auth
