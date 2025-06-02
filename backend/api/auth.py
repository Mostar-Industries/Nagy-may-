import os
import jwt
import functools
from datetime import datetime, timedelta
from flask import request, jsonify, current_app, g
from firebase_admin import auth as firebase_auth
from shared.database import get_db_sync

class AuthError(Exception):
    """Custom authentication error."""
    def __init__(self, message, status_code=401):
        self.message = message
        self.status_code = status_code

def init_auth(app):
    """Initialize authentication for the Flask app."""
    app.config.setdefault('JWT_SECRET_KEY', os.getenv('JWT_SECRET_KEY', 'dev-secret-key'))
    app.config.setdefault('JWT_EXPIRATION_HOURS', 24)
    app.logger.info("Authentication system initialized")

def generate_jwt_token(user_id: str, email: str) -> str:
    """Generate JWT token for authenticated user."""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")

def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token."""
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise AuthError(f"Firebase token verification failed: {str(e)}")

def require_auth(f):
    """Decorator to require authentication for API endpoints."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            # Support both "Bearer <token>" and "<token>" formats
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
            
            # Try Firebase token first, then JWT
            try:
                user_data = verify_firebase_token(token)
                g.current_user = {
                    'user_id': user_data['uid'],
                    'email': user_data.get('email'),
                    'auth_type': 'firebase'
                }
            except AuthError:
                # Fallback to JWT
                user_data = verify_jwt_token(token)
                g.current_user = {
                    'user_id': user_data['user_id'],
                    'email': user_data['email'],
                    'auth_type': 'jwt'
                }
            
            return f(*args, **kwargs)
            
        except AuthError as e:
            return jsonify({'error': e.message}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def require_api_key(f):
    """Decorator to require API key for service-to-service communication."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key against environment or database
        valid_api_keys = os.getenv('VALID_API_KEYS', '').split(',')
        
        if api_key not in valid_api_keys:
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.api_authenticated = True
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get current authenticated user from request context."""
    return getattr(g, 'current_user', None)

# Authentication endpoints
def login():
    """Login endpoint for JWT authentication."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # In a real implementation, verify credentials against your user database
    # For now, we'll use a simple check
    if email == 'admin@mntrk.com' and password == 'admin123':
        token = generate_jwt_token('admin-user-id', email)
        return jsonify({
            'token': token,
            'user': {
                'id': 'admin-user-id',
                'email': email,
                'role': 'admin'
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

def refresh_token():
    """Refresh JWT token."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    new_token = generate_jwt_token(user['user_id'], user['email'])
    return jsonify({'token': new_token})
