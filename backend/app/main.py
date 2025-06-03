import os
from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, jwt
from .routes.auth import auth_bp
from .routes.agents import agents_bp
from .routes.ai import ai_bp
from .routes.omniverse import omniverse_bp

def create_app():
    app = Flask(__name__)
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.getenv('DATABASE_URL', 'sqlite:///:memory:'))
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(omniverse_bp, url_prefix='/api/omniverse')

    with app.app_context():
        db.create_all()

    return app

application = create_app()
