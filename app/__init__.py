"""
Flask application factory for PlanSowGrow.

This module implements the application factory pattern for creating
and configuring the Flask application instance.
"""
import os
import logging
from flask import Flask
from config import config
from app.models.base import db


def create_app(config_name=None):
    """
    Application factory function.
    
    Creates and configures a Flask application instance using the
    application factory pattern. This allows for multiple instances
    with different configurations (development, testing, production).
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
                          Defaults to FLASK_ENV environment variable or 'development'
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register shell context
    register_shell_context(app)
    
    # Create database tables (in development/testing)
    with app.app_context():
        if config_name in ['development', 'testing']:
            db.create_all()
    
    app.logger.info(f'PlanSowGrow application started in {config_name} mode')
    
    return app


def register_blueprints(app):
    """
    Register all Flask blueprints with the application.
    
    Args:
        app (Flask): Flask application instance
    """
    from app.routes import main_bp, garden_bp, season_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(garden_bp)
    app.register_blueprint(season_bp)


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.
    
    Args:
        app (Flask): Flask application instance
    """
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        db.session.rollback()
        app.logger.error(f'Internal server error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        return render_template('errors/403.html'), 403


def register_shell_context(app):
    """
    Register shell context for Flask shell.
    
    Makes commonly used objects available in Flask shell automatically.
    
    Args:
        app (Flask): Flask application instance
    """
    @app.shell_context_processor
    def make_shell_context():
        """Add models and services to shell context."""
        from app.models import db, BaseModel
        from app.models.garden import Garden
        from app.models.bed import Bed
        from app.models.season import Season
        from app.services import GardenService, BedService, SeasonService
        
        return {
            'db': db,
            'BaseModel': BaseModel,
            'Garden': Garden,
            'Bed': Bed,
            'Season': Season,
            'GardenService': GardenService,
            'BedService': BedService,
            'SeasonService': SeasonService
        }


def configure_logging(app):
    """
    Configure application logging.
    
    Args:
        app (Flask): Flask application instance
    """
    if not app.debug and not app.testing:
        # Production logging setup
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/plansowgrow.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('PlanSowGrow startup')
