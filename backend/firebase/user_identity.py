from firebase.client import get_firestore, get_auth
from firebase_admin import firestore, auth
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Configure logging
logger = logging.getLogger(__name__)

# Collection name
COLLECTION = 'users'

def create_user(email: str, password: str, display_name: str = None, role: str = 'user') -> Dict[str, Any]:
    """Create a new user in Firebase Authentication and Firestore."""
    try:
        # Create user in Firebase Auth
        auth_client = get_auth()
        user = auth_client.create_user(
            email=email,
            password=password,
            display_name=display_name,
            disabled=False
        )
        
        # Create user document in Firestore
        db = get_firestore()
        user_data = {
            'email': email,
            'display_name': display_name,
            'role': role,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'last_login': None
        }
        
        db.collection(COLLECTION).document(user.uid).set(user_data)
        
        logger.info(f"Created user with ID: {user.uid}")
        return {
            'uid': user.uid,
            'email': email,
            'display_name': display_name,
            'role': role
        }
    
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    try:
        # Get user from Firebase Auth
        auth_client = get_auth()
        auth_user = auth_client.get_user(user_id)
        
        # Get user document from Firestore
        db = get_firestore()
        doc = db.collection(COLLECTION).document(user_id).get()
        
        if not doc.exists:
            logger.warning(f"User document not found: {user_id}")
            return {
                'uid': auth_user.uid,
                'email': auth_user.email,
                'display_name': auth_user.display_name,
                'disabled': auth_user.disabled
            }
        
        data = doc.to_dict()
        data['uid'] = auth_user.uid
        data['email'] = auth_user.email
        data['display_name'] = auth_user.display_name
        data['disabled'] = auth_user.disabled
        
        return data
    
    except auth.UserNotFoundError:
        logger.warning(f"User not found: {user_id}")
        return None
    
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise

def update_user(user_id: str, data: Dict[str, Any]) -> bool:
    """Update a user."""
    try:
        # Update user in Firebase Auth
        auth_client = get_auth()
        auth_params = {}
        
        if 'email' in data:
            auth_params['email'] = data['email']
        
        if 'display_name' in data:
            auth_params['display_name'] = data['display_name']
        
        if 'password' in data:
            auth_params['password'] = data['password']
        
        if 'disabled' in data:
            auth_params['disabled'] = data['disabled']
        
        if auth_params:
            auth_client.update_user(user_id, **auth_params)
        
        # Update user document in Firestore
        db = get_firestore()
        firestore_data = {k: v for k, v in data.items() if k not in ['password']}
        
        if firestore_data:
            firestore_data['updated_at'] = firestore.SERVER_TIMESTAMP
            db.collection(COLLECTION).document(user_id).update(firestore_data)
        
        logger.info(f"Updated user: {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise

def delete_user(user_id: str) -> bool:
    """Delete a user."""
    try:
        # Delete user from Firebase Auth
        auth_client = get_auth()
        auth_client.delete_user(user_id)
        
        # Delete user document from Firestore
        db = get_firestore()
        db.collection(COLLECTION).document(user_id).delete()
        
        logger.info(f"Deleted user: {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise

def list_users(limit: int = 1000) -> List[Dict[str, Any]]:
    """List all users."""
    try:
        # List users from Firebase Auth
        auth_client = get_auth()
        page = auth_client.list_users()
        
        users = []
        for user in page.users:
            users.append({
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'disabled': user.disabled
            })
            
            if len(users) >= limit:
                break
        
        return users
    
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise

def update_user_last_login(user_id: str) -> bool:
    """Update user's last login timestamp."""
    try:
        db = get_firestore()
        db.collection(COLLECTION).document(user_id).update({
            'last_login': firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Updated last login for user: {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to update user last login: {e}")
        raise
