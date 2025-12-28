"""
Flask application initialization for PlanSowGrow.
"""
import os
from flask import Flask
from extensions import db


def create_app(config_name=None):
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration name ('development', 'production', or None for default)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Create tables within app context
    with app.app_context():
        # Import models to ensure they're registered
        import models
    
    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
