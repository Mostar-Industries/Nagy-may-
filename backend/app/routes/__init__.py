from flask import Blueprint

# Import blueprints from route modules
from .auth import auth_bp
from .agents import agents_bp
from .ai import ai_bp
from .omniverse import omniverse_bp

def register_routes(app):
    """Register application blueprints."""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(omniverse_bp, url_prefix='/api/omniverse')
