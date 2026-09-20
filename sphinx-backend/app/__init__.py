from flask import Flask
from config import config_by_name
from app.extensions import db, ma, jwt, cors
from app.utils.exceptions import register_error_handlers
from app.api import v1_blueprints


def create_app(config_name: str = 'development') -> Flask:
    """
    Application Factory for Project SPHINX Backend.
    Sets up configuration, extensions, RBAC, JWT, CORS, error handling, and blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register custom error handlers
    register_error_handlers(app)

    # Register API Blueprints
    for bp in v1_blueprints:
        app.register_blueprint(bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'system': 'SPHINX Secure Patient Healthcare Information Platform',
            'version': '1.0.0'
        }, 200

    return app
