import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import storage
from firebase_admin import auth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
_firebase_app = None
_firestore_client = None
_storage_client = None

def initialize_firebase():
    """Initialize Firebase Admin SDK and clients."""
    global _firebase_app, _firestore_client, _storage_client
    
    if _firebase_app:
        logger.info("Firebase already initialized")
        return
    
    try:
        # Get Firebase credentials from environment variable
        firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
        
        if not firebase_creds:
            raise ValueError("FIREBASE_CREDENTIALS environment variable is required")
        
        # Check if it's a file path or JSON string
        if os.path.exists(firebase_creds):
            cred = credentials.Certificate(firebase_creds)
        else:
            # Try to parse as JSON string
            try:
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError:
                raise ValueError("FIREBASE_CREDENTIALS must be a valid JSON string or file path")
        
        # Initialize Firebase Admin SDK
        _firebase_app = firebase_admin.initialize_app(cred, {
            'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'mntrk-sovereign.appspot.com')
        })
        
        # Initialize Firestore client
        _firestore_client = firestore.client()
        
        # Initialize Storage client
        _storage_client = storage.bucket()
        
        logger.info("Firebase initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise

def get_firestore():
    """Get the Firestore client instance."""
    global _firestore_client
    
    if not _firestore_client:
        initialize_firebase()
    
    return _firestore_client

def get_storage():
    """Get the Firebase Storage bucket instance."""
    global _storage_client
    
    if not _storage_client:
        initialize_firebase()
    
    return _storage_client

def get_auth():
    """Get the Firebase Auth instance."""
    if not firebase_admin._apps:
        initialize_firebase()
    
    return auth
