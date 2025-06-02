#!/usr/bin/env python3
"""
REAL Firebase connection test for mntrk-fcd2b project
"""
import os
import sys
from config.firebase_config import initialize_firebase, get_firestore, get_storage

def test_firestore_connection():
    """Test REAL Firestore connection."""
    print("🔥 Testing Firestore connection to mntrk-fcd2b...")
    
    try:
        db = get_firestore()
        
        # Write test document
        test_doc = {
            'status': 'sovereign_grid_online',
            'project_id': 'mntrk-fcd2b',
            'timestamp': firestore.SERVER_TIMESTAMP,
            'test_type': 'connection_verification'
        }
        
        doc_ref = db.collection('system_tests').add(test_doc)
        print(f"✅ Firestore write successful: {doc_ref[1].id}")
        
        # Read test document
        docs = db.collection('system_tests').limit(1).stream()
        for doc in docs:
            print(f"✅ Firestore read successful: {doc.to_dict()}")
            break
        
        return True
        
    except Exception as e:
        print(f"❌ Firestore test failed: {e}")
        return False

def test_storage_connection():
    """Test REAL Firebase Storage connection."""
    print("📁 Testing Firebase Storage connection...")
    
    try:
        bucket = get_storage()
        
        # Test file upload
        test_content = b"MNTRK Sovereign Grid Test File"
        blob = bucket.blob('tests/connection_test.txt')
        blob.upload_from_string(test_content)
        
        print(f"✅ Storage upload successful: gs://mntrk-fcd2b.firebasestorage.app/tests/connection_test.txt")
        
        # Test file download
        downloaded = blob.download_as_bytes()
        if downloaded == test_content:
            print("✅ Storage download successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return False

def main():
    """Run all Firebase tests."""
    print("🛡️ MNTRK Sovereign Grid - Firebase Connection Test")
    print("=" * 50)
    
    # Check environment
    if not os.environ.get('FIREBASE_CREDENTIALS'):
        print("❌ FIREBASE_CREDENTIALS environment variable not set")
        print("Set it with: export FIREBASE_CREDENTIALS=/path/to/firebase-credentials.json")
        sys.exit(1)
    
    # Initialize Firebase
    try:
        initialize_firebase()
        print("✅ Firebase initialization successful")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        sys.exit(1)
    
    # Run tests
    firestore_ok = test_firestore_connection()
    storage_ok = test_storage_connection()
    
    if firestore_ok and storage_ok:
        print("\n🔥 ALL FIREBASE TESTS PASSED - SOVEREIGN GRID READY")
        return True
    else:
        print("\n❌ SOME TESTS FAILED - CHECK CONFIGURATION")
        return False

if __name__ == "__main__":
    main()
