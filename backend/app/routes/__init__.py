from flask import Blueprint

# Import blueprints from route modules
from .auth import auth_bp
from .detections import detections_bp 
# Import other blueprints as they are created
# from .agents import agents_bp
# from .omniverse import omniverse_bp
# from .ai import ai_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(detections_bp, url_prefix='/api/detections')
    # Register other blueprints
    # app.register_blueprint(agents_bp, url_prefix='/api/agents')
    # app.register_blueprint(omniverse_bp, url_prefix='/api/omniverse')
    # app.register_blueprint(ai_bp, url_prefix='/api/ai')
