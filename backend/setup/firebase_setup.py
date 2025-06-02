#!/usr/bin/env python3
"""
Real Firebase setup and connection test script
Run this after creating your Firebase project and downloading credentials
"""

import os
import sys
import json
import firebase_admin
from firebase_admin import credentials, firestore

def setup_firebase():
    """Setup and test Firebase connection"""
    
    # Check for credentials file
    creds_path = os.environ.get('FIREBASE_CREDENTIALS')
    if not creds_path:
        print("❌ FIREBASE_CREDENTIALS environment variable not set")
        print("Set it with: export FIREBASE_CREDENTIALS=/path/to/firebase-credentials.json")
        return False
    
    if not os.path.exists(creds_path):
        print(f"❌ Firebase credentials file not found: {creds_path}")
        return False
    
    try:
        # Initialize Firebase
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
        
        # Test Firestore connection
        db = firestore.client()
        
        # Write test document
        test_ref = db.collection('system_test').document('connection_test')
        test_ref.set({
            'status': 'firebase_operational',
            'timestamp': firestore.SERVER_TIMESTAMP,
            'test_type': 'connection_verification'
        })
        
        # Read it back
        doc = test_ref.get()
        if doc.exists:
            print("✅ Firebase Firestore connection successful")
            print(f"✅ Test document created: {doc.to_dict()}")
            
            # Clean up test document
            test_ref.delete()
            print("✅ Test document cleaned up")
            return True
        else:
            print("❌ Failed to read test document")
            return False
            
    except Exception as e:
        print(f"❌ Firebase setup failed: {e}")
        return False

if __name__ == "__main__":
    print("🔥 FIREBASE SETUP AND CONNECTION TEST")
    print("=" * 50)
    
    if setup_firebase():
        print("✅ Firebase is ready for MNTRK deployment")
    else:
        print("❌ Firebase setup failed - fix issues before proceeding")
        sys.exit(1)
