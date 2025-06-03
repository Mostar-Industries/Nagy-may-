from flask import Blueprint, request, jsonify
from ..models.user import User
from ..extensions import db
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
        
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password: # Email can be optional for registration depending on requirements
        return jsonify({"msg": "Missing username or password"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 409
    
    if email and User.query.filter_by(email=email).first(): # Check email if provided and unique
        return jsonify({"msg": "Email already exists"}), 409

    new_user = User(username=username, email=email) # Store email if provided
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id) # Good practice to issue refresh tokens
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    
    return jsonify({"msg": "Bad username or password"}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) # Requires a valid refresh token
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_access_token), 200

@auth_bp.route('/protected_example', methods=['GET']) # Renamed from '/protected' for clarity
@jwt_required() # Requires a valid access token
def protected_example():
    current_user_id = get_jwt_identity()
    # Use db.session.get for SQLAlchemy 2.0 style, or User.query.get for older Flask-SQLAlchemy
    user = db.session.get(User, current_user_id) 
    if not user:
         return jsonify({"msg": "User not found"}), 404
    return jsonify(logged_in_as=user.username, user_id=user.id), 200
